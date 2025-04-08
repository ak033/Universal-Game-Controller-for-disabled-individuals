import pygame
import sys
import random
import serial
import time
import numpy as np
import tensorflow as tf
from collections import deque

import gameUI 

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
pygame.display.set_caption("Dino Game with EMG Control")

game_font = pygame.font.Font(None, 24)

# Load the trained model and setup classification
model = tf.keras.models.load_model("emg_classifier.h5")
label_classes = ['clench', 'index', 'rest']

# Parameters for the sliding window
WINDOW_SIZE = 200
OVERLAP_PERCENTAGE = 0.5
CONFIDENCE_THRESHOLD = 0.6

data_buffer = deque(maxlen=WINDOW_SIZE)
timestamps_buffer = deque(maxlen=WINDOW_SIZE)

# Open serial connection (adjust port if necessary)
ser = serial.Serial('COM4', 9600)
ser.flushInput()
time.sleep(0.5)

# Existing game classes remain the same as in the original gameUI.py
# [... Paste all the existing class definitions for Cloud, Dino, Cactus, Ptero ...]

# Variables
game_speed = 7
jump_count = 10
player_score = 0
game_over = False
obstacle_timer = 0
obstacle_spawn = False
obstacle_cooldown = 1000

# Surfaces and other initializations remain the same
# [... Paste all existing surface and initialization code ...]

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

def end_game():
    # [... Paste the existing end_game function from the original script ...]
    pass

# Main game loop with classification integration
while True:
    try:
        # Read and process serial data for classification
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
                
                # Control dinosaur based on classification
                if predicted_label == 'clench' and max_prob > CONFIDENCE_THRESHOLD:
                    gameUI.dinosaur.jump()
                elif predicted_label == 'wrist' and max_prob > CONFIDENCE_THRESHOLD:
                    gameUI.dinosaur.duck()
                
                # Slide the window with overlap
                slide_amount = int(WINDOW_SIZE * (1 - OVERLAP_PERCENTAGE))
                data_buffer = deque(list(data_buffer)[slide_amount:], maxlen=WINDOW_SIZE)
                timestamps_buffer = deque(list(timestamps_buffer)[slide_amount:], maxlen=WINDOW_SIZE)

        except Exception as e:
            # Silently continue if there's an error parsing serial data
            pass

    except KeyboardInterrupt:
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == gameUI.CLOUD_EVENT:
            current_cloud_y = random.randint(50, 300)
            current_cloud = gameUI.Cloud(gameUI.cloud, 1380, current_cloud_y)
            gameUI.cloud_group.add(current_cloud)

    screen.fill("white")

    # Existing game logic remains the same
    # [... Paste the rest of the game logic from the original script ...]

    clock.tick(120)
    pygame.display.update()

ser.close()
pygame.quit()
sys.exit()
