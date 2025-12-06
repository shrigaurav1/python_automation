import requests
import time
import os

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus.monitoring.svc:9090")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
CHECK_INTERVAL_SECONDS = 60

# Prometheus query for p99 latency (adjust metric & labels)
PROMQL_QUERY = r'''
histogram_quantile(
  0.99,
  sum(rate(http_request_duration_seconds_bucket{job="my-api"}[5m])) by (le)
)
'''

THRESHOLD_SECONDS = 1.0  # alert if p99 > 1s

def query_prometheus():
    resp = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": PROMQL_QUERY},
        timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    if data["status"] != "success":
        raise RuntimeError(f"Prometheus error: {data}")
    result = data["data"]["result"]
    if not result:
        return None
    # Assume single time series
    value = float(result[0]["value"][1])
    return value

def send_slack_alert(value):
    if not SLACK_WEBHOOK_URL:
        print("No SLACK_WEBHOOK_URL set, skipping Slack alert")
        return
    text = f":rotating_light: High p99 latency detected: {value:.3f}s (> {THRESHOLD_SECONDS}s)"
    payload = {"text": text}
    resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
    resp.raise_for_status()

def main():
    while True:
        try:
            value = query_prometheus()
            if value is None:
                print("No data for query yet")
            else:
                print(f"Current p99: {value:.3f}s")
                if value > THRESHOLD_SECONDS:
                    send_slack_alert(value)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
