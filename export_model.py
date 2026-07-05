from micromlgen import port
import pickle
import os

MODEL_PATH = r"c:/Users/POWER/Desktop/NILM/analysis_output/nilm_rf_model.pkl"
HEADER_PATH = r"c:/Users/POWER/Desktop/NILM/the main folder/src/nilm_model.h"

print("Loading model...")
with open(MODEL_PATH, 'rb') as f:
    clf = pickle.load(f)

print("Exporting model to C++ using micromlgen...")
c_code = port(clf)

with open(HEADER_PATH, 'w') as f:
    f.write(c_code)

print(f"Model exported successfully to: {HEADER_PATH}")
