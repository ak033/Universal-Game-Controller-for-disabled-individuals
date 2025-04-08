# Universal-Game-Controller-for-Disabled-Individuals

## AI model

For prototyping purposes we decided to use a simple classification neural network with 2 hidden layers. 


## Data Flow Summary

Collect raw EMG data → CSV files via data_collection.py

Preprocess → single features.csv via data_preprocessing.py

Train → saved Keras model via model_training.py

Deploy → live predictions via real_time_classification.py
