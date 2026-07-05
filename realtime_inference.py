import serial
import time
import pickle
import pandas as pd
import os

# --- Configuration ---
COM_PORT = 'COM3'  # قم بتغيير هذا إلى المنفذ الصحيح إذا كان مختلفاً
BAUD_RATE = 9600
MODEL_PATH = r"c:/Users/POWER/Desktop/NILM/analysis_output/nilm_rf_model.pkl"

print("==================================================")
print("NILM Real-Time Inference Started...")
print("==================================================")

# 1. Load the trained model
if not os.path.exists(MODEL_PATH):
    print(f"Error: Model not found at {MODEL_PATH}")
    print("Please make sure you have trained the model first.")
    exit()

print("Loading Machine Learning model...")
with open(MODEL_PATH, 'rb') as f:
    clf = pickle.load(f)
print("Model loaded successfully!")

# 2. Connect to Serial Port
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # انتظار استقرار الاتصال
    print(f"Connected to {COM_PORT} successfully!")
except Exception as e:
    print(f"Error connecting to port: {e}")
    print("Make sure the Wemos is connected and the COM port is correct.")
    exit()

print("\n[START] Waiting for data from Wemos...\n")
print("Time(ms)\tVoltage(V)\tCurrent(A)\tPower(W)\t=> PREDICTED DEVICE")
print("-" * 80)

# إرسال سطر فارغ أو أي إشارة بدء إذا كان Wemos ينتظر ذلك
try:
    ser.write(b'\n')
except:
    pass

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # محاولة استخراج الأرقام من السطر
                # يفترض أن الـ Wemos يرسل: Time,Voltage,Current,Power
                parts = line.split(',')
                
                # إذا كان السطر يحتوي على نصوص غير متوقعة، نحاول أخذ آخر 4 أرقام
                if len(parts) >= 4:
                    try:
                        # أخذ آخر 4 قيم بافتراض أنها الوقت، الجهد، التيار، الطاقة
                        t_ms = float(parts[-4])
                        v = float(parts[-3])
                        i = float(parts[-2])
                        p = float(parts[-1])
                        
                        # إنشاء DataFrame لتمريره للنموذج (بأسماء الأعمدة التي تدرب عليها)
                        features = pd.DataFrame([[v, i, p]], columns=['Voltage(V)', 'Current(A)', 'Power(W)'])
                        
                        # التنبؤ
                        prediction = clf.predict(features)[0]
                        
                        print(f"{t_ms:.0f}\t\t{v:.2f}\t\t{i:.3f}\t\t{p:.2f}\t\t=> [{prediction.upper()}]")
                        
                    except ValueError:
                        # السطر لا يحتوي على أرقام قابلة للتحويل
                        pass
except KeyboardInterrupt:
    print("\nInference stopped by user.")
finally:
    ser.close()
    print("Serial port closed.")
