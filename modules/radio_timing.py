# modules/radio_timing.py
import subprocess
import time
import re
from modules.call_control import make_call  # <-- add this import

PAT_DIALING = re.compile(r"state=DIALING")
PAT_ALERTING = re.compile(r"state=ALERTING")
PAT_ACTIVE  = re.compile(r"state=ACTIVE")
PAT_SIP_100 = re.compile(r"SIP/2\.0 100")
PAT_SIP_180 = re.compile(r"SIP/2\.0 180")
PAT_SIP_183 = re.compile(r"SIP/2\.0 183")
PAT_SIP_200 = re.compile(r"SIP/2\.0 200")

def now():
    return time.time()

def measure_call_timing_radio(phone_number, timeout=20):
    # clear old logs
    subprocess.run(["adb", "logcat", "-b", "radio", "-c"])

    # start logcat
    proc = subprocess.Popen(
        ["adb", "logcat", "-b", "radio"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # place the call AFTER logcat is running
    make_call(phone_number)

    t_start = now()
    t_dial = t_alert = t_active = None
    t_sip100 = t_sip180 = t_sip183 = t_sip200 = None

    for line in proc.stdout:
        ts = now()

        if PAT_SIP_100.search(line):
            t_sip100 = t_sip100 or ts
        if PAT_SIP_180.search(line):
            t_sip180 = t_sip180 or ts
        if PAT_SIP_183.search(line):
            t_sip183 = t_sip183 or ts
        if PAT_SIP_200.search(line):
            t_sip200 = t_sip200 or ts

        if PAT_DIALING.search(line):
            t_dial = t_dial or ts
        if PAT_ALERTING.search(line):
            t_alert = t_alert or ts
        if PAT_ACTIVE.search(line):
            t_active = t_active or ts
            break

        if now() - t_start > timeout:
            break

    proc.kill()

    answered = t_active is not None

    if t_sip180:
        pdd = t_sip180 - (t_dial or t_start)
    elif t_alert:
        pdd = t_alert - (t_dial or t_start)
    else:
        pdd = None

    ringing_time = (t_active - t_alert) if (t_active and t_alert) else None
    setup_time   = (t_active - t_dial)  if (t_active and t_dial)  else None
    early_media  = t_sip183 is not None and (not t_sip180 or t_sip183 < t_sip180)

    return {
        "answered": answered,
        "pdd": pdd,
        "ringing_time": ringing_time,
        "setup_time": setup_time,
        "early_media": early_media,
        "sip_100": t_sip100,
        "sip_180": t_sip180,
        "sip_183": t_sip183,
        "sip_200": t_sip200,
        "dial": t_dial,
        "alert": t_alert,
        "active": t_active
    }

