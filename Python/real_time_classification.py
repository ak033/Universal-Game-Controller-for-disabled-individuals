"""
real_time_classification.py

This script performs real-time classification by reading sensor data from the serial port,
processing a sliding window of data, extracting enhanced features,
and using the trained model to predict the movement.


"""

import serial
import time
import numpy as np
import tensorflow as tf
from collections import deque

# Load the trained model
model = tf.keras.models.load_model("emg_classifier.h5")
# Define label classes as per the training (update these based on your actual labels)
label_classes = ['clench', 'index', 'rest', 'wrist']

# Parameters for the sliding window
WINDOW_SIZE = 100  # Number of samples in each window
OVERLAP_PERCENTAGE = 0  # 50% overlap between windows
CONFIDENCE_THRESHOLD = 0.7  # Only report predictions above this confidence

data_buffer = deque(maxlen=WINDOW_SIZE)
timestamps_buffer = deque(maxlen=WINDOW_SIZE)

# Open serial connection (adjust port if necessary)
ser = serial.Serial('COM4', 9600)
ser.flushInput()
time.sleep(0.5)

def extract_features(window, timestamps):
    """
    Extract enhanced features from a list of sensor values.
    Features: AUC, mean, std, RMS, max, min, mean derivative, std derivative.
    """
    window = np.array(window)
    timestamps = np.array(timestamps)
    
    # Calculate AUC using the trapezoidal rule
    if len(timestamps) > 1:
        auc = np.trapezoid(window, timestamps)
    else:
        auc = 0

    mean_val = np.mean(window)
    std_val = np.std(window)
    rms_val = np.sqrt(np.mean(np.square(window)))
    max_val = np.max(window)
    min_val = np.min(window)
    
    # Compute derivative features
    derivative = np.diff(window)
    if len(derivative) > 0:
        mean_deriv = np.mean(derivative)
        std_deriv = np.std(derivative)
    else:
        mean_deriv = 0
        std_deriv = 0
    
    features = np.array([auc, mean_val, std_val, rms_val, max_val, min_val, mean_deriv, std_deriv])
    return features.reshape(1, -1)

print("Starting real-time classification. Press Ctrl+C to stop.")

last_prediction = None
last_prediction_time = 0
prediction_cooldown = 0.5  # Seconds between reporting same prediction

try:
    while True:
        line = ser.readline().decode('latin-1').strip()
        try:
            value = int(line)
            current_time = time.time()
            
            data_buffer.append(value)
            timestamps_buffer.append(current_time)
            
            # Check if we have enough data to make a prediction
            if len(data_buffer) >= WINDOW_SIZE:
                features = extract_features(list(data_buffer), list(timestamps_buffer))
                prediction = model.predict(features)
                max_prob = np.max(prediction)
                predicted_label = label_classes[np.argmax(prediction)]
                
                # Report prediction only if confidence is high and not repeating too fast
                if (max_prob > CONFIDENCE_THRESHOLD and 
                    (current_time - last_prediction_time > prediction_cooldown or 
                    predicted_label != last_prediction)):
                    print(f"Predicted movement: {predicted_label} (Confidence: {max_prob:.2f})")
                    last_prediction = predicted_label
                    last_prediction_time = current_time
                
                # Slide the window with overlap
                slide_amount = int(WINDOW_SIZE * (1 - OVERLAP_PERCENTAGE))
                data_buffer = deque(list(data_buffer)[slide_amount:], maxlen=WINDOW_SIZE)
                timestamps_buffer = deque(list(timestamps_buffer)[slide_amount:], maxlen=WINDOW_SIZE)

        except Exception as e:
            # Optionally, print or log the exception: print("Error:", e)
            continue

except KeyboardInterrupt:
    print("Exiting real-time classification...")
ser.close()
