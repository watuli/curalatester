def bar_graph(value, min_val, max_val, width=20):
    try:
        v = float(value)
    except:
        return "—"

    v = max(min_val, min(max_val, v))
    fraction = (v - min_val) / (max_val - min_val)
    filled = int(fraction * width)
    return "█" * filled + "─" * (width - filled)

def bar_rsrp(v): return bar_graph(v, -140, -44)
def bar_rsrq(v): return bar_graph(v, -20, -3)
def bar_sinr(v): return bar_graph(v, -5, 30)

