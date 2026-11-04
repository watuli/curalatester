# modules/msisdn_manager.py

MSISDN_LIST = [
    ("+358103403488", "Default test number (Elisa QA)"),
    ("+358505066249", "Backup SIM (Telia)"),
    ("+358401234567", "Load test target (Sonera)"),
    ("+358451112223", "VoLTE/VoWiFi test line"),
]

DEFAULT_MSISDN = MSISDN_LIST[0][0]


def select_msisdn():
    print("\nSelect MSISDN to call:")

    for i, (number, label) in enumerate(MSISDN_LIST, start=1):
        print(f"  {i}. {number:<15}  [{label}]")

    print(f"\nPress ENTER to use default: {DEFAULT_MSISDN}")

    choice = input("> ").strip()

    # ENTER → default
    if choice == "":
        print(f"[INFO] Using default MSISDN: {DEFAULT_MSISDN}")
        return DEFAULT_MSISDN

    # Validate numeric selection
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(MSISDN_LIST):
            selected = MSISDN_LIST[idx - 1][0]
            print(f"[INFO] Selected MSISDN: {selected}")
            return selected

    # Invalid → fallback to default
    print("[WARN] Invalid selection, using default MSISDN.")
    return DEFAULT_MSISDN
