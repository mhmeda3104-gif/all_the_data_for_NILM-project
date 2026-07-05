import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
import warnings
warnings.filterwarnings('ignore')

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
MIN_VOLTAGE = 150.0

DEVICE_MAP = {
    "freezer":             "Freezer",
    "fridge":              "Fridge",
    "oven":                "Oven",
    "phone charger":       "Phone Charger",
    "solder":              "Solder",
    "split":               "Split AC",
    "water heater":        "Water Heater",
    "water heater&cooler": "Water Heater&Cooler"
}

COLORS = {
    "Freezer":             "#E63946",
    "Fridge":              "#F4A261",
    "Oven":                "#2A9D8F",
    "Phone Charger":       "#457B9D",
    "Solder":              "#8338EC",
    "Split AC":            "#FB5607",
    "Water Heater":        "#06D6A0",
    "Water Heater&Cooler": "#FFBE0B"
}

all_dfs = {}

for filename in os.listdir(DATASET_DIR):
    if not filename.endswith(".csv") or filename == "nilm_log.csv":
        continue
    device_key = filename.replace(".csv", "").lower().strip()
    if device_key not in DEVICE_MAP:
        continue
    label = DEVICE_MAP[device_key]
    filepath = os.path.join(DATASET_DIR, filename)
    try:
        df = pd.read_csv(filepath, on_bad_lines='skip')
        df.columns = [c.strip() for c in df.columns]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)
        df = df[df['Voltage(V)'] >= MIN_VOLTAGE]
        if len(df) >= 10:
            all_dfs[label] = df
    except Exception:
        continue

# =====================================================================
# Figure: Current Interference / Overlap Visualization
# =====================================================================
fig = plt.figure(figsize=(16, 14))
fig.patch.set_facecolor('#0D1117')
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

# ---- Plot 1: Current Time-Series Overlay (Simulated Simultaneous Operation) ----
ax1 = fig.add_subplot(gs[0, :])
ax1.set_facecolor('#161B22')

t = np.linspace(0, 10, 300)
total_current = np.zeros(len(t))
legend_patches = []

for label, df in all_dfs.items():
    mean_I = df['Current(A)'].mean()
    std_I  = df['Current(A)'].std()
    # Simulate a realistic fluctuating current waveform for each device
    np.random.seed(list(all_dfs.keys()).index(label))
    noise = np.random.normal(0, std_I * 0.3, len(t))
    wave  = mean_I + noise
    wave  = np.clip(wave, 0, None)
    total_current += wave
    color = COLORS[label]
    ax1.plot(t, wave, color=color, linewidth=1.8, alpha=0.85, label=label)
    legend_patches.append(mpatches.Patch(color=color, label=f"{label} (~{mean_I:.2f}A avg)"))

ax1.plot(t, total_current, color='white', linewidth=2.5, linestyle='--', 
         alpha=0.9, label='Total (Aggregate) Current')
legend_patches.append(mpatches.Patch(color='white', label='⚡ Total Aggregate Current (Mixed Signal)'))

ax1.set_title('Current Interference: All Devices Operating Simultaneously', 
              color='white', fontsize=14, fontweight='bold', pad=12)
ax1.set_xlabel('Time (seconds)', color='#8B949E', fontsize=11)
ax1.set_ylabel('Current (Amperes)', color='#8B949E', fontsize=11)
ax1.tick_params(colors='#8B949E')
ax1.spines[:].set_color('#30363D')
ax1.legend(handles=legend_patches, loc='upper right', fontsize=8,
           facecolor='#21262D', edgecolor='#30363D', labelcolor='white',
           ncol=3)
ax1.grid(axis='y', color='#21262D', linewidth=0.7)

# Annotation
ax1.annotate('⚠️ The NILM system receives ONLY this\nmixed aggregate signal and must\ndisaggregate each appliance from it.',
             xy=(5, total_current[150]), xytext=(6.5, total_current[150] * 0.6),
             color='#FFA657', fontsize=9, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#FFA657', lw=1.5),
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#21262D', edgecolor='#FFA657'))

# ---- Plot 2: Current Range (Min/Max) Bar Chart ----
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_facecolor('#161B22')

labels_list = list(all_dfs.keys())
means  = [all_dfs[l]['Current(A)'].mean() for l in labels_list]
stds   = [all_dfs[l]['Current(A)'].std()  for l in labels_list]
colors = [COLORS[l] for l in labels_list]
x_pos  = np.arange(len(labels_list))

bars = ax2.bar(x_pos, means, yerr=stds, capsize=5,
               color=colors, alpha=0.85, edgecolor='white', linewidth=0.5,
               error_kw=dict(ecolor='white', elinewidth=1.5, capthick=1.5))

ax2.set_title('Mean Current per Appliance\n(with ±1σ Interference Band)', 
              color='white', fontsize=11, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(labels_list, rotation=40, ha='right', color='#8B949E', fontsize=8)
ax2.set_ylabel('Current (A)', color='#8B949E', fontsize=10)
ax2.tick_params(colors='#8B949E')
ax2.spines[:].set_color('#30363D')
ax2.grid(axis='y', color='#21262D', linewidth=0.7)

for bar, mean in zip(bars, means):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{mean:.2f}A', ha='center', va='bottom', color='white', fontsize=8, fontweight='bold')

# ---- Plot 3: Current Overlap Heatmap ----
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor('#161B22')

# Build overlap matrix: how much do current ranges overlap between devices?
n = len(labels_list)
overlap_matrix = np.zeros((n, n))

for i, l1 in enumerate(labels_list):
    i_min1 = all_dfs[l1]['Current(A)'].mean() - all_dfs[l1]['Current(A)'].std()
    i_max1 = all_dfs[l1]['Current(A)'].mean() + all_dfs[l1]['Current(A)'].std()
    for j, l2 in enumerate(labels_list):
        i_min2 = all_dfs[l2]['Current(A)'].mean() - all_dfs[l2]['Current(A)'].std()
        i_max2 = all_dfs[l2]['Current(A)'].mean() + all_dfs[l2]['Current(A)'].std()
        overlap = max(0, min(i_max1, i_max2) - max(i_min1, i_min2))
        range1  = i_max1 - i_min1 + 1e-9
        overlap_matrix[i][j] = overlap / range1  # normalized

im = ax3.imshow(overlap_matrix, cmap='YlOrRd', vmin=0, vmax=1, aspect='auto')
ax3.set_xticks(np.arange(n))
ax3.set_yticks(np.arange(n))
short = [l.replace(' ', '\n') for l in labels_list]
ax3.set_xticklabels(short, color='#8B949E', fontsize=7, rotation=45, ha='right')
ax3.set_yticklabels(short, color='#8B949E', fontsize=7)
ax3.set_title('Current Range Overlap Matrix\n(Higher = Harder to Distinguish)', 
              color='white', fontsize=11, fontweight='bold')

for i in range(n):
    for j in range(n):
        val = overlap_matrix[i][j]
        ax3.text(j, i, f'{val:.2f}', ha='center', va='center',
                 color='black' if val > 0.5 else 'white', fontsize=7, fontweight='bold')

cbar = plt.colorbar(im, ax=ax3)
cbar.ax.yaxis.set_tick_params(color='#8B949E')
cbar.set_label('Overlap Ratio', color='#8B949E')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8B949E')

fig.suptitle('NILM — Appliance Current Interference & Overlap Analysis',
             color='white', fontsize=16, fontweight='bold', y=0.98)

out_path = os.path.join(OUTPUT_DIR, 'ML_CurrentInterference.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='#0D1117')
print(f"Saved: {out_path}")
