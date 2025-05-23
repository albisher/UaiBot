# System & Platform Health Checks

This document describes the health check scripts for system and platform information in UaiBot.

## 1. System Information Health Check

**Script:** `app/health_check/system_info_health_check.py`

- Prints general system information: OS, version, platform, machine, processor, Python version, shell, current working directory, and environment (Docker, WSL, VM, etc.).
- **How to run:**
  ```bash
  python3 app/health_check/system_info_health_check.py
  ```
- **Output:** JSON with all detected system info.

## 2. Platform-Specific Health Check

**Script:** `app/health_check/platform_health_check.py`

- Prints platform-specific details:
  - **macOS:** Version and model
  - **Windows:** Edition and version
  - **Linux:** Distro and model (e.g., Raspberry Pi)
- **How to run:**
  ```bash
  python3 app/health_check/platform_health_check.py
  ```
- **Output:** Platform-specific info for your OS.

## 3. Usage & Integration

- Use these scripts to quickly diagnose the environment UaiBot is running on.
- Integrate them into automated health checks or troubleshooting workflows.

## 4. Extending

- Add more platform-specific checks as needed (e.g., Jetson, WSL, Docker, VM details).
- Keep scripts modular and well-documented. 