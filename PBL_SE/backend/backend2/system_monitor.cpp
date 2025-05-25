#include <iostream>
#include <vector>
#include <windows.h>
#include <tlhelp32.h>
#include <psapi.h>

class ProcessMonitor {
public:
    void listProcesses() {
        HANDLE hProcessSnap;
        PROCESSENTRY32 pe32;

        hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (hProcessSnap == INVALID_HANDLE_VALUE) {
            std::cerr << "Failed to take snapshot of processes." << std::endl;
            return;
        }

        pe32.dwSize = sizeof(PROCESSENTRY32);
        if (!Process32First(hProcessSnap, &pe32)) {
            std::cerr << "Failed to retrieve process information." << std::endl;
            CloseHandle(hProcessSnap);
            return;
        }

        do {
            std::wcout << L"Process Name: " << pe32.szExeFile
                       << L" | PID: " << pe32.th32ProcessID
                       << L" | Parent PID: " << pe32.th32ParentProcessID;

            // Try opening the process to get memory info
            HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pe32.th32ProcessID);
            if (hProcess) {
                PROCESS_MEMORY_COUNTERS pmc;
                if (GetProcessMemoryInfo(hProcess, &pmc, sizeof(pmc))) {
                    std::wcout << L" | Memory: " << pmc.WorkingSetSize / 1024 << L" KB";
                }
                CloseHandle(hProcess);
            }

            std::wcout << std::endl;

        } while (Process32Next(hProcessSnap, &pe32));

        CloseHandle(hProcessSnap);
    }
};

int main() {
    ProcessMonitor monitor;
    monitor.listProcesses();
    return 0;
}
