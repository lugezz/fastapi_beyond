
import time

from fastapi import APIRouter, BackgroundTasks, Header, status

from app.schemas.others import EmailPayload
from app.tasks.celery_tasks import send_email

router = APIRouter(prefix="/others", tags=["others"])


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/greet")
async def greet(name: str = "Guest", age: int = 30):
    return {"message": f"Hello, {name}!, You are {age} years old."}


@router.get("/get-headers")
async def get_headers(
    accept: str = Header(None),
    user_agent: str = Header(None),
    content_type: str = Header(None),
    host: str = Header(None)
):
    requested_headers = {
        "Accept": accept,
        "User-Agent": user_agent,
        "Content-Type": content_type,
        "Host": host
    }
    return {"requested_headers": requested_headers}


@router.post("/long-request")
async def long_request(
    payload: dict,
    background_tasks: BackgroundTasks
):
    email = payload.get("email", "")

    def sleep_task():
        time.sleep(5)
        print(f"Finished long request for email: {email}")

    background_tasks.add_task(sleep_task)
    return {
        "message": f"This is a long request endpoint from email: {email}"
    }


@router.post("/send-email", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def send_email_in_background(payload: EmailPayload):
    recipients = payload.recipients
    subject = payload.subject
    body = payload.body

    task = send_email.delay(recipients, subject, body)

    return {
        "message": "Email task queued",
        "task_id": task.id,
    }
