# backend/app.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import psutil
import time

app = Flask(__name__)
CORS(app)

CACHE = {
    'cpu_usage': None,
    'memory_usage': None,
    'disk_usage': None,
    'network_usage': None,
    'last_updated': 0
}

CACHE_EXPIRY_TIME = 10

def is_cache_expired():
    return time.time() - CACHE['last_updated'] > CACHE_EXPIRY_TIME

def refresh_cache():
    if is_cache_expired():
        CACHE['cpu_usage'] = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        CACHE['memory_usage'] = {
            'total_memory': memory_info.total,
            'used_memory': memory_info.used,
            'free_memory': memory_info.available,
            'memory_percentage': memory_info.percent
        }

        disk_info = psutil.disk_usage('/')
        CACHE['disk_usage'] = {
            'total_disk_space': disk_info.total,
            'used_disk_space': disk_info.used,
            'free_disk_space': disk_info.free,
            'disk_percentage': disk_info.percent
        }

        net_info = psutil.net_io_counters()
        CACHE['network_usage'] = {
            'bytes_sent': net_info.bytes_sent,
            'bytes_received': net_info.bytes_recv,
            'packets_sent': net_info.packets_sent,
            'packets_received': net_info.packets_recv
        }

        CACHE['last_updated'] = time.time()

import json
from flask import send_from_directory

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        with open('alerts.json', 'r') as f:
            alerts = json.load(f)
        return jsonify(alerts), 200
    except FileNotFoundError:
        return jsonify([]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cpu', methods=['GET'])
def get_cpu_usage():
    try:
        refresh_cache()
        return jsonify({'cpu_usage': CACHE['cpu_usage']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory', methods=['GET'])
def get_memory_usage():
    try:
        refresh_cache()
        return jsonify(CACHE['memory_usage']), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/disk', methods=['GET'])
def get_disk_usage():
    try:
        refresh_cache()
        return jsonify(CACHE['disk_usage']), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/network', methods=['GET'])
def get_network_usage():
    try:
        refresh_cache()
        return jsonify(CACHE['network_usage']), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "API is running"}), 200

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
