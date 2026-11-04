from modules.device_manager import (
    list_adb_devices,
    get_all_known_devices,
    select_moc_device,
    get_device_info
)
from modules.adb_connection import auto_connect
from modules.user_inputs import ask_connection_mode, collect_user_call_settings
from modules.call_loop import run_call_loop

def main():

    # 1. Ask connection mode FIRST
    connection_mode = ask_connection_mode()

    # 2. Build device list based on connection mode
    if connection_mode == "usb":
        devices = list_adb_devices()
        if not devices:
            print("[ERROR] No USB devices detected. Connect cable and try again.")
            return
    else:
        # TCP/IP mode → list ALL devices from DEVICE_MAP
        devices = get_all_known_devices()

    # 3. Select MOC device from the list
    moc_device = select_moc_device(devices)

    # 4. Get device info (name + IP)
    info = get_device_info(moc_device)

    # 5. Connect based on mode
    if connection_mode == "tcpip":
        moc_device = auto_connect(moc_device, info["ip"])
    else:
        print("[ADB] Using USB cable connection")

    # 6. Ask remaining call settings
    settings = collect_user_call_settings()

    # 7. Run call loop
    print("\n--- STARTING CALL LOOP ---")
    run_call_loop(moc_device, settings)

if __name__ == "__main__":
    main()
