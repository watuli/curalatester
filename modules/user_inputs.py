from config import PHONE_NUMBER_MOC

def ask_sim_slot():
    print("\nSelect SIM (1 or 2):")
    while True:
        sim = input("> ").strip()
        if sim in ("1", "2"):
            return int(sim) - 1   # convert to phoneId: 0 or 1
        print("Invalid SIM. Enter 1 or 2.")


def ask_phone_number():
    user_input = input(f"Enter phone number to call (default: {PHONE_NUMBER_MOC}): ").strip()
    return user_input if user_input else PHONE_NUMBER_MOC


def ask_call_mode():
    print("\nCall mode: 1 = Infinite, 2 = Fixed count")
    while True:
        mode = input("> ").strip()
        if mode == "1":
            return "infinite", None
        if mode == "2":
            max_calls = int(input("How many calls: ").strip())
            return "fixed", max_calls
        print("Invalid choice. Enter 1 or 2.")


def ask_duration_mode():
    print("\nDuration mode: 1 = Fixed, 2 = Random")

    while True:
        mode = input("> ").strip()

        if mode == "1":
            # Fixed duration
            d = int(input("Duration (s): ").strip())
            return {"mode": "fixed", "value": d}

        if mode == "2":
            # Random duration
            dmin = int(input("Min duration (s): ").strip())
            dmax = int(input("Max duration (s): ").strip())
            return {"mode": "random", "min": dmin, "max": dmax}

        print("Invalid choice. Enter 1 or 2.")

def ask_wait_time():
    print("\nEnter wait time before next call (seconds):")
    while True:
        try:
            return float(input("> ").strip())
        except ValueError:
            print("Invalid number. Try again.")

def ask_connection_mode():
    print("\nConnection mode:")
    print("  1. USB cable")
    print("  2. TCP/IP (tailscale)")

    while True:
        mode = input("> ").strip()
        if mode == "1":
            return "usb"
        if mode == "2":
            return "tcpip"
        print("Invalid choice. Enter 1 or 2.")

def collect_user_call_settings():
    sim_slot = ask_sim_slot()
    phone_number = ask_phone_number()
    call_mode, max_calls = ask_call_mode()
    duration_settings = ask_duration_mode()
    wait_time = ask_wait_time()

    return {
        "sim_slot": sim_slot,
        "phone_number": phone_number,
        "call_mode": call_mode,
        "max_calls": max_calls,
        "duration": duration_settings,
        "wait_time": wait_time
    }

