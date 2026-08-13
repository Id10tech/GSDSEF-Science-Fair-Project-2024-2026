import os
import pathlib

# Output directory
OUTPUT_DIR = pathlib.Path(r"C:\Users\Lucas Chen\OneDrive\Science Project 2026\Digital Analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

import numpy as np
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Style
plt.rcParams.update({
    'figure.facecolor': '#0f0f1a', 'axes.facecolor': '#1a1a2e',
    'axes.edgecolor':   '#444466', 'axes.grid': True,
    'grid.color':       '#2a2a4a', 'grid.linewidth': 0.6,
    'text.color':       '#ccccdd', 'axes.labelcolor': '#ccccdd',
    'xtick.color':      '#ccccdd', 'ytick.color':     '#ccccdd',
    'legend.facecolor': '#1a1a2e', 'legend.edgecolor':'#444466',
    'axes.titlesize':   11,        'axes.labelsize':   10,
    'legend.fontsize':  8,
})

HCOLORS = ['#00e5ff','#ff6b9d','#ff9f43','#26de81','#a29bfe',
           '#fd79a8','#fdcb6e','#74b9ff','#55efc4','#e17055']

# Data
N = 20
m = np.arange(N)

A   = [2*240.3411499, 2*323.6750783, 2*19.62380682, 2*49.5953873,
       2*24.82707025, 2*3.716276805, 2*13.57305442, 2*24.24657408,
       2*57.89750227, 33.87470998]

phi = [-1.168084937,  1.279642856,  2.892337571, -1.593010231,
       -1.561450804,  0.301711856, -2.921065905,  1.31937808,
        0.245177689,  1.05072e-13]

harmonics = [A[k] * np.cos(2*np.pi*(k+1)*m/N + phi[k]) for k in range(N//2)]
x_clean   = np.sum(harmonics, axis=0)

data = np.array([473.3178654,   44.08352668, 129.9303944,  -431.5545244,
                  44.08352668,  250.5800464, 619.4895592,   839.9071926,
                 575.4060325,  512.7610209,           0,  -436.1948956,
                -918.7935035, -1111.36891,  -1160.092807,  -684.4547564,
                  -2.320185615, 382.8306265,  577.7262181,   294.6635731])

# Printed Results
print("=" * 60)
print("  PROGRAM 1 — DFT HARMONIC RECONSTRUCTION")
print("=" * 60)

print(f"\n  Signal properties:")
print(f"    Samples (N):           {N}")
print(f"    Harmonics (N/2):       {N//2}")
print(f"    Peak amplitude:        {np.max(x_clean):.2f} counts (sample {np.argmax(x_clean)})")
print(f"    Trough amplitude:      {np.min(x_clean):.2f} counts (sample {np.argmin(x_clean)})")
print(f"    Peak-to-peak:          {np.max(x_clean) - np.min(x_clean):.2f} counts")
print(f"    RMS:                   {np.sqrt(np.mean(x_clean**2)):.2f} counts")

print(f"\n  Harmonic breakdown:")
print(f"  {'H#':<5} {'Amplitude':>12} {'% of total power':>18} {'Phase (rad)':>14}")
print(f"  {'─'*5} {'─'*12} {'─'*18} {'─'*14}")

total_power = sum(a**2 for a in A)
for k, (a, p) in enumerate(zip(A, phi), start=1):
    pct = 100 * a**2 / total_power
    print(f"  H{k:<4} {a:>12.3f} {pct:>17.1f}% {p:>14.6f}")

# Reconstruction quality
residual_max = np.max(np.abs(x_clean - data))
residual_rms = np.sqrt(np.mean((x_clean - data)**2))
print(f"\n  Reconstruction accuracy:")
print(f"    Max residual:          {residual_max:.2e}  (should be ~0)")
print(f"    RMS residual:          {residual_rms:.2e}")
print(f"    Quality:               {'EXACT ✓' if residual_max < 0.01 else 'APPROXIMATE'}")

# Which harmonics carry the signal
dominant = sorted(range(N//2), key=lambda i: A[i]**2, reverse=True)
print(f"\n  Top 3 harmonics by power:")
for i in dominant[:3]:
    pct = 100 * A[i]**2 / total_power
    print(f"    H{i+1}: A={A[i]:.1f}, {pct:.1f}% of total signal power")

print(f"\n  → H1+H2 carry {100*(A[0]**2+A[1]**2)/total_power:.1f}% of total signal power")
print(f"  → These MUST be preserved by any filter for valid TOA extraction")
print(f"\n  Figure saved: program1_dft_reconstruction.png")
print("=" * 60)

# Plot
fig, ax = plt.subplots(1, 1, figsize=(12, 7))
fig.suptitle("DFT Harmonic Reconstruction of Pulsar Waveform",
             color='white', fontsize=13, fontweight='bold')

for i, h in enumerate(harmonics):
    ax.plot(m, h, color=HCOLORS[i], alpha=0.55, linewidth=1.3,
            linestyle='--', label=f'H{i+1}  A={A[i]:.0f}')
ax.plot(m, x_clean, color='#ff6b9d', linewidth=2.8, label='DFT Sum', zorder=5)
ax.plot(m, data, color='#00e5ff', linewidth=2, linestyle=':',
        marker='o', markersize=6, label='Original Data', zorder=6)
ax.set_xlabel('Sample Index')
ax.set_ylabel('Amplitude (pulse counts)')
ax.set_title('Individual harmonics H1–H10 and DFT sum vs original data',
             color='#aaaacc', fontsize=9)
ax.legend(ncol=6, loc='upper center', bbox_to_anchor=(0.5, -0.12),
          borderaxespad=0)

fig.tight_layout()
fig.subplots_adjust(bottom=0.22)
fig.savefig(OUTPUT_DIR / "program1_dft_reconstruction.png",
            dpi=300, bbox_inches="tight")
plt.show()