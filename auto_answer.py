#!/usr/bin/env python3
import subprocess
import time
import threading
import os
import json
import sys

# ---------------------------------------------------------
#  IMPORT MODULES FROM CURALATESTER
# ---------------------------------------------------------
MODULE_PATH = "/Users/mice/python/adb/curalatester/modules"
if MODULE_PATH not in sys.path:
    sys.path.append(MODULE_PATH)

from device_manager import (
    list_adb_devices,
    get_device_info,
    select_device,
    DEVICE_MAP
)


incoming_call_counter = 0

# ---------------------------------------------------------
#  CONNECTION MODE SELECTION
# ---------------------------------------------------------
def select_connection_mode():
    while True:
        print("\nConnection mode:")
        print("  1. USB cable")
        print("  2. TCP/IP (tailscale)")
        mode = input("Select mode: ").strip()

        if mode == "1":
            return "usb"

        if mode == "2":
            return "tcpip"

        print("Invalid selection. Try again.\n")


# ---------------------------------------------------------
#  LIST ADB DEVICES
# ---------------------------------------------------------
def list_adb_devices():
    try:
        out = subprocess.check_output(
            ["adb", "devices"],
            stderr=subprocess.STDOUT
        ).decode(errors="ignore")

        devices = []
        for line in out.splitlines():
            if "\tdevice" in line:
                serial = line.split("\t")[0].strip()
                devices.append(serial)

        return devices

    except Exception:
        return []

# ---------------------------------------------------------
#  MATTERMOST WEBHOOK SENDER
# ---------------------------------------------------------
import urllib.request

MATTERMOST_WEBHOOK_URL = "https://matter.elisa.fi/hooks/74b5texmopd1bczh45qasfzrcy"

def send_mattermost(text):
    try:
        data = json.dumps({"text": text}).encode("utf-8")
        req = urllib.request.Request(
            MATTERMOST_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"[Mattermost] Error sending message: {e}")


# ---------------------------------------------------------
#  GET FRIENDLY DEVICE NAME
# ---------------------------------------------------------
def get_device_name(serial):
    try:
        name = subprocess.check_output(
            ["adb", "-s", serial, "shell", "getprop", "ro.product.model"],
            stderr=subprocess.STDOUT
        ).decode(errors="ignore").strip()

        if not name:
            name = "Unknown Model"

        return name

    except Exception:
        return "Unknown Model"


# ---------------------------------------------------------
#  SELECT WHICH ADB DEVICE TO USE (USB MODE)
# ---------------------------------------------------------
def select_adb_device_usb():
    devices = list_adb_devices()
    selected = select_device(devices)
    info = get_device_info(selected)
    print(f"[INFO] Selected USB device: {info['name']} ({selected})")
    return selected


# ---------------------------------------------------------
#  SELECT DEVICE IN TCP/IP MODE
# ---------------------------------------------------------
def select_adb_device_tcpip():
    devices = list_adb_devices()

    if not devices:
        print("[ERROR] No USB device detected for TCP/IP enabling.")
        sys.exit(1)

    # Käytetään moduulin valintaa USB-laitteen valintaan
    usb_serial = select_device(devices)
    info = get_device_info(usb_serial)

    # Jos IP löytyy DEVICE_MAP:sta → käytä sitä
    ip = info.get("ip")
    if ip:
        print(f"[INFO] Using mapped IP for {info['name']}: {ip}")
    else:
        # Muuten kysytään käyttäjältä
        ip = input("\nEnter device IP (tailscale): ").strip()

    print(f"[ADB] Enabling TCP/IP mode on USB device...")
    subprocess.call(["adb", "-s", usb_serial, "tcpip", "5555"])

    print(f"[ADB] Connecting to {ip}:5555...")
    subprocess.call(["adb", "connect", f"{ip}:5555"])

    print(f"✔ Connected over TCP/IP: {ip}:5555")
    return f"{ip}:5555"


# ---------------------------------------------------------
#  ASK USER WHICH SIM TO MONITOR
# ---------------------------------------------------------
def select_sim_slot():
    while True:
        print("\nSelect SIM to monitor:")
        print("1 = SIM 1")
        print("2 = SIM 2")
        sim = input("Enter SIM number: ").strip()

        if sim in ["1", "2"]:
            return int(sim) - 1

        print("Invalid selection. Try again.\n")


# ---------------------------------------------------------
#  PARSE TELEPHONY.REGISTRY FOR SIGNAL + IMS + CALL STATE
# ---------------------------------------------------------
def get_phone_status(phone_id):
    status = {
        "call_state": "Unknown",
        "operator": "Unknown",
        "ims": "Unknown",
        "nr_available": "Unknown",
        "rat": "Unknown",
        "lte_rsrp": "—",
        "lte_rsrq": "—",
        "lte_snr": "—",
        "nr_rsrp": "—",
        "nr_rsrq": "—",
        "nr_sinr": "—",
        "incoming_number": "—"
    }

    try:
        out = subprocess.check_output(
            ["adb", "shell", "dumpsys", "telephony.registry"],
            stderr=subprocess.STDOUT
        ).decode(errors="ignore")

        blocks = out.split("Phone Id=")
        target = None

        for b in blocks:
            if b.strip().startswith(str(phone_id)):
                target = b
                break

        if not target:
            return status

        for line in target.splitlines():
            line = line.strip()

            if "mCallState" in line:
                cs = int(line.split("=")[-1].strip())
                status["call_state"] = {0: "IDLE", 1: "RINGING", 2: "OFFHOOK"}.get(cs, "Unknown")

            if "mOperatorAlphaLong" in line:
                status["operator"] = line.split("=")[-1].strip()

            if "mImsRegistered" in line:
                status["ims"] = "Registered" if "true" in line else "Not registered"

            if "isNrAvailable" in line:
                status["nr_available"] = "Yes" if "true" in line else "No"

            if "lteRsrp" in line:
                status["lte_rsrp"] = line.split("=")[-1].strip()
            if "lteRsrq" in line:
                status["lte_rsrq"] = line.split("=")[-1].strip()
            if "lteRssnr" in line:
                status["lte_snr"] = line.split("=")[-1].strip()

            if "ssRsrp" in line:
                status["nr_rsrp"] = line.split("=")[-1].strip()
            if "ssRsrq" in line:
                status["nr_rsrq"] = line.split("=")[-1].strip()
            if "ssSinr" in line:
                status["nr_sinr"] = line.split("=")[-1].strip()

            if "mCallIncomingNumber" in line:
                num = line.split("=")[-1].strip()
                status["incoming_number"] = num if num else "—"

        lte = status["lte_rsrp"] != "—"
        nr = status["nr_rsrp"] != "—"

        if nr and not lte:
            status["rat"] = "5G SA"
        elif nr and lte:
            status["rat"] = "5G NSA"
        elif lte:
            status["rat"] = "LTE"
        else:
            status["rat"] = "Unknown"

    except Exception:
        pass

    return status



# ---------------------------------------------------------
#  JSON LOGGING
# ---------------------------------------------------------
def log_event(event_type, phone_id, number, status, device_name):
    entry = {
        "timestamp": time.strftime("%H:%M:%S"),
        "event": event_type,
        "sim": phone_id + 1,
        "number": number,
        "rat": status["rat"],
        "operator": status["operator"],
        "device": device_name
    }

    with open("call_events.json", "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------
#  DASHBOARD
# ---------------------------------------------------------
def dashboard_loop(phone_id, device_name):
    global incoming_call_counter

    while True:
        os.system("clear")
        st = get_phone_status(phone_id)

        incoming = st["incoming_number"]
        if incoming == "" or incoming == "—":
            incoming = "—"

        print("==============================================")
        print("        📱 PHONE STATUS DASHBOARD")
        print("==============================================")
        print(f" Device Model:       {device_name}")
        print(f" SIM Slot:           {phone_id + 1}")
        print(f" Operator:           {st['operator']}")
        print(f" Call State:         {st['call_state']}")
        print(f" Incoming Number:    {incoming}")
        print(f" Total Calls:        {incoming_call_counter}")
        print(f" Radio Network:      {st['rat']}")
        print("----------------------------------------------")
        print(" LTE SIGNAL")
        print(f"   RSRP:             {st['lte_rsrp']}")
        print(f"   RSRQ:             {st['lte_rsrq']}")
        print(f"   SNR:              {st['lte_snr']}")
        print("----------------------------------------------")
        print(" NR SIGNAL")
        print(f"   RSRP:             {st['nr_rsrp']}")
        print(f"   RSRQ:             {st['nr_rsrq']}")
        print(f"   SINR:             {st['nr_sinr']}")
        print("----------------------------------------------")
        print(f" IMS Registered:     {st['ims']}")
        print(f" NR Available:       {st['nr_available']}")
        print("----------------------------------------------")
        print(f" Last Update:        {time.strftime('%H:%M:%S')}")
        print("==============================================")

        if st["call_state"] == "RINGING":
            print(" 🔔 Incoming call…")
        else:
            print(" Waiting for incoming calls…")

        print("==============================================")

        time.sleep(1)


# ---------------------------------------------------------
#  GET CALL STATE
# ---------------------------------------------------------
def get_call_state(phone_id):
    try:
        out = subprocess.check_output(
            ["adb", "shell", "dumpsys", "telephony.registry"],
            stderr=subprocess.STDOUT
        ).decode(errors="ignore")

        blocks = out.split("Phone Id=")
        target = None

        for b in blocks:
            if b.strip().startswith(str(phone_id)):
                target = b
                break

        if not target:
            return -1

        for line in target.splitlines():
            if "mCallState" in line:
                return int(line.split("=")[-1].strip())

    except Exception:
        return -1

    return -1


# ---------------------------------------------------------
#  ANSWER CALL
# ---------------------------------------------------------
def answer_call():
    print("📞 Answering call...")
    subprocess.call(["adb", "shell", "input", "keyevent", "5"])
    print("✔️ Call answered.")


# ---------------------------------------------------------
#  INCOMING CALL HANDLER
# ---------------------------------------------------------
def incoming_call_handler(phone_id, device_name):
    global incoming_call_counter

    st = get_phone_status(phone_id)
    number = st["incoming_number"]

    incoming_call_counter += 1

    print(f"\n🔔 Incoming call detected! Number: {number}")
    print(f"📊 Total calls since start: {incoming_call_counter}")

    # Log event
    log_event("incoming_call", phone_id, number, st, device_name)

    # Mattermost notification every 50 calls
    if incoming_call_counter % 50 == 0:
        msg = (
            f"🚨 https://github.devcloud.elisa.fi/Datacore/toolbox/edit/main/auto_answer_mtc/ 🚨\n"
            f"🚨 **{incoming_call_counter} incoming calls received** 🚨\n"
            f"Device: {device_name}\n"
            f"SIM: {phone_id + 1}\n"
            f"Last caller: {number}\n"
            f"RAT: {st['rat']}\n"
            f"Operator: {st['operator']}"
        )
        send_mattermost(msg)
        print(f"📨 Mattermost notification sent ({incoming_call_counter} calls milestone).")

    answer_call()



# ---------------------------------------------------------
#  LOGCAT LISTENER WITH DEBOUNCE
# ---------------------------------------------------------
def logcat_listener(phone_id, device_name):
    proc = subprocess.Popen(
        ["adb", "logcat", "-b", "radio"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    ring_confirmations = 0

    for line in proc.stdout:
        line = line.strip()

        if "RINGING" in line or "CALL_STATE_RINGING" in line:
            cs = get_call_state(phone_id)

            if cs == 1:
                ring_confirmations += 1
            else:
                ring_confirmations = 0

            if ring_confirmations >= 2:
                ring_confirmations = 0
                incoming_call_handler(phone_id, device_name)


# ---------------------------------------------------------
#  MAIN LOOP
# ---------------------------------------------------------
def monitor_incoming_calls(phone_id, device_name):
    threading.Thread(
        target=logcat_listener,
        args=(phone_id, device_name),
        daemon=True
    ).start()

    while True:
        if get_call_state(phone_id) == 1:
            incoming_call_handler(phone_id, device_name)
            time.sleep(5)

        time.sleep(0.5)


# ---------------------------------------------------------
#  ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    mode = select_connection_mode()

    if mode == "usb":
        adb_serial = select_adb_device_usb()
    else:
        adb_serial = select_adb_device_tcpip()

    device_name = get_device_name(adb_serial)

    os.environ["ANDROID_SERIAL"] = adb_serial

    phone_id = select_sim_slot()

    threading.Thread(target=dashboard_loop, args=(phone_id, device_name), daemon=True).start()

    monitor_incoming_calls(phone_id, device_name)
