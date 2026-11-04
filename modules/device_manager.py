import subprocess
import sys

# ---------------------------------------------------------
# DEVICE MAP: SERIAL → { name, ip }
# ---------------------------------------------------------
DEVICE_MAP = {
    "AQKSLVH002M41300717": {"name": "Nokia X20", "ip": None},
    "ASCARLH009M82400286": {"name": "Nokia X10", "ip": "100.75.16.57"}
}

def get_all_known_devices():
    return list(DEVICE_MAP.keys())

def run_adb_command(cmd):
    """Run an ADB command and return output as string."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"[ERROR] Failed to run ADB command: {e}")
        return ""

def list_adb_devices():
    """Return a list of connected ADB device serials."""
    output = run_adb_command("adb devices")

    devices = []
    for line in output.splitlines():
        if "\tdevice" in line:
            serial = line.split("\t")[0].strip()
            devices.append(serial)

    return devices


def get_device_info(serial):
    """Return device info dict or fallback."""
    if serial in DEVICE_MAP:
        return DEVICE_MAP[serial]
    return {
        "name": f"Unknown Device ({serial})",
        "ip": None
    }


def select_device(devices):
    """Let user select a device from the list."""
    if not devices:
        print("[ERROR] No devices detected via ADB")
        sys.exit(1)

    if len(devices) == 1:
        serial = devices[0]
        info = get_device_info(serial)
        print(f"[INFO] Using the only connected device: {info['name']}")
        return serial

    print("\nConnected devices:")
    for idx, serial in enumerate(devices, start=1):
        info = get_device_info(serial)
        print(f"  {idx}. {info['name']}  [{serial}]")

    while True:
        choice = input("\nSelect device number: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(devices):
                return devices[choice - 1]
        print("Invalid selection. Try again.")


def get_selected_device():
    """Main entry: detect devices and return selected serial."""
    devices = list_adb_devices()
    selected = select_device(devices)
    info = get_device_info(selected)
    print(f"[INFO] Selected: {info['name']} ({selected})")
    return selected

def select_moc_device(devices):
    """Ask user which device will be used for MOC (outgoing call)."""
    print("\nWhich device will be used for MOC (outgoing call)?")

    for idx, serial in enumerate(devices, start=1):
        info = get_device_info(serial)
        print(f"  {idx}. {info['name']}  [{serial}]")

    while True:
        choice = input("\nSelect MOC device number: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(devices):
                selected_serial = devices[choice - 1]
                info = get_device_info(selected_serial)
                print(f"[INFO] MOC device selected: {info['name']} ({selected_serial})")
                return selected_serial

        print("Invalid selection. Try again.")

def select_sim_slot():
    """Ask user which SIM slot to use (SIM1 or SIM2)."""
    print("\nSelect SIM slot for this device:")
    print("  1. SIM1")
    print("  2. SIM2")

    while True:
        choice = input("\nSelect SIM slot number: ").strip()
        if choice == "1":
            print("[INFO] SIM1 selected (phoneId = 0)")
            return 0
        elif choice == "2":
            print("[INFO] SIM2 selected (phoneId = 1)")
            return 1
        else:
            print("Invalid selection. Try again.")
