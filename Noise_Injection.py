import os
import pathlib

# Output
OUTPUT_DIR = pathlib.Path(r"C:\Users\Lucas Chen\OneDrive\Science Project 2026\Digital Analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'figure.facecolor': '#0f0f1a', 'axes.facecolor': '#1a1a2e',
    'axes.edgecolor':   '#444466', 'axes.grid': True,
    'grid.color':       '#2a2a4a', 'grid.linewidth': 0.6,
    'text.color':       '#ccccdd', 'axes.labelcolor': '#ccccdd',
    'xtick.color':      '#ccccdd', 'ytick.color':     '#ccccdd',
    'legend.facecolor': '#1a1a2e','legend.edgecolor': '#444466',
    'axes.titlesize':   11,        'axes.labelsize':   10,
    'legend.fontsize':  9,
})

# Data
N = 20
m = np.arange(N)

A   = [2*240.3411499, 2*323.6750783, 2*19.62380682, 2*49.5953873,
       2*24.82707025, 2*3.716276805, 2*13.57305442, 2*24.24657408,
       2*57.89750227, 33.87470998]
phi = [-1.168084937,  1.279642856,  2.892337571, -1.593010231,
       -1.561450804,  0.301711856, -2.921065905,  1.31937808,
        0.245177689,  1.05072e-13]

x_clean = np.sum([A[k] * np.cos(2*np.pi*(k+1)*m/N + phi[k])
                  for k in range(N//2)], axis=0)

# Lab SNR Calculation
SIGNAL_VPP = 1.5    # V after 20dB attenuation
NOISE_VPP  = 10.0   # V from adder box
ATT_DB     = 20.0   # dB of attenuation applied

signal_vpeak = SIGNAL_VPP / 2
noise_vpeak  = NOISE_VPP  / 2

# RMS values
signal_vrms  = signal_vpeak / np.sqrt(2)           # sinusoidal crest factor
noise_vrms   = NOISE_VPP    / 6.0                  # gaussian crest factor about 6

snr_db       = 20 * np.log10(signal_vrms / noise_vrms)
voltage_ratio = noise_vrms / signal_vrms
power_ratio   = voltage_ratio**2

# Scale  data array to lab v range (map to ±0.75V = 1.5VPP)
data_scale   = signal_vpeak / np.max(np.abs(x_clean))
x_volts      = x_clean * data_scale           # in volts

# Inject calibrated noise
np.random.seed(42)
x_rms        = np.sqrt(np.mean(x_volts**2))
noise_sigma  = 100 * x_rms                    # 100× signal RMS means SNR ≈ −40 dB

# 20-point noise for SNR calculation, normalized
noise_v      = np.random.normal(0, 1, N)
noise_v     -= noise_v.mean()
noise_v     /= noise_v.std()
noise_v     *= noise_sigma
x_noisy_v    = x_volts + noise_v

achieved_snr = 20 * np.log10(
    np.sqrt(np.mean(x_volts**2)) /
    np.sqrt(np.mean((x_noisy_v - x_volts)**2))
)

# Dense oversampled arrays for plotting
OVERSAMPLE   = 10                              # 10× finer than DFT grid = 200 pts/period
N_dense      = N * OVERSAMPLE
m_dense      = np.linspace(0, N - 1, N_dense)
x_dense_volts = np.sum([A[k] * np.cos(2*np.pi*(k+1)*m_dense/N + phi[k])
                         for k in range(N//2)], axis=0) * data_scale
noise_dense   = np.random.normal(0, noise_sigma, N_dense)   # raw — natural variation
x_noisy_dense = x_dense_volts + noise_dense

# Printed Results
print("=" * 62)
print("  PROGRAM 2 — CALIBRATED NOISE INJECTION")
print("=" * 62)

print(f"\n  ── Lab Voltage Parameters ──────────────────────────────")
print(f"    Signal amplitude:        {SIGNAL_VPP} VPP ({signal_vpeak:.4f} Vpeak)")
print(f"    Signal RMS:              {signal_vrms:.4f} Vrms  [Vpeak/√2]")
print(f"    Noise amplitude:         {NOISE_VPP} VPP  ({noise_vpeak:.2f} Vpeak)")
print(f"    Noise RMS (σ):           {noise_vrms:.4f} Vrms  [VPP/6, gaussian]")

print(f"\n  ── SNR Calculation ─────────────────────────────────────")
print(f"    SNR = 20·log₁₀(Vsig_rms / Vnoise_rms)")
print(f"        = 20·log₁₀({signal_vrms:.4f} / {noise_vrms:.4f})")
print(f"        = {snr_db:.1f} dB")
print(f"    Noise is {voltage_ratio:.1f}× signal in voltage")
print(f"    Noise is {power_ratio:.1f}× signal in power")

print(f"\n  ── What 20 dB Attenuation Means ────────────────────────")
print(f"    20 dB = 10× voltage reduction")
print(f"    If pre-attenuation signal was ~{SIGNAL_VPP*10:.0f} VPP")
print(f"    → Attenuated to {SIGNAL_VPP} VPP")
print(f"    The 20 dB attenuator deliberately buried the signal")
print(f"    to simulate the extremely weak X-ray photon flux")
print(f"    received by spacecraft detectors (e.g. NICER: 1900 cm²,")
print(f"    NinjaSat: 16 cm² per module)")

print(f"\n  ── Digitally Injected Noise (100× signal RMS) ──────────")
print(f"    Noise sigma used:        {noise_sigma:.4f} V  (= 100 × signal RMS)")
print(f"    Achieved SNR:            {achieved_snr:.1f} dB  (target: −40 dB)")
print(f"    Noisy signal range:      [{np.min(x_noisy_v):.3f}, {np.max(x_noisy_v):.3f}] V")
print(f"    Clean signal range:      [{np.min(x_volts):.3f}, {np.max(x_volts):.3f}] V")

print(f"\n  ── Scientific Context ──────────────────────────────────")
print(f"    SNR = {snr_db:.0f} dB is BELOW the noise floor.")
print(f"    A single unfiltered pulse is completely invisible.")
print(f"    This stress-tests filtering at an extreme boundary")
print(f"    more hostile than typical pulsar navigation scenarios.")
print(f"    Signal recovery under these conditions validates")
print(f"    the robustness of both analog and digital approaches.")

print(f"\n  Figure saved: program2_noise_injection.png")
print("=" * 62)

# Plot
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Broadband Noise Injection (Lab-Matched Conditions)",
             color='white', fontsize=13, fontweight='bold')

# Panel 1: clean signal — dense line + original 20 sample dots
axes[0].plot(m_dense, x_dense_volts, color='#00e5ff', linewidth=1.8, alpha=0.9)
axes[0].plot(m, x_volts, color='#00e5ff', linewidth=0, marker='o', markersize=5,
             label='DFT sample points')
axes[0].axhline(0, color='white', linewidth=0.7, linestyle='--', alpha=0.4)
axes[0].set_title(f'Clean Signal\n{SIGNAL_VPP} VPP (after 20 dB attenuation)',
                  color='white')
axes[0].set_xlabel('Sample Index')
axes[0].set_ylabel('Voltage (V)')
axes[0].set_ylim(-1.0, 1.0)
axes[0].legend(fontsize=8)

# Panel 2: noise only — dense, mimics oscilloscope bandwidth
axes[1].plot(m_dense, noise_dense, color='#888899', linewidth=0.8, alpha=0.85)
axes[1].axhline(noise_sigma,  color='#ff9f43', linestyle='--', linewidth=1.2,
                label=f'+1σ = {noise_sigma:.2f}V')
axes[1].axhline(-noise_sigma, color='#ff9f43', linestyle='--', linewidth=1.2,
                label=f'−1σ = {-noise_sigma:.2f}V')
axes[1].set_title(f'Noise Only  ({N_dense} pts, {OVERSAMPLE}× oversampled)\n'
                  f'100× signal RMS  (SNR = {achieved_snr:.0f} dB)',
                  color='white')
axes[1].set_xlabel('Sample Index')
axes[1].set_ylabel('Voltage (V)')
axes[1].legend(fontsize=8)

# Panel 3: combined — dense noisy trace + clean reference
axes[2].plot(m_dense, x_noisy_dense, color='#ff6b9d', linewidth=0.9, alpha=0.85,
             label=f'Noisy  SNR={achieved_snr:.1f} dB')
axes[2].plot(m_dense, x_dense_volts, color='#00e5ff', linewidth=2.0, linestyle='--',
             alpha=0.8, label='Clean (hidden in noise)')
axes[2].set_title('Noisy Signal (as received)\nSignal completely buried in noise',
                  color='white')
axes[2].set_xlabel('Sample Index')
axes[2].set_ylabel('Voltage (V)')
axes[2].legend()

for ax in axes:
    ax.set_xlim(-0.5, N - 0.5)

fig.tight_layout()
fig.savefig(OUTPUT_DIR / "program2_noise_injection.png",
            dpi=300, bbox_inches="tight")
plt.show()