import requests
import os
from email.mime.text import MIMEText
import smtplib

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus.monitoring.svc:9090")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "alert@example.com")
SMTP_PASS = os.getenv("SMTP_PASS", "password")
REPORT_EMAIL_TO = os.getenv("REPORT_EMAIL_TO", "sre-team@example.com")
TOP_N = 10

def query_top_alerts():
    # Adjust metric name/labels as per your setup
    query = r'''
topk(
  {TOP_N},
  sum(increase(alertmanager_notifications_total[24h])) by (alertname, severity)
)
'''.replace("{TOP_N}", str(TOP_N))

    resp = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    if data["status"] != "success":
        raise RuntimeError(f"Prometheus error: {data}")
    return data["data"]["result"]

def format_report(results):
    if not results:
        return "No alert notifications in the last 24h."

    lines = ["Top alerts in last 24h:\n"]
    for r in results:
        labels = r["metric"]
        value = float(r["value"][1])
        name = labels.get("alertname", "unknown")
        severity = labels.get("severity", "unknown")
        lines.append(f"{name} (severity={severity}) -> {value:.0f} notifications")
    return "\n".join(lines)

def send_email_report(body):
    msg = MIMEText(body)
    msg["Subject"] = "Daily Alert Noise Report"
    msg["From"] = SMTP_USER
    msg["To"] = REPORT_EMAIL_TO
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(SMTP_USER, [REPORT_EMAIL_TO], msg.as_string())

def main():
    results = query_top_alerts()
    body = format_report(results)
    print(body)
    send_email_report(body)

if __name__ == "__main__":
    main()
