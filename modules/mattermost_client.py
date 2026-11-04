import json
import urllib.request
from config import MATTERMOST_WEBHOOK

MATTERMOST_THREAD_ID = None

def notify_mattermost(message):
    global MATTERMOST_THREAD_ID
    if not MATTERMOST_WEBHOOK:
        return

    payload = {"text": message}
    if MATTERMOST_THREAD_ID:
        payload["root_id"] = MATTERMOST_THREAD_ID

    try:
        req = urllib.request.Request(
            MATTERMOST_WEBHOOK,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode("utf-8"))

        if MATTERMOST_THREAD_ID is None and "id" in data:
            MATTERMOST_THREAD_ID = data["id"]

    except Exception as e:
        print(f"[Mattermost ERROR] {e}")

def notify_progress(call_count):
    notify_mattermost(f"📞 Progress: {call_count} calls completed.")

