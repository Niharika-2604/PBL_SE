from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import psutil
import time
import logging
from datetime import datetime
import json
import random
import pickle
import os
from collections import defaultdict
from rl_scheduler import rl_scheduler_step
from rl_scheduler import get_current_state 


app = Flask(__name__)
CORS(app)

# -------------------- Logging Setup --------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# -------------------- Monitoring System Cache --------------------
CACHE = {
    'cpu_usage': None,
    'memory_usage': None,
    'disk_usage': None,
    'network_usage': None,
    'last_updated': 0
}
APP_START_TIME = time.time()
CACHE_EXPIRY_TIME = 10  # seconds

def is_cache_expired():
    return time.time() - CACHE['last_updated'] > CACHE_EXPIRY_TIME

def refresh_cache(force=False):
    if is_cache_expired() or force:
        logging.info("Refreshing system data cache.")
        try:
            CACHE['cpu_usage'] = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            CACHE['memory_usage'] = {
                'total': mem.total,
                'used': mem.used,
                'available': mem.available,
                'percent': mem.percent
            }

            disk = psutil.disk_usage('/')
            CACHE['disk_usage'] = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }

            net = psutil.net_io_counters()
            CACHE['network_usage'] = {
                'bytes_sent': net.bytes_sent,
                'bytes_recv': net.bytes_recv,
                'packets_sent': net.packets_sent,
                'packets_recv': net.packets_recv
            }

            CACHE['last_updated'] = time.time()
        except Exception as e:
            logging.error(f"Error refreshing cache: {e}")
            raise

def get_uptime():
    return int(time.time() - APP_START_TIME)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Advanced System Monitoring API"}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "OK",
        "uptime_seconds": get_uptime(),
        "last_cache_refresh": datetime.utcfromtimestamp(CACHE['last_updated']).isoformat() + "Z"
    }), 200

@app.route('/api/cpu', methods=['GET'])
def get_cpu_usage():
    try:
        refresh_cache(force=request.args.get('refresh') == '1')
        return jsonify({'cpu_usage': CACHE['cpu_usage']}), 200
    except Exception as e:
        return jsonify({'error': f"Failed to get CPU usage: {str(e)}"}), 500

@app.route('/api/memory', methods=['GET'])
def get_memory_usage():
    try:
        refresh_cache(force=request.args.get('refresh') == '1')
        return jsonify(CACHE['memory_usage']), 200
    except Exception as e:
        return jsonify({'error': f"Failed to get memory usage: {str(e)}"}), 500

@app.route('/api/disk', methods=['GET'])
def get_disk_usage():
    try:
        refresh_cache(force=request.args.get('refresh') == '1')
        return jsonify(CACHE['disk_usage']), 200
    except Exception as e:
        return jsonify({'error': f"Failed to get disk usage: {str(e)}"}), 500

@app.route('/api/network', methods=['GET'])
def get_network_usage():
    try:
        refresh_cache(force=request.args.get('refresh') == '1')
        return jsonify(CACHE['network_usage']), 200
    except Exception as e:
        return jsonify({'error': f"Failed to get network usage: {str(e)}"}), 500

@app.route('/api/system_snapshot', methods=['GET'])
def get_full_snapshot():
    try:
        refresh_cache(force=request.args.get('refresh') == '1')
        return jsonify({
            'cpu_usage': CACHE['cpu_usage'],
            'memory_usage': CACHE['memory_usage'],
            'disk_usage': CACHE['disk_usage'],
            'network_usage': CACHE['network_usage'],
            'uptime_seconds': get_uptime()
        }), 200
    except Exception as e:
        return jsonify({'error': f"Failed to get system snapshot: {str(e)}"}), 500

# -------------------- Alerts --------------------
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

@app.route('/api/alerts/log', methods=['GET'])
def download_alert_log():
    try:
        with open('alerts.json', 'r') as f:
            alerts = json.load(f)
        with open('alerts.log', 'w') as f:
            for alert in alerts:
                f.write(f"[{alert['timestamp']}] [{alert['level'].upper()}] {alert['message']}\n")
        return send_file('alerts.log', as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------- RL Scheduler --------------------

Q_TABLE_FILE = "q_table.pkl"
CPU_STATES = ['low', 'medium', 'high']
MEMORY_STATES = ['low', 'medium', 'high']
ACTIONS = ['schedule_task', 'skip_task']
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1

def default_action_values():
    return {action: 0.0 for action in ACTIONS}

Q_TABLE = defaultdict(default_action_values)

if os.path.exists(Q_TABLE_FILE):
    try:
        with open(Q_TABLE_FILE, "rb") as f:
            loaded_q = pickle.load(f)
            Q_TABLE.update(loaded_q)
            logging.info("Q-table loaded successfully.")
    except (EOFError, pickle.UnpicklingError):
        logging.warning("Q-table was empty or corrupted. Starting fresh...")

def get_rl_state():
    cpu = CACHE.get('cpu_usage', 0)
    mem_percent = CACHE.get('memory_usage', {}).get('percent', 0)

    cpu_state = 'low' if cpu < 40 else 'medium' if cpu < 75 else 'high'
    mem_state = 'low' if mem_percent < 40 else 'medium' if mem_percent < 75 else 'high'

    return (cpu_state, mem_state)

def choose_action(state):
    if random.random() < EPSILON:
        return random.choice(ACTIONS)
    return max(Q_TABLE[state], key=Q_TABLE[state].get)

def get_reward(state, action):
    cpu, mem = state
    if action == 'schedule_task':
        if cpu == 'low' and mem == 'low':
            return 5
        elif cpu == 'medium' or mem == 'medium':
            return 2
        else:
            return -5
    else:
        if cpu == 'high' or mem == 'high':
            return 4
        else:
            return -2

@app.route("/scheduler/status", methods=["GET"])
def scheduler_status():
    try:
        refresh_cache()
        state = get_rl_state()
        action = choose_action(state)
        reward = get_reward(state, action)
        next_state = get_rl_state()
        next_max_q = max(Q_TABLE[next_state].values())

        Q_TABLE[state][action] += ALPHA * (reward + GAMMA * next_max_q - Q_TABLE[state][action])

        with open(Q_TABLE_FILE, "wb") as f:
            pickle.dump(dict(Q_TABLE), f)

        return jsonify({
            "state": state,
            "action": action,
            "reward": reward,
            "updated_q_value": Q_TABLE[state][action]
        }), 200
    except Exception as e:
        return jsonify({'error': f"Failed to run scheduler: {str(e)}"}), 500
    
@app.route('/api/scheduler/step', methods=['GET'])
def scheduler_step():
    try:
        result = rl_scheduler_step()
        return jsonify({
            'message': 'RL decision executed',
            'state': result['state'],
            'action': result['action'],
            'reward': result['reward'],
            'updated_q_value': result['updated_q_value']
        }), 200
    except Exception as e:
        logging.error(f"RL Scheduler failed: {e}")
        return jsonify({'error': 'RL Scheduler failed', 'details': str(e)}), 500

from flask import Flask, jsonify
from rl_scheduler import rl_scheduler_step  # Import the RL step
from rl_scheduler import get_current_state  # Import the function to get the current state

app = Flask(__name__)

@app.route('/api/rl/current_state', methods=['GET'])
def get_current_rl_state():
    try:
        state = get_current_state()  # Get the current state (CPU and Memory usage)
        return jsonify({
            'cpu_usage': state[0],
            'memory_usage': state[1]
        }), 200
    except Exception as e:
        return jsonify({'error': f"Failed to get current state: {str(e)}"}), 500


@app.route('/api/rl/train', methods=['GET'])
@app.route('/api/rl/train', methods=['GET'])
def train_rl_agent():
    print("Training RL agent...")
    return jsonify({"message": "RL training completed."}), 200


if __name__ == "__main__":
    app.run(debug=True)


# -------------------- Main Entry --------------------
if __name__ == '__main__':
    logging.info("Starting System Monitoring API Server with Scheduler...")
    app.run(debug=True, host='0.0.0.0', port=5000)
