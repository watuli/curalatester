import time
import subprocess
import sys

# ---------------------------------------------------------
# Spinner (visual wait)
# ---------------------------------------------------------
def spinner_wait(seconds):
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + seconds
    idx = 0
    while time.time() < end_time:
        sys.stdout.write(f"\rWaiting {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    print("\r", end="")

# ---------------------------------------------------------
# Make call
# ---------------------------------------------------------
def make_call(device_serial, phone_number, sim_slot):
    """
    sim_slot = 0 for SIM1
    sim_slot = 1 for SIM2
    """
    try:
        subprocess.run(
            [
                "adb", "-s", device_serial, "shell", "am", "start",
                "-a", "android.intent.action.CALL",
                "-d", f"tel:{phone_number}",
                "--ei", "android.telecom.extra.PHONE_ACCOUNT_HANDLE_ID", str(sim_slot)
            ],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


# ---------------------------------------------------------
# End call
# ---------------------------------------------------------
def end_call(device_serial):
    try:
        subprocess.run(
            ["adb", "-s", device_serial, "shell", "input", "keyevent", "KEYCODE_ENDCALL"],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

# ---------------------------------------------------------
# Nokia-compatible call state detection
# ---------------------------------------------------------
def get_call_state(device_serial):
    """
    Returns one of: "IDLE", "DIALING", "RINGING", "ACTIVE"
    """
    try:
        out = subprocess.check_output(
            ["adb", "-s", device_serial, "shell", "dumpsys", "telecom"],
            stderr=subprocess.STDOUT
        ).decode(errors="ignore")

        if "state=ACTIVE" in out:
            return "ACTIVE"

        if "state=RINGING" in out:
            return "RINGING"

        if "state=DIALING" in out or "state=CONNECTING" in out:
            return "DIALING"

        if "state=DISCONNECTED" in out:
            return "IDLE"

    except Exception:
        return "IDLE"

    return "IDLE"

# ---------------------------------------------------------
# Wait for call to be answered
# ---------------------------------------------------------
def wait_for_call_answer(device_serial, timeout=20):
    """
    Wait until call transitions to ACTIVE.
    Returns (answered: bool, setup_time: float or None)
    """
    start = time.time()

    while time.time() - start < timeout:
        state = get_call_state(device_serial)

        if state == "ACTIVE":
            setup_time = time.time() - start
            return True, setup_time

        if state == "IDLE":
            return False, None

        time.sleep(0.2)

    return False, None

# ---------------------------------------------------------
# Measure call timing (PDD, ringing, setup)
# ---------------------------------------------------------
def measure_call_timing(device_serial, timeout=30):
    """
    Tracks:
      - PDD (dial → ringing)
      - Ringing time (ringing → active)
      - Total setup time (dial → active)
    Returns dict with timing values.
    """
    t_start = time.time()
    t_dial = t_start
    t_ring = None
    t_active = None

    while time.time() - t_start < timeout:
        state = get_call_state(device_serial)

        if state == "RINGING" and t_ring is None:
            t_ring = time.time()

        if state == "ACTIVE":
            t_active = time.time()
            break

        if state == "IDLE" and t_ring is None:
            return {
                "answered": False,
                "pdd": None,
                "ringing_time": None,
                "setup_time": None
            }

        time.sleep(0.2)

    if t_active is None:
        return {
            "answered": False,
            "pdd": None,
            "ringing_time": None,
            "setup_time": None
        }

    pdd = t_ring - t_dial if t_ring else None
    ringing_time = t_active - t_ring if t_ring else None
    setup_time = t_active - t_dial

    return {
        "answered": True,
        "pdd": pdd,
        "ringing_time": ringing_time,
        "setup_time": setup_time
    }

