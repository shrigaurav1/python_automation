from kubernetes import client, config
import smtplib
from email.mime.text import MIMEText
import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "alert@example.com")
SMTP_PASS = os.getenv("SMTP_PASS", "password")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "oncall@example.com")
RESTART_THRESHOLD = 5

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(SMTP_USER, [ALERT_EMAIL_TO], msg.as_string())

def main():
    # Use in-cluster config if running inside a pod; otherwise load kubeconfig
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces().items

    problems = []

    for pod in pods:
        ns = pod.metadata.namespace
        name = pod.metadata.name

        for cs in (pod.status.container_statuses or []):
            reason = (cs.state.waiting.reason if cs.state and cs.state.waiting else "")
            restarts = cs.restart_count

            if reason == "CrashLoopBackOff" or restarts >= RESTART_THRESHOLD:
                problems.append(
                    f"{ns}/{name} container={cs.name} state={reason} restarts={restarts}"
                )

    if problems:
        body = "Found problematic pods:\n\n" + "\n".join(problems)
        send_email("K8s Pod CrashLoop/Restart Alert", body)
        print("Alert sent:\n", body)
    else:
        print("No problematic pods found")

if __name__ == "__main__":
    main()
