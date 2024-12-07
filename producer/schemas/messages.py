from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    recipient: EmailStr
    subject: str
    body: str
