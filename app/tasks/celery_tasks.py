import time

from app.worker.celery_app import celery_app


@celery_app.task(name="tasks.send_email")
def send_email(recipients: list[str], subject: str, body: str) -> str:
    """Fake send email task"""
    time.sleep(5)
    recipients_str = ", ".join(recipients)
    print(f"Email sent to: {recipients_str}")
    print("Subject", subject)
    print("Body", body)
    return f"Email sent to {recipients_str}"
