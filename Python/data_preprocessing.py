"""
data_preprocessing.py

This script scans the 'data' folder for CSV files of raw sensor data,
extracts enhanced features, 
and outputs a combined features.csv file.

Assumes each file is named in the format: data_<label>_<timestamp>.csv
"""

import os
import glob
import pandas as pd
import numpy as np

# Folder where raw data CSVs are stored (create this folder and move your CSV files here)
data_folder = "data"
files = glob.glob(os.path.join(data_folder, "*.csv"))

rows = []
for file in files:
    # Extract label from filename: expected pattern: data_<label>_<timestamp>.csv
    basename = os.path.basename(file)
    parts = basename.split('_')
    if len(parts) < 3:
        continue
    label = parts[1]
    df = pd.read_csv(file)
    if 'value' not in df.columns:
        continue
    
    values = df['value'].values
    # If your CSV contains a "timestamp" column with the actual times, use it;
    # otherwise, assume uniform sampling (you may adjust dx accordingly)
    if 'timestamp' in df.columns:
        timestamps = df['timestamp'].values
        auc = np.trapezoid(values, timestamps)
    else:
        # If no timestamp available, use the sample index (adjust dx if needed)
        auc = np.trapezoid(values)
    
    # Basic features
    mean_val = np.mean(values)
    std_val = np.std(values)
    rms_val = np.sqrt(np.mean(np.square(values)))
    max_val = np.max(values)
    min_val = np.min(values)
    
    # Compute first derivative of the signal and its statistics
    derivative = np.diff(values)
    if len(derivative) > 0:
        mean_deriv = np.mean(derivative)
        std_deriv = np.std(derivative)
    else:
        mean_deriv = 0
        std_deriv = 0
    
    rows.append({
        "label": label, 
        "auc": auc,
        "mean": mean_val, 
        "std": std_val, 
        "rms": rms_val,
        "max": max_val,
        "min": min_val,
        "mean_deriv": mean_deriv,
        "std_deriv": std_deriv
    })

features_df = pd.DataFrame(rows)
features_df.to_csv("features.csv", index=False)
print("Features saved to features.csv")
