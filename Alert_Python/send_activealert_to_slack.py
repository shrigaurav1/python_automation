import requests
import os

ALERTMANAGER_URL = os.getenv("ALERTMANAGER_URL", "http://alertmanager.monitoring.svc:9093")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def get_firing_alerts():
    resp = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
    resp.raise_for_status()
    alerts = resp.json()
    firing = [a for a in alerts if a.get("status", {}).get("state") == "active"]
    return firing

def format_alerts(alerts):
    if not alerts:
        return "No firing alerts :white_check_mark:"

    lines = []
    for a in alerts:
        labels = a.get("labels", {})
        annotations = a.get("annotations", {})
        name = labels.get("alertname", "unknown")
        severity = labels.get("severity", "unknown")
        summary = annotations.get("summary", "")
        instance = labels.get("instance", "")
        lines.append(f"*{name}* (severity={severity}, instance={instance}) - {summary}")
    return "\n".join(lines)

def send_slack_message(text):
    if not SLACK_WEBHOOK_URL:
        print("No SLACK_WEBHOOK_URL set, skipping Slack")
        return
    resp = requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=5)
    resp.raise_for_status()

def main():
    alerts = get_firing_alerts()
    msg = format_alerts(alerts)
    print(msg)
    send_slack_message(msg)

if __name__ == "__main__":
    main()
