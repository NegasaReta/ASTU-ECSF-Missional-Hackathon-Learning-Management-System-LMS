from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
import uuid
from enum import Enum


class AdminBase(SQLModel):
    full_name: str
    email: EmailStr
    password: str
    phone: str = Field(max_length=10, min_length=10)


class AdminCreate(AdminBase):
    pass


class Admin(AdminCreate, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LanguageOption(str, Enum):
    both = "Afan Oromo and Amharic"
    afan_oromo = "Afan Oromo"
    amharic = "Amharic"


class MisionnaryBase(SQLModel):
    full_name: str
    email: EmailStr
    batch: int
    phone: str = Field(max_length=10, min_length=10)
    language: LanguageOption
    experienced: bool
    password: str


class MissionaryCreate(MisionnaryBase):
    pass


class Missionary(MissionaryCreate, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
