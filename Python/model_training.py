"""
model_training.py

This script loads features.csv (with enhanced features),
encodes the movement labels,
trains a neural network classifier using TensorFlow/Keras, and saves the model.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf

keras = tf.keras

# Load features dataset (ensure features.csv has the new feature columns)
data = pd.read_csv("features.csv")
# Use the enhanced feature set: auc, mean, std, rms, max, min, mean_deriv, std_deriv
feature_columns = ["auc", "mean", "std", "rms", "max", "min", "mean_deriv", "std_deriv"]
X = data[feature_columns].values
labels = data["label"].values
print("Labels:", labels)

# Encode string labels to integers
le = LabelEncoder()
y_encoded = le.fit_transform(labels)
num_classes = len(le.classes_)
y = keras.utils.to_categorical(y_encoded, num_classes)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define a neural network model
model = keras.models.Sequential([
    keras.layers.Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(num_classes, activation='softmax')  # Output layer: softmax gives probabilities
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=150, batch_size=4, validation_data=(X_test, y_test))

# Save the trained model
model.save("emg_classifier.h5")
print("Trained classes:", le.classes_)
print("Model saved as emg_classifier.h5")
