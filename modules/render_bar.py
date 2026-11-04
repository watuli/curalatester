# modules/render_bar.py
# ---------------------------------------------------
# Renders a horizontal bar for RF values (RSRP/RSRQ/SINR)
# ---------------------------------------------------

# You can later add color support by importing from rf_quality
# For now, bars are plain white.

def render_bar(value, width=20, min_val=-120, max_val=30):
    """
    Render a horizontal bar for RF metrics.
    Handles:
      - numeric values
      - "—" (no data)
    """

    # No data → empty bar
    if value == "—":
        return "─" * width

    try:
        v = int(value)
    except ValueError:
        return "─" * width

    # Clamp value to range
    if v < min_val:
        v = min_val
    if v > max_val:
        v = max_val

    # Normalize to 0..1
    ratio = (v - min_val) / (max_val - min_val)

    # Compute bar fill
    filled = int(ratio * width)
    empty = width - filled

    return "█" * filled + "─" * empty
