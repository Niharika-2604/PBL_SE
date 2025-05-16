import argparse
import logging
import os
import platform
import psutil
import subprocess
from time import sleep
from plyer import notification
from playsound import playsound

# ========== CONFIG ==========

LOG_FILE = 'system_alerts.log'
ALERT_SOUND = 'alert.mp3'  # Use a short alert sound, e.g., in same dir

# ========== LOGGING SETUP ==========

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ========== NOTIFY USER ==========

def notify_user(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=10  # seconds
        )
        logging.info(f"Notification sent: {title} - {message}")
    except Exception as e:
        logging.error(f"Notification failed: {e}")

# ========== SOUND ALERT ==========

def play_alert_sound():
    try:
        playsound(ALERT_SOUND)
        logging.info("Played alert sound.")
    except Exception as e:
        logging.error(f"Sound alert failed: {e}")

# ========== SYSTEM MONITORING ==========

def monitor_system(thresholds):
    alerts = []

    cpu = psutil.cpu_percent(interval=1)
    if cpu > thresholds['cpu']:
        alerts.append(f"⚠️ High CPU Usage: {cpu:.2f}%")

    memory = psutil.virtual_memory().percent
    if memory > thresholds['memory']:
        alerts.append(f"⚠️ High Memory Usage: {memory:.2f}%")

    disk = psutil.disk_usage('/').percent
    if disk > thresholds['disk']:
        alerts.append(f"⚠️ High Disk Usage: {disk:.2f}%")

    return alerts

# ========== MAIN LOOP ==========

def run_monitor(thresholds, interval):
    while True:
        alerts = monitor_system(thresholds)
        if alerts:
            for msg in alerts:
                notify_user("System Alert", msg)
            play_alert_sound()
        sleep(interval)

# ========== CLI PARSER ==========
from flask import Flask, jsonify
import json

app = Flask(__name__)

# Simulated alert data store (could be replaced with a database or log file)
ALERT_LOG = "alerts.json"

def load_alerts():
    try:
        with open(ALERT_LOG, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    alerts = load_alerts()
    return jsonify(alerts), 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="🔍 System Resource Monitor")
    parser.add_argument('--cpu', type=int, default=80, help="CPU threshold %")
    parser.add_argument('--memory', type=int, default=80, help="Memory threshold %")
    parser.add_argument('--disk', type=int, default=90, help="Disk threshold %")
    parser.add_argument('--interval', type=int, default=60, help="Check interval in seconds")
    args = parser.parse_args()

    thresholds = {
        'cpu': args.cpu,
        'memory': args.memory,
        'disk': args.disk
    }

    logging.info("✅ System-only Alert Manager started.")
    run_monitor(thresholds, args.interval)
