from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
import uuid
from typing import List, Optional
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

    recipients: List["Recipient"] = Relationship(back_populates="missionary")


class RecipientStatus(str, Enum):
    win = "Win"
    hope = "Hope"
    exposed = "Exposed"


class ReligionStatus(str, Enum):
    orthodox = "Orthodox"
    muslim = "Muslim"
    jehovah_witness = "Jehova Witness"
    only_jesus = "Only Jesus"
    adventist = "Adventist"
    waqefeta = "Waqefeta"
    others = "Others"


class RecipientBase(SQLModel):
    full_name: str
    missionary_id: uuid.UUID = Field(
        foreign_key="missionary.id", ondelete="SET NULL", nullable=True
    )
    phone: str = Field(max_length=10, min_length=10)
    location: str
    status: RecipientStatus
    current_religion: ReligionStatus
    nearest_church: str


class RecipientCreate(RecipientBase):
    pass


class Recipient(RecipientCreate, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    missionary: Optional["Missionary"] = Relationship(back_populates="recipients")
