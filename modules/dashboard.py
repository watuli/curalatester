import os

from modules.render_bar import render_bar
from modules.rf_quality import (
    classify_rsrp, classify_rsrq, classify_sinr,
    color_quality, color_for_value
)



def color_5g(mode):
    if mode == "5G SA":
        return f"\033[92m{mode}\033[0m"
    if mode == "5G NSA":
        return f"\033[93m{mode}\033[0m"
    if mode == "5G":
        return f"\033[96m{mode}\033[0m"
    return f"\033[90m{mode}\033[0m"

def color_endc(status):
    if status == "ENDC":
        return f"\033[95m{status}\033[0m"
    return f"\033[90m{status}\033[0m"

def print_dashboard(title, rf, call_count):
    os.system("clear")

    def fmt(v):
        return v if v not in ["N/A", "2147483647"] else "—"

    print(f"==================== {title} ====================")
    print(f"📱 Phone: {rf['model']}")
    print(f"📞 Total Calls: {call_count}")
    print("-----------------------------------------------")
    print(f"Data RAT:   {rf['data_rat']}")
    print(f"Voice RAT:  {rf['voice_rat']}")
    print(f"5G Mode:    {color_5g(rf['nr_mode'])}")
    print(f"NR Band:    {rf['nr_band']}")
    print(f"ENDC:       {color_endc(rf['endc'])}")
    print("-----------------------------------------------")

    rsrp = rf.get("rsrp", "—")
    rsrq = rf.get("rsrq", "—")
    sinr = rf.get("sinr", "—")
    
    rsrp_q = classify_rsrp(rsrp)
    rsrq_q = classify_rsrq(rsrq)
    sinr_q = classify_sinr(sinr)

    print(f"RSRP:   {rsrp:>4}  {render_bar(rsrp)}  {color_quality(rsrp_q)}")
    print(f"RSRQ:   {rsrq:>4}  {render_bar(rsrq)}  {color_quality(rsrq_q)}")
    print(f"SINR:   {sinr:>4}  {render_bar(sinr)}  {color_quality(sinr_q)}")

    print("-----------------------------------------------")
    print(f"PCI: {fmt(rf['pci'])}   TAC: {fmt(rf['tac'])}")
    print(f"ARFCN: {fmt(rf['arfcn'])}   NCI: {fmt(rf['nci'])}")
    print("===============================================\n")


