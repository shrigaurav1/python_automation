#!/usr/bin/env python3
import os
import time
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
HEARTBEAT_PATH = "/var/log/engine/heartbeat"    # heartbeat file
THRESHOLD_SEC = 1.0                             # 1000ms threshold
COOLDOWN_SEC = 300                              # avoid email spam (5 minutes)
STATE_FILE = "/tmp/heartbeat_last_alert"        # state for cooldown

# Email config (use app password for Gmail)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "your.email@gmail.com"
SMTP_PASS = "your_app_password"
EMAIL_TO  = "alerts@example.com"
EMAIL_FROM = SMTP_USER


# -----------------------------
# SEND EMAIL ALERT
# -----------------------------
def send_alert(message):
    msg = EmailMessage()
    msg["Subject"] = "Trading Engine Hang Detected"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(message)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print("Alert email sent!")
    except Exception as e:
        print(f"Email failed: {e}")


# -----------------------------
# COOLDOWN CHECK
# -----------------------------
def cooldown_ok():
    if not os.path.exists(STATE_FILE):
        return True
    last = float(open(STATE_FILE).read().strip())
    return (time.time() - last) > COOLDOWN_SEC


def update_cooldown():
    with open(STATE_FILE, "w") as f:
        f.write(str(time.time()))


# -----------------------------
# MAIN
# -----------------------------
def main():
    if not os.path.exists(HEARTBEAT_PATH):
        print("Heartbeat file missing!")
        return

    mtime = os.path.getmtime(HEARTBEAT_PATH)
    delay = time.time() - mtime

    # Write metrics for Prometheus Node Exporter (Grafana)
    write_prometheus_metrics(delay)

    if delay > THRESHOLD_SEC:
        if cooldown_ok():
            msg = (
                f"Trading Engine heartbeat delayed!\n"
                f"Delay: {delay:.3f} seconds\n"
                f"Threshold: {THRESHOLD_SEC}s\n"
                f"Time: {datetime.utcnow().isoformat()}Z\n"
            )
            send_alert(msg)
            update_cooldown()
        else:
            print("Cooldown active — alert suppressed.")
    else:
        print("Heartbeat OK:", delay)


# -----------------------------
# PROMETHEUS METRICS EXPORT
# -----------------------------
def write_prometheus_metrics(delay):
    """
    This writes a file node_exporter can read:
    /var/lib/node_exporter/textfile_collector/heartbeat.prom
    """
    path = "/var/lib/node_exporter/textfile_collector/heartbeat.prom"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(f"heartbeat_delay_seconds {delay}\n")
        f.write(f"heartbeat_threshold_seconds {THRESHOLD_SEC}\n")
        f.write(f"heartbeat_ok {1 if delay <= THRESHOLD_SEC else 0}\n")


if __name__ == "__main__":
    main()
