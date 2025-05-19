let autoRefreshInterval;

window.onload = function () {
  fetchAllData();
  autoRefreshInterval = setInterval(fetchAllData, 5000);

  document.getElementById('refreshBtn').addEventListener('click', () => {
    fetchAllData();
  });
};

function fetchAllData() {
  fetchCPU();
  fetchMemory();
  fetchDisk();
  fetchNetwork();
  fetchAlerts();
}

function fetchCPU() {
  fetch("http://localhost:5000/api/cpu")
    .then(res => res.json())
    .then(data => {
      const usage = data.cpu_usage;
      document.getElementById("cpuUsageText").innerText = `CPU Usage: ${usage}%`;
      document.getElementById("cpuUsageBar").style.width = usage + "%";
    })
    .catch(err => {
      document.getElementById("cpuUsageText").innerText = "Error loading CPU data";
      document.getElementById("cpuUsageBar").style.width = "0%";
    });
}

function fetchMemory() {
  fetch("http://localhost:5000/api/memory")
    .then(res => res.json())
    .then(data => {
      const percent = data.memory_percentage;
      document.getElementById("memoryUsageText").innerText =
        `Used: ${(data.used_memory / 1e9).toFixed(2)} GB / ${(data.total_memory / 1e9).toFixed(2)} GB (${percent}%)`;
      document.getElementById("memoryUsageBar").style.width = percent + "%";
    })
    .catch(err => {
      document.getElementById("memoryUsageText").innerText = "Error loading Memory data";
      document.getElementById("memoryUsageBar").style.width = "0%";
    });
}

function fetchDisk() {
  fetch("http://localhost:5000/api/disk")
    .then(res => res.json())
    .then(data => {
      const percent = data.disk_percentage;
      document.getElementById("diskUsageText").innerText =
        `Used: ${(data.used_disk_space / 1e9).toFixed(2)} GB / ${(data.total_disk_space / 1e9).toFixed(2)} GB (${percent}%)`;
      document.getElementById("diskUsageBar").style.width = percent + "%";
    })
    .catch(err => {
      document.getElementById("diskUsageText").innerText = "Error loading Disk data";
      document.getElementById("diskUsageBar").style.width = "0%";
    });
}

function fetchNetwork() {
  fetch("http://localhost:5000/api/network")
    .then(res => res.json())
    .then(data => {
      document.getElementById("networkUsageText").innerText =
        `Sent: ${(data.bytes_sent / 1e6).toFixed(2)} MB, Received: ${(data.bytes_received / 1e6).toFixed(2)} MB`;
    })
    .catch(err => {
      document.getElementById("networkUsageText").innerText = "Error loading Network data";
    });
}

function fetchAlerts() {
  fetch("http://localhost:5000/api/alerts")
    .then(res => res.json())
    .then(data => {
      const alertsList = document.getElementById("alertsList");
      alertsList.innerHTML = "";
      if (data.length === 0) {
        alertsList.innerHTML = "<li>No alerts</li>";
        return;
      }
      data.slice().reverse().forEach(alert => {
        const li = document.createElement("li");
        li.textContent = `[${alert.timestamp}] (${alert.level.toUpperCase()}) - ${alert.message}`;
        if (alert.level.toLowerCase() === "critical") {
          li.classList.add("critical");
        }
        alertsList.appendChild(li);
      });
    })
    .catch(err => {
      const alertsList = document.getElementById("alertsList");
      alertsList.innerHTML = "<li>Error loading alerts</li>";
    });
}
