import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
MIN_VOLTAGE = 150.0

DEVICE_MAP = {
    "freezer": "Freezer",
    "fridge": "Fridge",
    "oven": "Oven",
    "phone charger": "Phone Charger",
    "solder": "Solder",
    "split": "Split AC",
    "water heater": "Water Heater",
    "water heater&cooler": "Water Heater&Cooler"
}

all_dfs = []

for filename in os.listdir(DATASET_DIR):
    if not filename.endswith(".csv") or filename == "nilm_log.csv":
        continue

    device_key = filename.replace(".csv", "").lower().strip()
    if device_key not in DEVICE_MAP:
        continue

    filepath = os.path.join(DATASET_DIR, filename)
    try:
        df = pd.read_csv(filepath, on_bad_lines='skip')
    except Exception:
        continue

    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)
    df = df[df['Voltage(V)'] >= MIN_VOLTAGE]
    
    if len(df) < 10:
        continue

    df['Device'] = DEVICE_MAP[device_key]
    all_dfs.append(df)

if not all_dfs:
    print("No valid data found.")
    exit()

data = pd.concat(all_dfs, ignore_index=True)
data['PowerFactor'] = data['Power(W)'] / (data['Voltage(V)'] * data['Current(A)'])
data['PowerFactor'].replace([np.inf, -np.inf], np.nan, inplace=True)
data.fillna(1.0, inplace=True)
data['PowerFactor'] = np.clip(data['PowerFactor'], 0, 1)

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'figure.dpi': 150})

# 1. Scatter Plot: Power vs Current colored by Device
plt.figure(figsize=(10, 6))
sns.scatterplot(data=data, x='Current(A)', y='Power(W)', hue='Device', alpha=0.7, palette='Set2')
plt.title('Appliance Power vs Current Signatures')
plt.xlabel('Current (Amperes)')
plt.ylabel('Power (Watts)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(DATASET_DIR, 'ML_Power_vs_Current.png'))

# 2. Boxplot: Power Factor by Device
plt.figure(figsize=(10, 6))
sns.boxplot(data=data, x='Device', y='PowerFactor', palette='Pastel1')
plt.title('Power Factor Distribution by Appliance')
plt.xlabel('Appliance')
plt.ylabel('Power Factor (PF)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(DATASET_DIR, 'ML_PowerFactor_Dist.png'))

# 3. Scatter Plot: Power Factor vs Power
plt.figure(figsize=(10, 6))
sns.scatterplot(data=data, x='PowerFactor', y='Power(W)', hue='Device', alpha=0.7, palette='Dark2')
plt.title('Power Factor vs Power (Appliance Clusters)')
plt.xlabel('Power Factor (PF)')
plt.ylabel('Power (Watts)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(DATASET_DIR, 'ML_PF_vs_Power.png'))

print("Images generated successfully: ML_Power_vs_Current.png, ML_PowerFactor_Dist.png, ML_PF_vs_Power.png")
