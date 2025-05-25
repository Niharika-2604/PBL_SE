#include <windows.h>
#include <psapi.h>
#include <iostream>
#include <iomanip>

void getMemoryUsage() {
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(memInfo);
    GlobalMemoryStatusEx(&memInfo);

    DWORDLONG totalPhysMem = memInfo.ullTotalPhys;
    DWORDLONG physMemUsed = memInfo.ullTotalPhys - memInfo.ullAvailPhys;

    std::cout << "Memory Usage:\n";
    std::cout << "  Total Physical Memory: " << totalPhysMem / (1024 * 1024) << " MB\n";
    std::cout << "  Used Physical Memory : " << physMemUsed / (1024 * 1024) << " MB\n";
    std::cout << "  Memory Usage Percent : " << memInfo.dwMemoryLoad << " %\n";
}

double calculateCpuUsage() {
    FILETIME idleTime, kernelTime, userTime;
    static FILETIME prevIdleTime = {0}, prevKernelTime = {0}, prevUserTime = {0};

    GetSystemTimes(&idleTime, &kernelTime, &userTime);

    ULONGLONG idle = (ULONGLONG)idleTime.dwLowDateTime | ((ULONGLONG)idleTime.dwHighDateTime << 32);
    ULONGLONG kernel = (ULONGLONG)kernelTime.dwLowDateTime | ((ULONGLONG)kernelTime.dwHighDateTime << 32);
    ULONGLONG user = (ULONGLONG)userTime.dwLowDateTime | ((ULONGLONG)userTime.dwHighDateTime << 32);

    ULONGLONG prevIdle = (ULONGLONG)prevIdleTime.dwLowDateTime | ((ULONGLONG)prevIdleTime.dwHighDateTime << 32);
    ULONGLONG prevKernel = (ULONGLONG)prevKernelTime.dwLowDateTime | ((ULONGLONG)prevKernelTime.dwHighDateTime << 32);
    ULONGLONG prevUser = (ULONGLONG)prevUserTime.dwLowDateTime | ((ULONGLONG)prevUserTime.dwHighDateTime << 32);

    ULONGLONG totalSys = (kernel + user) - (prevKernel + prevUser);
    ULONGLONG totalIdle = idle - prevIdle;

    prevIdleTime = idleTime;
    prevKernelTime = kernelTime;
    prevUserTime = userTime;

    if (totalSys == 0) return 0.0;

    return (100.0 * (totalSys - totalIdle)) / totalSys;
}

int main() {
    std::cout << std::fixed << std::setprecision(2);

    for (int i = 0; i < 10; ++i) {
        system("cls");
        std::cout << "System Resource Monitor\n========================\n";

        getMemoryUsage();

        double cpuUsage = calculateCpuUsage();
        std::cout << "\nCPU Usage: " << cpuUsage << " %\n";

        Sleep(1000);  // Wait 1 second
    }

    return 0;
}
