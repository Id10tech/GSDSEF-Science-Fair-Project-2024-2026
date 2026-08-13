import os
import pathlib

OUTPUT_DIR = pathlib.Path(r"C:\Users\Lucas Chen\OneDrive\Science Project 2026\Digital Analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, group_delay

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

# Method A: IIR Butterworth LP (analog-equivalent baseline)
fs          = N
nyq         = fs / 2.0
# H2.6 ≈ 1300 Hz — matches lab cutoff. Passes H1+H2 (96% of signal power),
# rolls off H3–H10. Butterworth's steeper rolloff vs. lab analog filter means
# this cutoff can sit closer to the signal than the physical 1300 Hz used.
cutoff_norm = 2.6 / nyq
b_iir, a_iir = butter(4, cutoff_norm, btype='low')
x_iir        = lfilter(b_iir, a_iir, x_noisy)

# ── Method B: Matched Filter (circular cross-correlation with template) ────────
# Optimal linear detector for known signal shape in white noise.
# Uses FFT-based circular cross-correlation: H*(f) · X(f)
X_noisy    = np.fft.fft(x_noisy)
X_template = np.fft.fft(x_volts)
x_matched  = np.real(np.fft.ifft(np.conj(X_template) * X_noisy))
# Normalize to signal amplitude scale for display
x_matched  = x_matched / np.max(np.abs(x_matched)) * np.max(np.abs(x_volts))

# ── Methods C & D: Epoch Folding ──────────────────────────────────────────────
# Stack K independent noisy periods; noise reduces by 1/√K while signal
# accumulates coherently. This is exactly what NICER does on-orbit.
N_FOLDS_C = 1_000
N_FOLDS_D = 100_000

rng_epoch = np.random.default_rng(999)   # independent from the single-period noise

# Vectorised: generate all noise at once, then mean over fold axis
noise_C   = rng_epoch.normal(0, noise_sigma, (N_FOLDS_C, N))
x_epoch_C = x_volts + np.mean(noise_C, axis=0)  # = mean(x_volts + noise_i)

noise_D   = rng_epoch.normal(0, noise_sigma, (N_FOLDS_D, N))
x_epoch_D = x_volts + np.mean(noise_D, axis=0)

# ── Metrics ───────────────────────────────────────────────────────────────────
def snr_db(sig, clean):
    residual = sig - clean
    return 10 * np.log10(np.mean(clean**2) / np.mean(residual**2))

def toa_bias(sig, clean):
    return int(np.argmax(sig)) - int(np.argmax(clean))

PULSAR_PERIOD_MS = 4.87
dt_ms            = PULSAR_PERIOD_MS / N

def nav_error_km(toa_samples):
    return abs(toa_samples) * dt_ms * 1e3 * 300 / 1e6

def expected_epoch_snr(n_folds):
    return snr_db(x_noisy, x_volts) + 10 * np.log10(n_folds)

true_peak = int(np.argmax(x_volts))

results = {
    'IIR Butterworth (baseline)':    (x_iir,     '#ff9f43'),
    'Matched Filter':                 (x_matched, '#74b9ff'),
    f'Epoch Fold  (K={N_FOLDS_C:,})': (x_epoch_C, '#26de81'),
    f'Epoch Fold  (K={N_FOLDS_D:,})': (x_epoch_D, '#fd79a8'),
}

# ── Printed Results ───────────────────────────────────────────────────────────
print("=" * 70)
print("  PROGRAM 3 — ADVANCED DIGITAL RECOVERY METHODS")
print("=" * 70)
print(f"\n  Input SNR:    {snr_db(x_noisy, x_volts):.1f} dB  (100× signal RMS, −40 dB target)")
print(f"  True peak at: sample {true_peak}")
print(f"  Pulsar:       PSR J0030+0451, period {PULSAR_PERIOD_MS} ms → {dt_ms:.3f} ms/sample")

print(f"\n  ── Theoretical SNR Improvement ────────────────────────────────────")
print(f"  IIR LP (H4.5 cutoff):    removes out-of-band noise only (~3 dB gain)")
print(f"  Matched filter (N={N}):   10·log₁₀({N}) = {10*np.log10(N):.1f} dB gain")
print(f"  Epoch fold K=1,000:      10·log₁₀(1000) = {10*np.log10(1000):.1f} dB gain")
print(f"  Epoch fold K=100,000:    10·log₁₀(100000) = {10*np.log10(100_000):.1f} dB gain")

print(f"\n  ── Results ─────────────────────────────────────────────────────────")
print(f"  {'Method':<35} {'SNR out':>8} {'ΔSNR':>7} {'TOA bias':>10} {'Nav err':>10}")
print(f"  {'─'*35} {'─'*8} {'─'*7} {'─'*10} {'─'*10}")
snr_in = snr_db(x_noisy, x_volts)
print(f"  {'Noisy (unfiltered)':<35} {snr_in:>+8.1f} {'—':>7} {'—':>10} {'—':>10}")
for name, (sig, _) in results.items():
    s   = snr_db(sig, x_volts)
    t   = toa_bias(sig, x_volts)
    nav = nav_error_km(t)
    print(f"  {name:<35} {s:>+8.1f} {s-snr_in:>+7.1f} {t:>+10d} {nav:>9.3f}km")

print(f"\n  ── Key Finding ─────────────────────────────────────────────────────")
snr_epoch_C = snr_db(x_epoch_C, x_volts)
snr_epoch_D = snr_db(x_epoch_D, x_volts)
print(f"  IIR LP filter gain:     {snr_db(x_iir, x_volts) - snr_in:+.1f} dB  (mostly noise, fails at −40 dB)")
print(f"  Matched filter gain:    {snr_db(x_matched, x_volts) - snr_in:+.1f} dB  (≈ theoretical {10*np.log10(N):.0f} dB)")
print(f"  Epoch fold 1k gain:     {snr_epoch_C - snr_in:+.1f} dB  → net {snr_epoch_C:.1f} dB")
print(f"  Epoch fold 100k gain:   {snr_epoch_D - snr_in:+.1f} dB  → net {snr_epoch_D:.1f} dB")
print(f"\n  → Epoch folding (100k) matches NICER ~8 min observation of J0030+0451")
print(f"    (~{PULSAR_PERIOD_MS}ms period → {int(8*60*1000/PULSAR_PERIOD_MS):,} pulses in 8 min)")

print(f"\n  Figure saved: program3_filter_comparison.png")
print("=" * 70)

# ── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("Digital Processing Pipeline: LP Filter vs. Matched Filter vs. Epoch Folding",
             color='white', fontsize=12, fontweight='bold')

panels = [
    (axes[0, 0], x_iir,     '#ff9f43',
     f'Method A: IIR Butterworth LP  (analog baseline)\n'
     f'SNR = {snr_db(x_iir, x_volts):+.1f} dB  |  TOA bias = {toa_bias(x_iir, x_volts):+d} sample(s)'),
    (axes[0, 1], x_matched, '#74b9ff',
     f'Method B: Matched Filter  (cross-correlation, optimal single-pass)\n'
     f'SNR = {snr_db(x_matched, x_volts):+.1f} dB  |  TOA bias = {toa_bias(x_matched, x_volts):+d} sample(s)'),
    (axes[1, 0], x_epoch_C, '#26de81',
     f'Method C: Epoch Folding  (K = {N_FOLDS_C:,} pulses)\n'
     f'SNR = {snr_db(x_epoch_C, x_volts):+.1f} dB  |  TOA bias = {toa_bias(x_epoch_C, x_volts):+d} sample(s)'),
    (axes[1, 1], x_epoch_D, '#fd79a8',
     f'Method D: Epoch Folding  (K = {N_FOLDS_D:,} pulses, NICER scale)\n'
     f'SNR = {snr_db(x_epoch_D, x_volts):+.1f} dB  |  TOA bias = {toa_bias(x_epoch_D, x_volts):+d} sample(s)'),
]

for ax, sig, color, title in panels:
    ax.fill_between(m, sig, alpha=0.12, color=color)
    ax.plot(m, x_volts, color='#00e5ff', linewidth=1.8, linestyle='--',
            alpha=0.75, label='Clean reference')
    ax.plot(m, sig, color=color, linewidth=2.2, label='Output')
    ax.axvline(true_peak, color='#00e5ff', linewidth=1.3,
               linestyle=':', alpha=0.8, label=f'True peak (s{true_peak})')
    det_peak = int(np.argmax(sig))
    ax.axvline(det_peak, color=color, linewidth=1.3,
               linestyle='-', alpha=0.9, label=f'Detected peak (s{det_peak})')
    if det_peak != true_peak:
        ax.axvspan(min(true_peak, det_peak), max(true_peak, det_peak),
                   alpha=0.12, color='red', label='TOA bias region')
    ax.set_title(title, color='white', fontsize=10)
    ax.set_xlabel('Sample Index')
    ax.set_ylabel('Voltage (V)')
    ax.set_xlim(-0.5, N - 0.5)
    ax.legend(loc='upper right', fontsize=7.5)

fig.tight_layout()
fig.savefig(OUTPUT_DIR / "program3_filter_comparison.png",
            dpi=300, bbox_inches="tight")
plt.show()
