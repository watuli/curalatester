import csv
from datetime import datetime
from config import LOG_FILE

def log_event(event_type, data_network, voice_network, extra=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, event_type, data_network, voice_network, extra]

    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)

