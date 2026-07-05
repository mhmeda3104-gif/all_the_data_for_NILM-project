import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from micromlgen import port

MAIN_FOLDER = r"c:/Users/POWER/Desktop/NILM/the main folder"
HEADER_PATH = r"c:/Users/POWER/Desktop/NILM/the main folder/src/nilm_model.h"

print("==================================================")
print("Starting Delta-P (Event-Based) Model Training...")
print("==================================================")

csv_files = [f for f in os.listdir(MAIN_FOLDER) if f.endswith('.csv') and f != 'nilm_log.csv']
dataframes = []

for file in csv_files:
    file_path = os.path.join(MAIN_FOLDER, file)
    device_name = file.replace('.csv', '')
    try:
        df = pd.read_csv(file_path)
        if 'Voltage(V)' in df.columns and 'Current(A)' in df.columns and 'Power(W)' in df.columns:
            # Drop the first 20% to avoid startup transients (Inrush current)
            # This ensures the model learns the pure "Steady State Delta"
            drop_count = int(len(df) * 0.2)
            df_steady = df.iloc[drop_count:].copy()
            df_steady['Device'] = device_name
            dataframes.append(df_steady)
            print(f"Loaded {device_name}: {len(df_steady)} steady-state records.")
    except Exception as e:
        print(f"Error loading {file}: {e}")

if not dataframes:
    print("No valid data found.")
    exit()

combined_df = pd.concat(dataframes, ignore_index=True)
combined_df.dropna(inplace=True)

X = combined_df[['Voltage(V)', 'Current(A)', 'Power(W)']]
y = combined_df['Device']

print(f"Total training samples: {len(X)}")
print("Training Random Forest Classifier (Optimized for ESP32)...")
# Limit estimators and depth so the C++ code fits easily in ESP32 memory
clf = RandomForestClassifier(n_estimators=25, max_depth=12, random_state=42)
clf.fit(X, y)

print("Exporting model to C++ header (nilm_model.h)...")
c_code = port(clf)

with open(HEADER_PATH, 'w') as f:
    f.write(c_code)

print(f"Model exported successfully to: {HEADER_PATH}")
print("Training Complete!")
