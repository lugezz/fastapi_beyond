from pydantic import BaseModel


class EmailPayload(BaseModel):
    recipients: list
    subject: str
    body: str
