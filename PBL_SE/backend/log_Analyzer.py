import customtkinter as ctk
import tkinter.filedialog as fd
from tkinter import messagebox
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
import psutil  # For system monitoring
import time
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SystemMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("System Monitor & Log Analyzer")
        self.geometry("1000x700")

        # System monitoring variables
        self.monitoring = False
        self.log_lines = []
        self.update_interval = 2  # seconds

        # Create main container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # Monitoring controls frame
        self.control_frame = ctk.CTkFrame(self.container)
        self.control_frame.pack(fill="x", pady=5)

        self.start_button = ctk.CTkButton(
            self.control_frame, 
            text="Start Monitoring", 
            command=self.start_monitoring
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(
            self.control_frame, 
            text="Stop Monitoring", 
            command=self.stop_monitoring,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        # Metrics display frame
        self.metrics_frame = ctk.CTkFrame(self.container)
        self.metrics_frame.pack(fill="x", pady=5)

        self.cpu_label = ctk.CTkLabel(self.metrics_frame, text="CPU: --%")
        self.cpu_label.pack(side="left", padx=10)

        self.mem_label = ctk.CTkLabel(self.metrics_frame, text="Memory: --%")
        self.mem_label.pack(side="left", padx=10)

        self.disk_label = ctk.CTkLabel(self.metrics_frame, text="Disk: --%")
        self.disk_label.pack(side="left", padx=10)

        # Log analysis components
        self.search_entry = ctk.CTkEntry(
            self.container, 
            placeholder_text="Search system logs..."
        )
        self.search_entry.pack(fill="x", pady=5)

        self.search_button = ctk.CTkButton(
            self.container, 
            text="Search Logs", 
            command=self.search_logs
        )
        self.search_button.pack(pady=5)

        # Output display
        self.output_box = ctk.CTkTextbox(self.container, wrap="word")
        self.output_box.pack(fill="both", expand=True, pady=10)

        # Visualization buttons
        self.chart_frame = ctk.CTkFrame(self.container)
        self.chart_frame.pack(fill="x", pady=5)

        self.cpu_chart_button = ctk.CTkButton(
            self.chart_frame,
            text="Show CPU History",
            command=lambda: self.show_chart("CPU")
        )
        self.cpu_chart_button.pack(side="left", padx=5)

        self.mem_chart_button = ctk.CTkButton(
            self.chart_frame,
            text="Show Memory History",
            command=lambda: self.show_chart("Memory")
        )
        self.mem_chart_button.pack(side="left", padx=5)

    def get_system_metrics(self):
        """Collect current system metrics"""
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, mem, disk

    def update_metrics_display(self, cpu, mem, disk):
        """Update the metrics display labels"""
        self.cpu_label.configure(text=f"CPU: {cpu}%")
        self.mem_label.configure(text=f"Memory: {mem}%")
        self.disk_label.configure(text=f"Disk: {disk}%")

    def log_metrics(self, cpu, mem, disk):
        """Log metrics with timestamp"""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_entry = f"{timestamp} CPU: {cpu}% | Memory: {mem}% | Disk: {disk}%"
        self.log_lines.append(log_entry)
        self.output_box.insert("end", log_entry + "\n")
        self.output_box.see("end")  # Auto-scroll to bottom

    def monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            cpu, mem, disk = self.get_system_metrics()
            self.update_metrics_display(cpu, mem, disk)
            self.log_metrics(cpu, mem, disk)
            time.sleep(self.update_interval)

    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.log_lines = []
        
        # Start monitoring in a separate thread
        self.monitor_thread = threading.Thread(
            target=self.monitoring_loop, 
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.output_box.insert("end", "\nMonitoring stopped\n")

    def search_logs(self):
        """Search logged metrics"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            return

        self.output_box.delete("1.0", "end")
        found = False
        
        for line in self.log_lines:
            if keyword in line.lower():
                self.output_box.insert("end", line + "\n")
                found = True
                
        if not found:
            self.output_box.insert("end", f"No entries found for '{keyword}'")

    def show_chart(self, metric_type):
        """Show historical chart for selected metric"""
        if not self.log_lines:
            messagebox.showwarning("No Data", "No monitoring data available")
            return

        timestamps = []
        values = []
        
        for line in self.log_lines:
            try:
                # Extract timestamp
                ts_str = line.split("]")[0] + "]"
                timestamp = datetime.strptime(ts_str, "[%Y-%m-%d %H:%M:%S]")
                timestamps.append(timestamp)
                
                # Extract metric value
                if metric_type == "CPU":
                    value = float(line.split("CPU: ")[1].split("%")[0])
                elif metric_type == "Memory":
                    value = float(line.split("Memory: ")[1].split("%")[0])
                values.append(value)
            except Exception as e:
                continue

        if not timestamps:
            messagebox.showerror("Error", "Could not parse log data")
            return

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, values, marker='o')
        plt.title(f"{metric_type} Usage Over Time")
        plt.xlabel("Time")
        plt.ylabel(f"{metric_type} Usage (%)")
        plt.grid(True)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()
