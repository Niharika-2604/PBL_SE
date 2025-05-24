import re
from datetime import datetime

# Keywords or patterns to look for
SUSPICIOUS_PATTERNS = [
    r'Failed password',         # Common SSH brute-force failure
    r'authentication failure',  # PAM/SSH login issue
    r'Invalid user',            # Attempt to log in with a non-existent user
    r'root login',              # Root login attempt
    r'sudo:',                   # Use of sudo
    r'error',                   # General error
    r'command not found',       # Attempt to run invalid commands
    r'segmentation fault',      # App crash
]

def analyze_log(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
            print(f"\nAnalyzing log file: {file_path}\n{'='*60}")
            line_count = 0
            suspicious_count = 0

            for line in log_file:
                line_count += 1
                for pattern in SUSPICIOUS_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        suspicious_count += 1
                        print(f"[Suspicious] Line {line_count}: {line.strip()}")
                        break

            print(f"\nTotal Lines Scanned     : {line_count}")
            print(f"Suspicious Entries Found: {suspicious_count}")
            print("Analysis Completed.\n")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
from flask import Blueprint, jsonify

log_analyzer = Blueprint('log_analyzer', __name__)

@log_analyzer.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        with open('system_logs.log', 'r') as f:
            lines = f.readlines()
        return jsonify({"logs": lines[-100:]}), 200  # last 100 entries
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple Log File Analyzer")
    parser.add_argument("logfile", help="Path to the log file (e.g., /var/log/auth.log or system.log)")

    args = parser.parse_args()
    analyze_log(args.logfile)
