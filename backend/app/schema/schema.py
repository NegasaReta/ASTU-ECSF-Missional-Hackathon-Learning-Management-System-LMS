from pydantic import BaseModel, EmailStr
from typing import List
import uuid


class RecipientRead(BaseModel):
    id: uuid.UUID
    full_name: str
    phone: str
    location: str
    status: str
    current_religion: str
    nearest_church: str

    class Config:
        from_attributes = True


class MissionaryRead(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    batch: int
    phone: str
    language: str
    experienced: bool
    recipients: List[RecipientRead] = []

    class Config:
        from_attributes = True
