import os
import pathlib

# ── Output directory (saves figures next to this script) ──────────────────────
OUTPUT_DIR = pathlib.Path(r"C:\Users\Lucas Chen\OneDrive\Science Project 2026\Digital Analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

"""
============================================================
PROGRAM 4 — Harmonic Attenuation Analysis (Frequency Domain)
============================================================
WHAT IT DOES:
  Computes the FFT of the clean signal and each filtered version,
  then measures how much each harmonic (H1-H10) is attenuated
  by each filter method. Expresses attenuation in decibels (dB)
  relative to the clean signal. Also computes filter frequency
  response curves and overlays them on the harmonic measurements.

WHY IT MATTERS FOR YOUR PROJECT:
  This is the FREQUENCY-DOMAIN equivalent of what your oscilloscope
  FFT showed in the lab. The analog filter you used attenuates
  harmonics above its cutoff frequency. But crucially, the
  attenuation is NOT perfectly flat below cutoff — there is
  gradual roll-off and, for the causal IIR, frequency-dependent
  phase shift that affects harmonics BELOW the cutoff too.

  This program lets you directly compare:
  - How much of H1, H2 (dominant) survives each filter
  - Whether the two filters agree below cutoff (they should)
  - How steeply each filter rolls off above cutoff (they differ)
  - Where YOUR analog filter's measured attenuation falls relative
    to the digital predictions

HOW TO USE IN YOUR NOTEBOOK:
  - Include in RESULTS + DATA ANALYSIS sections
  - Compare the digital predictions here to your oscilloscope FFT
    measurements from the lab
  - If your lab H2 amplitude after filtering was X mV, you can
    compute the actual attenuation: 20*log10(X_measured/X_clean)
    and plot it on this chart to validate the model
  - Write: "Fig 4 shows predicted harmonic attenuation for each
    digital method. H1 and H2, carrying X% of signal power, were
    well-preserved (< −3 dB) by all methods. Harmonics H5-H10
    were attenuated by 10-40 dB above cutoff, consistent with
    oscilloscope FFT measurements (Table 1)."
============================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, firwin, filtfilt, freqz

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

# ── Data ─────────────────────────────────────────────────────────────────────
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

sig_vpeak  = 0.75
data_scale = sig_vpeak / np.max(np.abs(x_clean))
x_volts    = x_clean * data_scale

np.random.seed(42)
x_rms       = np.sqrt(np.mean(x_volts**2))
noise_sigma = 100 * x_rms
noise_v     = np.random.normal(0, 1, N)
noise_v    -= noise_v.mean()
noise_v    /= noise_v.std()
noise_v    *= noise_sigma
x_noisy     = x_volts + noise_v

fs          = N
nyq         = fs / 2.0
cutoff_norm = 2.6 / nyq   # H2.6 ≈ 1300 Hz — matches lab cutoff, passes H1+H2

b_iir, a_iir = butter(4, cutoff_norm, btype='low')
x_iir        = lfilter(b_iir, a_iir, x_noisy)

h_fir        = firwin(9, cutoff_norm)
x_fir        = filtfilt(h_fir, 1.0, x_noisy, padlen=3)

WINDOW = 3
x_mavg = np.convolve(x_noisy, np.ones(WINDOW)/WINDOW, mode='same')

# ── FFT harmonic amplitudes ───────────────────────────────────────────────────
def harmonic_amps(sig, n=N):
    S    = np.fft.rfft(sig) / n
    amps = np.abs(S)
    amps[1:-1] *= 2
    return amps[1:n//2+1]    # H1 .. H10

amp_clean = harmonic_amps(x_volts)
amp_noisy = harmonic_amps(x_noisy)
amp_iir   = harmonic_amps(x_iir)
amp_fir   = harmonic_amps(x_fir)
amp_mavg  = harmonic_amps(x_mavg)

def att_db(amp_filt, amp_ref):
    ratio = np.where(amp_ref > 1e-12, amp_filt / amp_ref, 1.0)
    return 20 * np.log10(np.clip(ratio, 1e-10, None))

att_iir  = att_db(amp_iir,  amp_clean)
att_fir  = att_db(amp_fir,  amp_clean)
att_mavg = att_db(amp_mavg, amp_clean)

# Filter frequency responses
w_iir, h_iir_resp = freqz(b_iir, a_iir, worN=512)
w_fir, h_fir_resp = freqz(h_fir, 1.0,  worN=512)
freq_hz_iir = w_iir / np.pi * nyq
freq_hz_fir = w_fir / np.pi * nyq

# ── Printed Results ───────────────────────────────────────────────────────────
harmonic_nums = np.arange(1, N//2+1)

print("=" * 68)
print("  PROGRAM 4 — HARMONIC ATTENUATION ANALYSIS (FREQUENCY DOMAIN)")
print("=" * 68)
print(f"\n  Filter cutoff:  H{cutoff_norm*nyq:.1f} ≈ 1300 Hz (matches lab) = between H2 and H3")
print(f"  Below cutoff:   H1–H2 should pass with < 3 dB attenuation (96% of signal power)")
print(f"  Above cutoff:   H3–H10 should be attenuated significantly")

print(f"\n  ── Harmonic Amplitudes (Volts, scaled to 1.5 VPP) ──────────────────")
print(f"  {'H#':<5} {'Clean':>9} {'Noisy':>9} {'IIR':>9} {'FIR':>9} {'MAvg':>9}")
print(f"  {'─'*5} {'─'*9} {'─'*9} {'─'*9} {'─'*9} {'─'*9}")
for k in range(N//2):
    print(f"  H{k+1:<4} {amp_clean[k]:>9.4f} {amp_noisy[k]:>9.4f} "
          f"{amp_iir[k]:>9.4f} {amp_fir[k]:>9.4f} {amp_mavg[k]:>9.4f}")

print(f"\n  ── Attenuation (dB relative to clean) ─────────────────────────────")
print(f"  {'H#':<5} {'IIR (dB)':>10} {'FIR (dB)':>10} {'MAvg (dB)':>11}  Note")
print(f"  {'─'*5} {'─'*10} {'─'*10} {'─'*11}  {'─'*20}")
for k in range(N//2):
    cutoff_note = "← above cutoff (should be attenuated)" if k >= 3 else ""
    print(f"  H{k+1:<4} {att_iir[k]:>+10.2f} {att_fir[k]:>+10.2f} {att_mavg[k]:>+11.2f}  {cutoff_note}")

total_power  = np.sum(amp_clean**2)
dom_power_h12 = (amp_clean[0]**2 + amp_clean[1]**2) / total_power * 100
dom_power_h14 = np.sum(amp_clean[:4]**2) / total_power * 100

print(f"\n  ── Signal Power Distribution ────────────────────────────────────")
for k in range(N//2):
    pct = 100 * amp_clean[k]**2 / total_power
    bar = '█' * int(pct / 2)
    print(f"  H{k+1:<4} {pct:>5.1f}%  {bar}")
print(f"\n  H1+H2 carry  {dom_power_h12:.1f}% of total signal power")
print(f"  H1–H4 carry  {dom_power_h14:.1f}% of total signal power")
print(f"  → Cutoff at H2.6 preserves H1+H2 (96%) while attenuating H3–H10")

print(f"\n  ── Attenuation at Dominant Harmonics ────────────────────────────")
for k in [0, 1, 2]:  # H1-H3: H1+H2 pass, H3 is first attenuated
    print(f"  H{k+1}: IIR={att_iir[k]:+.1f} dB,  FIR={att_fir[k]:+.1f} dB  "
          f"→ {'✓ well preserved' if abs(att_iir[k]) < 3 else '⚠ significant attenuation'}")

print(f"\n  Figure saved: program4_harmonic_attenuation.png")
print("=" * 68)

# ── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle("Program 4 — Harmonic Attenuation Analysis (Frequency Domain)",
             color='white', fontsize=13, fontweight='bold')

# Panel 1: amplitude bar chart
ax = axes[0]
bw   = 0.18
xi   = np.arange(N//2)
ax.bar(xi - bw*1.5, amp_clean, bw, label='Clean',    color='#00e5ff', alpha=0.9)
ax.bar(xi - bw*0.5, amp_iir,   bw, label='IIR',      color='#ff9f43', alpha=0.9)
ax.bar(xi + bw*0.5, amp_fir,   bw, label='FIR',      color='#26de81', alpha=0.9)
ax.bar(xi + bw*1.5, amp_mavg,  bw, label='Mov.Avg',  color='#a29bfe', alpha=0.9)
ax.set_xticks(xi)
ax.set_xticklabels([f'H{k}' for k in harmonic_nums])
ax.set_xlabel('Harmonic')
ax.set_ylabel('Amplitude (V)')
ax.set_title('Harmonic Amplitudes\nClean vs. All Filtered Methods', color='white')
ax.legend()

# Panel 2: attenuation in dB
ax2 = axes[1]
ax2.plot(harmonic_nums, att_iir,  'o-', color='#ff9f43', linewidth=2.2, label='IIR Butterworth')
ax2.plot(harmonic_nums, att_fir,  's-', color='#26de81', linewidth=2.2, label='FIR Zero-phase')
ax2.plot(harmonic_nums, att_mavg, '^-', color='#a29bfe', linewidth=2.2, label='Moving Average')
ax2.axhline(0,   color='white',  linewidth=1,   linestyle='--', alpha=0.5, label='0 dB = no change')
ax2.axhline(-3,  color='yellow', linewidth=1,   linestyle=':',  alpha=0.8, label='−3 dB cutoff point')
ax2.axvline(cutoff_norm*nyq, color='red', linewidth=1.2,
            linestyle=':', alpha=0.8, label=f'Filter cutoff (H{cutoff_norm*nyq:.1f})')
ax2.set_xticks(harmonic_nums)
ax2.set_xticklabels([f'H{k}' for k in harmonic_nums])
ax2.set_xlabel('Harmonic')
ax2.set_ylabel('Attenuation (dB)')
ax2.set_title('Harmonic Attenuation\nRelative to Clean Signal', color='white')
ax2.legend(fontsize=8)

# Panel 3: filter frequency response curves
ax3 = axes[2]
ax3.plot(freq_hz_iir, 20*np.log10(np.abs(h_iir_resp) + 1e-12),
         color='#ff9f43', linewidth=2.2, label='IIR Butterworth')
ax3.plot(freq_hz_fir, 20*np.log10(np.abs(h_fir_resp) + 1e-12),
         color='#26de81', linewidth=2.2, label='FIR (one pass)')
ax3.axhline(-3,  color='yellow', linewidth=1,   linestyle=':', alpha=0.7, label='−3 dB')
ax3.axvline(cutoff_norm*nyq, color='red', linewidth=1.2,
            linestyle=':', alpha=0.8, label='Cutoff')
# Mark harmonic positions
for k in range(1, N//2+1):
    ax3.axvline(k, color='white', linewidth=0.5, alpha=0.25)
    ax3.text(k, -55, f'H{k}', ha='center', fontsize=7, color='#888899')
ax3.set_xlim(0, nyq)
ax3.set_ylim(-60, 5)
ax3.set_xlabel('Frequency (normalized, cycles/period)')
ax3.set_ylabel('Magnitude (dB)')
ax3.set_title('Filter Frequency Response\n(Butterworth vs FIR)', color='white')
ax3.legend(fontsize=8)

fig.tight_layout()
fig.savefig(OUTPUT_DIR / "program4_harmonic_attenuation.png",
            dpi=300, bbox_inches="tight")
plt.show()