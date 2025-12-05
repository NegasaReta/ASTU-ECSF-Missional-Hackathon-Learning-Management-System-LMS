from sqlmodel import SQLModel, Field
from pydantic import EmailStr
import uuid


class AdminBase(SQLModel):
    full_name: str
    email: EmailStr
    password: str
    phone: str = Field(max_length=10, min_length=10)


class AdminCreate(AdminBase):
    pass


class Admin(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
