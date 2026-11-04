# rf_quality.py
# ---------------------------------------------
# RF quality classification for RSRP / RSRQ / SINR
# ---------------------------------------------

# ANSI colors
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GREY   = "\033[90m"
RESET  = "\033[0m"


# -----------------------------
#   RSRP Classification
# -----------------------------
def classify_rsrp(value):
    if value == "—":
        return "UNKNOWN"
    v = int(value)

    if v >= -80:
        return "GOOD"
    if v >= -95:
        return "OK"
    return "BAD"


# -----------------------------
#   RSRQ Classification
# -----------------------------
def classify_rsrq(value):
    if value == "—":
        return "UNKNOWN"
    v = int(value)

    if v >= -10:
        return "GOOD"
    if v >= -15:
        return "OK"
    return "BAD"


# -----------------------------
#   SINR Classification
# -----------------------------
def classify_sinr(value):
    if value == "—":
        return "UNKNOWN"
    v = int(value)

    if v >= 20:
        return "GOOD"
    if v >= 10:
        return "OK"
    return "BAD"


# -----------------------------
#   Color mapping
# -----------------------------
def color_quality(label):
    if label == "GOOD":
        return f"{GREEN}{label}{RESET}"
    if label == "OK":
        return f"{YELLOW}{label}{RESET}"
    if label == "BAD":
        return f"{RED}{label}{RESET}"
    return f"{GREY}{label}{RESET}"


# -----------------------------
#   Optional: color for bars
# -----------------------------
def color_for_value(label, text):
    """Wrap bar text in color based on quality label."""
    if label == "GOOD":
        return f"{GREEN}{text}{RESET}"
    if label == "OK":
        return f"{YELLOW}{text}{RESET}"
    if label == "BAD":
        return f"{RED}{text}{RESET}"
    return f"{GREY}{text}{RESET}"
