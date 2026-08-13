import pathlib

OUTPUT_DIR = pathlib.Path(r"C:\Users\Lucas Chen\OneDrive\Science Project 2026\Digital Analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

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

# ── Data (identical to FILTER_COMPARISON.PY) ──────────────────────────────────
N = 20
m = np.arange(N)

A   = [2*240.3411499, 2*323.6750783, 2*19.62380682, 2*49.5953873,
       2*24.82707025, 2*3.716276805, 2*13.57305442, 2*24.24657408,
       2*57.89750227, 33.87470998]
phi = [-1.168084937,  1.279642856,  2.892337571, -1.593010231,
       -1.561450804,  0.301711856, -2.921065905,  1.31937808,
        0.245177689,  1.05072e-13]

x_clean    = np.sum([A[k] * np.cos(2*np.pi*(k+1)*m/N + phi[k])
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

# ── Method A: IIR Butterworth (causal) ────────────────────────────────────────
fs          = N
nyq         = fs / 2.0
cutoff_norm = 2.6 / nyq
b_iir, a_iir = butter(4, cutoff_norm, btype='low')
x_iir        = lfilter(b_iir, a_iir, x_noisy)

# ── Method B: Matched Filter ───────────────────────────────────────────────────
X_noisy    = np.fft.fft(x_noisy)
X_template = np.fft.fft(x_volts)
x_matched  = np.real(np.fft.ifft(np.conj(X_template) * X_noisy))
x_matched  = x_matched / np.max(np.abs(x_matched)) * np.max(np.abs(x_volts))

# ── Methods C & D: Epoch Folding ──────────────────────────────────────────────
N_FOLDS_C = 1_000
N_FOLDS_D = 100_000

rng_epoch = np.random.default_rng(999)
noise_C   = rng_epoch.normal(0, noise_sigma, (N_FOLDS_C, N))
x_epoch_C = x_volts + np.mean(noise_C, axis=0)
noise_D   = rng_epoch.normal(0, noise_sigma, (N_FOLDS_D, N))
x_epoch_D = x_volts + np.mean(noise_D, axis=0)

# ── TOA & navigation (same formulas as FILTER_COMPARISON.PY) ──────────────────
PULSAR_PERIOD_MS = 4.87
dt_ms            = PULSAR_PERIOD_MS / N          # ms per sample
dt_us            = dt_ms * 1e3                   # µs per sample

true_peak = int(np.argmax(x_volts))

def toa_bias_samples(sig):
    return int(np.argmax(sig)) - true_peak

def to_us(toa_samples):
    return toa_samples * dt_us

def nav_error_km(toa_samples):
    return abs(toa_samples) * dt_ms * 1e3 * 300 / 1e6

# ── Shared data for bar charts ─────────────────────────────────────────────────
method_labels = [
    'IIR Butterworth',
    'Matched Filter',
    f'Epoch Fold  (K={N_FOLDS_C:,})',
    f'Epoch Fold  (K={N_FOLDS_D:,})',
]
bar_colors = ['#ff9f43', '#74b9ff', '#26de81', '#fd79a8']
method_sigs = [x_iir, x_matched, x_epoch_C, x_epoch_D]

toa_biases_us  = [to_us(toa_bias_samples(s))       for s in method_sigs]
nav_errors_m   = [nav_error_km(toa_bias_samples(s)) * 1000 for s in method_sigs]

# ── Printed Results ────────────────────────────────────────────────────────────
print("=" * 70)
print("  TOA BIAS & NAVIGATION ERROR ANALYSIS")
print("=" * 70)
print(f"\n  Pulsar:  PSR J0030+0451  |  Period: {PULSAR_PERIOD_MS} ms  |  dt = {dt_us:.3f} µs/sample")
print(f"  Scale:   1 µs TOA error ≈ 300 m navigation error (SEXTANT)")
print(f"  True peak at: sample {true_peak}")
print(f"\n  {'Method':<30} {'TOA bias (samp)':>16} {'TOA bias (µs)':>14} {'Nav error (m)':>14}")
print(f"  {'─'*30} {'─'*16} {'─'*14} {'─'*14}")
for label, sig in zip(method_labels, method_sigs):
    b = toa_bias_samples(sig)
    print(f"  {label:<30} {b:>+16d} {to_us(b):>+14.3f} {nav_error_km(b)*1000:>14.1f}")
print("=" * 70)

# ── Figure 1: TOA Bias ─────────────────────────────────────────────────────────
fig1, ax = plt.subplots(figsize=(8, 5))
fig1.patch.set_facecolor('#0f0f1a')
ax.set_facecolor('#1a1a2e')

bars = ax.barh(method_labels, toa_biases_us, color=bar_colors,
               edgecolor='#555577', linewidth=0.8, height=0.5)
ax.axvline(0, color='#aaaacc', linewidth=1.2, linestyle='--', alpha=0.7)

val_range = max(abs(v) for v in toa_biases_us) or 1
for bar, val in zip(bars, toa_biases_us):
    offset = val_range * 0.04
    if val >= 0:
        ax.text(val + offset, bar.get_y() + bar.get_height()/2,
                f'{val:+.3f} µs', va='center', ha='left', fontsize=10, color='white')
    else:
        ax.text(val - offset, bar.get_y() + bar.get_height()/2,
                f'{val:+.3f} µs', va='center', ha='right', fontsize=10, color='white')

ax.set_xlabel('TOA Bias (µs)', fontsize=11)
ax.set_title('Pulse Time-of-Arrival Bias by Recovery Method', color='white', fontsize=12)
ax.tick_params(colors='#ccccdd')
for spine in ax.spines.values():
    spine.set_edgecolor('#444466')
xlim = (max(abs(v) for v in toa_biases_us) * 1.45) or 0.5
ax.set_xlim(-xlim, xlim)
fig1.tight_layout()
fig1.savefig(OUTPUT_DIR / "program5a_toa_bias.png", dpi=300, bbox_inches="tight")

# ── Figure 2: Navigation Error ─────────────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(8, 5))
fig2.patch.set_facecolor('#0f0f1a')
ax2.set_facecolor('#1a1a2e')

bars2 = ax2.barh(method_labels, nav_errors_m, color=bar_colors,
                 edgecolor='#555577', linewidth=0.8, height=0.5)
nav_range = max(nav_errors_m) or 1
for bar, val_m in zip(bars2, nav_errors_m):
    ax2.text(val_m + nav_range * 0.04, bar.get_y() + bar.get_height()/2,
             f'{val_m:.1f} m', va='center', ha='left', fontsize=10, color='white')

ax2.set_xlabel('Navigation Uncertainty (m)', fontsize=11)
ax2.set_title('Spacecraft Navigation Uncertainty by Recovery Method\n'
              '1 µs TOA error  ≈  300 m position error  (SEXTANT)',
              color='white', fontsize=12)
ax2.tick_params(colors='#ccccdd')
for spine in ax2.spines.values():
    spine.set_edgecolor('#444466')
ax2.set_xlim(0, (max(nav_errors_m) * 1.45) or 0.5)
fig2.tight_layout()
fig2.savefig(OUTPUT_DIR / "program5b_nav_error.png", dpi=300, bbox_inches="tight")

plt.show()
