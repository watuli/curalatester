import time
from modules.call_control import make_call, end_call
from modules.rf_info import get_rf_snapshot
from modules.dashboard import print_dashboard

def run_call_loop(device_serial, settings):
    call_count = 0

    while True:
        # increment FIRST
        call_count += 1

        # --- DASHBOARD BEFORE CALL ---
        rf = get_rf_snapshot(settings["sim_slot"])
        print_dashboard("IDLE STATE", rf, call_count)
        time.sleep(1)

        # --- START CALL ---
        print(f"\n--- Call #{call_count} ---")
        make_call(device_serial, settings["phone_number"], settings["sim_slot"])

        # --- DASHBOARD DURING CALL ---
        rf = get_rf_snapshot(settings["sim_slot"])
        print_dashboard("CALL ACTIVE", rf, call_count)

        # duration selection
        if settings["duration"]["mode"] == "fixed":
            duration = settings["duration"]["value"]
        else:
            import random
            duration = random.randint(settings["duration"]["min"], settings["duration"]["max"])

        time.sleep(duration)

        # --- END CALL ---
        end_call(device_serial)

        # --- DASHBOARD AFTER CALL ---
        rf = get_rf_snapshot(settings["sim_slot"])
        print_dashboard("CALL ENDED", rf, call_count)
        time.sleep(1)

        # --- WAIT LOOP WITH LIVE RF ---
        wait_time = int(settings["wait_time"])
        for i in range(wait_time):
            rf = get_rf_snapshot(settings["sim_slot"])
            print_dashboard(f"WAITING {wait_time - i}s", rf, call_count)
            time.sleep(1)
