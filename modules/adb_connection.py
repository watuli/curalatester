import subprocess
import time

# ---------------------------------------------------------
# Run ADB command
# ---------------------------------------------------------
def run(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode(errors="ignore")
        return out.strip()
    except Exception:
        return ""


# ---------------------------------------------------------
# Enable TCP/IP mode on device
# ---------------------------------------------------------
def enable_tcpip(device_serial, port=5555):
    print(f"[ADB] Enabling TCP/IP mode on {device_serial}...")
    out = run(["adb", "-s", device_serial, "tcpip", str(port)])
    print(f"[ADB] {out}")
    time.sleep(1)


# ---------------------------------------------------------
# Connect to device over TCP/IP
# ---------------------------------------------------------
def connect_tcpip(ip, port=5555):
    print(f"[ADB] Connecting to {ip}:{port}...")
    out = run(["adb", "connect", f"{ip}:{port}"])
    print(f"[ADB] {out}")
    return "connected" in out.lower()


# ---------------------------------------------------------
# Disconnect TCP/IP
# ---------------------------------------------------------
def disconnect_tcpip(ip, port=5555):
    print(f"[ADB] Disconnecting {ip}:{port}...")
    run(["adb", "disconnect", f"{ip}:{port}"])


# ---------------------------------------------------------
# Verify if device is connected over TCP/IP
# ---------------------------------------------------------
def is_connected_over_tcpip(ip, port=5555):
    out = run(["adb", "devices"])
    return f"{ip}:{port}\tdevice" in out


# ---------------------------------------------------------
# Auto-connect logic
# ---------------------------------------------------------
def auto_connect(device_serial, device_ip, port=5555):
    """
    device_serial = USB serial (e.g. AQKSLVH002M41300717)
    device_ip     = IP from DEVICE_MAP (e.g. 100.75.16.57)
    """

    if not device_ip:
        print("[ADB] No IP configured for this device → USB only")
        return device_serial  # fallback to USB

    # Already connected?
    if is_connected_over_tcpip(device_ip, port):
        print(f"[ADB] Already connected over TCP/IP: {device_ip}:{port}")
        return f"{device_ip}:{port}"

    # Enable TCP/IP mode
    enable_tcpip(device_serial, port)

    # Try connecting
    if connect_tcpip(device_ip, port):
        print(f"[ADB] Connected over TCP/IP: {device_ip}:{port}")
        return f"{device_ip}:{port}"

    print("[ADB] TCP/IP connection failed → falling back to USB")
    return device_serial
