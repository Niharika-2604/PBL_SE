import psutil
import numpy as np
from time import sleep
import logging
import argparse
import os
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Configurations
INTERVAL = 10  # Monitor interval in seconds
LOG_FILE = 'system_monitor.log'
MODEL_FILE = 'anomaly_detection_model.pkl'
TRAINING_DATA_FILE = 'training_data.npy'

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the Anomaly Detection Model
def collect_metrics():
    """Collect system metrics like CPU, memory, and disk usage."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, memory, disk
    except Exception as e:
        logging.error(f"Error collecting system metrics: {e}")
        return None, None, None

def load_model():
    """Load the pre-trained anomaly detection model."""
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, 'rb') as file:
            model = pickle.load(file)
            logging.info("Model loaded successfully.")
            return model
    else:
        logging.info("No model found. You can train a model first using training data.")
        return None

def save_model(model):
    """Save the trained anomaly detection model."""
    with open(MODEL_FILE, 'wb') as file:
        pickle.dump(model, file)
        logging.info("Model saved successfully.")

def train_model():
    """Train a new anomaly detection model using system metrics."""
    # Collect some training data (for demonstration purposes, we'll collect 100 samples)
    training_data = []
    for _ in range(100):
        metrics = collect_metrics()
        if None in metrics:
            continue
        training_data.append(metrics)
        sleep(INTERVAL)

    # Convert collected data to a NumPy array and scale it
    training_data = np.array(training_data)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(training_data)

    # Train an Isolation Forest model
    model = IsolationForest(contamination=0.1)  # Adjust contamination as per the expected anomaly rate
    model.fit(scaled_data)

    # Save the trained model
    save_model(model)
    return model

def is_anomalous(model, metrics):
    """Detect if the collected metrics are anomalous using the trained model."""
    # Standardize the metrics before passing to the model
    scaler = StandardScaler()
    scaled_metrics = scaler.fit_transform([metrics])

    # Predict if the metrics are anomalous
    prediction = model.predict(scaled_metrics)
    # The model returns 1 for normal and -1 for anomaly
    if prediction[0] == -1:
        return True
    return False
import json
from datetime import datetime

ALERT_FILE = 'alerts.json'

import json
from datetime import datetime

ALERT_FILE = 'alerts.json'

def save_alert(level, message):
    try:
        with open(ALERT_FILE, 'r') as f:
            alerts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        alerts = []

    alerts.append({
        "level": level,
        "message": message,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    with open(ALERT_FILE, 'w') as f:
        json.dump(alerts[-100:], f, indent=2)  # Keep last 100 alerts


def monitor():
    model = load_model()
    print("[*] Starting anomaly detector... (Ctrl+C to stop)")

    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            metrics = [cpu, mem, disk]

            if is_anomalous(model, metrics):
                alert_msg = f"Anomaly detected! CPU={cpu:.2f}%, MEM={mem:.2f}%, DISK={disk:.2f}%"
                logging.warning(alert_msg)
                print(f"[ALERT] {alert_msg}")
                save_alert('critical', alert_msg)
            else:
                print(f"[OK] CPU={cpu:.2f}% MEM={mem:.2f}% DISK={disk:.2f}%")

            sleep(10)
    except KeyboardInterrupt:
        print("\n[+] Monitoring stopped by user.")
        logging.info("Monitoring stopped.")


if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="System Anomaly Detector")
    parser.add_argument('--monitor', action='store_true', help="Start monitoring system metrics for anomalies")
    parser.add_argument('--train', action='store_true', help="Train a new anomaly detection model")
    args = parser.parse_args()

    if args.train:
        print("[*] Training new anomaly detection model...")
        train_model()
    elif args.monitor:
        monitor()
