import subprocess
import time
from .mattermost_client import notify_mattermost
from .logging_utils import log_event

def adb(cmd):
    full_cmd = ["adb"] + cmd.split()
    return subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def ensure_adb_connection():
    retry_count = 0
    retry_schedule = [60, 300, 1800]

    while True:
        result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode(errors="ignore").strip().splitlines()
        device_lines = [line for line in output[1:] if line.strip()]

        if not device_lines:
            msg = "⚠️ ADB ERROR: No device detected."
            print(msg)
            notify_mattermost(msg)
            log_event("adb_error", "N/A", "N/A", "No device detected")
        else:
            serial, status = device_lines[0].split()
            if status == "unauthorized":
                msg = "⚠️ ADB ERROR: Device unauthorized."
                print(msg)
                notify_mattermost(msg)
                log_event("adb_error", "N/A", "N/A", "Unauthorized")
            elif status != "device":
                msg = f"⚠️ ADB ERROR: Unexpected state: {status}"
                print(msg)
                notify_mattermost(msg)
                log_event("adb_error", "N/A", "N/A", status)
            else:
                if retry_count > 0:
                    notify_mattermost("✅ ADB connection restored.")
                print("[ADB] Connection OK.")
                return

        delay = retry_schedule[min(retry_count, len(retry_schedule) - 1)]
        retry_count += 1
        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)

