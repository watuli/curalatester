import re
from .adb_utils import adb

# NR band lookup
NR_BAND_MAP = {
    1: "n1", 2: "n2", 3: "n3", 5: "n5", 7: "n7", 8: "n8",
    20: "n20", 28: "n28", 38: "n38", 40: "n40", 41: "n41",
    48: "n48", 66: "n66", 71: "n71", 75: "n75", 76: "n76",
    77: "n77", 78: "n78", 79: "n79",
    258: "n258", 260: "n260", 261: "n261"
}

def get_call_state():
    out = adb("shell dumpsys telephony.registry").stdout.decode(errors="ignore")
    m = re.search(r"mCallState=(\d+)", out)
    if not m:
        return "UNKNOWN"

    state = int(m.group(1))
    if state == 0:
        return "IDLE"
    if state == 1:
        return "RINGING"
    if state == 2:
        return "OFFHOOK"
    return "UNKNOWN"


def get_phone_model():
    result = adb("shell getprop ro.product.model")
    return result.stdout.decode(errors="ignore").strip() or "Unknown Model"

def get_network_type(phone_id):
    out = adb("shell dumpsys telephony.registry").stdout.decode(errors="ignore")

    block = _extract_block(out, phone_id)
    if not block:
        return "UNKNOWN", "UNKNOWN"

    data = _extract(block, r"getRilDataRadioTechnology=\d+\((.*?)\)")
    voice = _extract(block, r"getRilVoiceRadioTechnology=\d+\((.*?)\)")

    return data, voice

def get_signal_strength(phone_id):
    out = adb("shell dumpsys telephony.registry").stdout.decode(errors="ignore")

    # Grab ALL NR signal blocks in the dump
    matches = re.findall(r"CellSignalStrengthNr\s*:\s*\{(.*?)\}", out, re.DOTALL)
    if not matches:
        print("DEBUG: No CellSignalStrengthNr blocks found at all")
        return "—", "—", "—"

    # Use the LAST one (most recent / active)
    nr = matches[-1]
    print("DEBUG: Using NR block:")
    print(nr)

    rsrp = _extract(nr, r"ssRsrp\s*=\s*(-?\d+)")
    rsrq = _extract(nr, r"ssRsrq\s*=\s*(-?\d+)")
    sinr = _extract(nr, r"ssSinr\s*=\s*(-?\d+)")

    print(f"DEBUG: Parsed RSRP={rsrp}, RSRQ={rsrq}, SINR={sinr}")
    return rsrp, rsrq, sinr

def get_cell_info(phone_id):
    out = adb("shell dumpsys telephony.registry").stdout.decode(errors="ignore")
    block = _extract_phone_block(out, phone_id)
    if not block:
        return "—", "—", "—", "—"

    m = re.search(r"CellIdentityNr:\{(.*?)\}", block, re.DOTALL)
    if not m:
        return "—", "—", "—", "—"

    ci = m.group(1)

    pci   = _extract(ci, r"mPci\s*=\s*(\d+)")
    tac   = _extract(ci, r"mTac\s*=\s*(\d+)")
    arfcn = _extract(ci, r"mNrArfcn\s*=\s*(\d+)")
    nci   = _extract(ci, r"mNci\s*=\s*(\d+)")

    return pci, tac, arfcn, nci

def get_nr_band(phone_id):
    out = adb("shell dumpsys telephony.registry").stdout.decode(errors="ignore")
    block = _extract_phone_block(out, phone_id)
    if not block:
        return "—"

    m = re.search(r"mBands\s*=\s*\[(\d+)\]", block)
    if not m:
        return "—"

    band_num = int(m.group(1))
    return NR_BAND_MAP.get(band_num, f"n{band_num}")


def get_5g_mode(phone_id):
    out = adb("shell dumpsys telephony.registry").stdout.decode(errors="ignore")
    block = _extract_block(out, phone_id)
    if not block:
        return "Unknown"

    tech_fields = []
    tech_fields.append(_extract(block, r"getRilDataRadioTechnology=\d+\((.*?)\)"))
    tech_fields.append(_extract(block, r"getRilVoiceRadioTechnology=\d+\((.*?)\)"))
    tech_fields.extend(re.findall(r"accessNetworkTechnology=(\w+)", block))
    tech_fields.append(_extract(block, r"isEnDcAvailable\s*=\s*(\w+)"))
    tech_fields.append(_extract(block, r"isNrAvailable\s*=\s*(\w+)"))

    tech = " ".join([t for t in tech_fields if t and t != "—"]).upper()

    if "NR_SA" in tech:
        return "5G SA"
    if "NR_NSA" in tech or "ENDC" in tech:
        return "5G NSA"
    if "NR" in tech:
        return "5G"

    return "No 5G"



def get_endc_status(phone_id):
    out = adb("shell dumpsys telephony.registry").stdout.decode(errors="ignore")
    block = _extract_phone_block(out, phone_id)
    if not block:
        return "—"

    endc = _extract(block, r"isEnDcAvailable\s*=\s*(\w+)")
    nr_avail = _extract(block, r"isNrAvailable\s*=\s*(\w+)")
    rat = _extract(block, r"getRilDataRadioTechnology=\d+\((.*?)\)")

    endc = endc.upper()
    nr_avail = nr_avail.upper()
    rat = rat.upper()

    if "LTE" in rat and endc == "TRUE" and nr_avail == "TRUE":
        return "ENDC"

    return "—"


def _extract_block(output, phone_id):
    # Extract only the service state block: state={ ... }
    pattern = rf"Phone Id={phone_id}.*?state=\{{(.*?)\}}"
    m = re.search(pattern, output, re.DOTALL)
    return m.group(1) if m else None

def _extract_phone_block(output, phone_id):
    # Match "Phone Id=X" followed by ANY indented lines until next "Phone Id="
    pattern = rf"Phone Id={phone_id}\n((?:\s+.*\n)+)"
    m = re.search(pattern, output)
    return m.group(1) if m else None


def _extract(text, pattern):
    m = re.search(pattern, text)
    if not m:
        return "—"
    v = m.group(1)
    return v if v != "2147483647" else "—"

def get_rf_snapshot(sim_slot):
    phone_id = sim_slot - 1

    # --- Service state (works) ---
    data_rat, voice_rat = get_network_type(phone_id)
    nr_mode = get_5g_mode(phone_id)

    # --- Signal strength (NR RSRP/RSRQ/SINR) ---
    rsrp, rsrq, sinr = get_signal_strength(phone_id)

    # --- Cell identity (PCI/TAC/ARFCN/NCI) ---
    pci, tac, arfcn, nci = get_cell_info(phone_id)

    # --- NR band ---
    nr_band = get_nr_band(phone_id)

    # --- ENDC ---
    endc = get_endc_status(phone_id)

    # --- Model ---
    model = get_phone_model()

    return {
        "data_rat": data_rat,
        "voice_rat": voice_rat,
        "nr_mode": nr_mode,
        "rsrp": rsrp,
        "rsrq": rsrq,
        "sinr": sinr,
        "pci": pci,
        "tac": tac,
        "arfcn": arfcn,
        "nci": nci,
        "nr_band": nr_band,
        "endc": endc,
        "model": model
    }
