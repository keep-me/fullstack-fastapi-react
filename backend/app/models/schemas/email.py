from pydantic import BaseModel, EmailStr


class EmailMessage(BaseModel):
    to: EmailStr
    subject: str
    body: str
