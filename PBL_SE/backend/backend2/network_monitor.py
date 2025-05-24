import psutil
import time
import os

def get_size(bytes):
    """Convert bytes to a human-readable format (e.g., KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor_network(interval=1):
    print("Starting network monitor... Press Ctrl+C to stop.\n")
    old_data = psutil.net_io_counters()

    try:
        while True:
            time.sleep(interval)
            new_data = psutil.net_io_counters()
            bytes_sent = new_data.bytes_sent - old_data.bytes_sent
            bytes_recv = new_data.bytes_recv - old_data.bytes_recv

            upload_speed = get_size(bytes_sent / interval)
            download_speed = get_size(bytes_recv / interval)
            total_sent = get_size(new_data.bytes_sent)
            total_recv = get_size(new_data.bytes_recv)

            clear_console()
            print("Real-Time Network Monitor")
            print("=========================")
            print(f"Upload Speed     : {upload_speed}/s")
            print(f"Download Speed   : {download_speed}/s")
            print(f"Total Uploaded   : {total_sent}")
            print(f"Total Downloaded : {total_recv}")
            
            old_data = new_data

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    monitor_network()
