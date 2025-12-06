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
    both = "Both"
    afan_oromo = "Afan Oromo"
    amharic = "Amharic"


class MisionnaryBase(SQLModel):
    full_name: str
    batch: int
    phone: str = Field(max_length=10, min_length=10)
    language: LanguageOption
    experienced: bool = Field(default=False)
    attendance: bool = Field(default=False)
    verified: bool = Field(default=False)


class MissionaryCreate(MisionnaryBase):
    pass


class Missionary(MissionaryCreate, table=True):
    id: uuid.UUID = Field(index=True, unique=True, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    recipients: List["Recipient"] = Relationship(back_populates="missionary")
    teams_led: List["Team"] = Relationship(back_populates="leader")
    team_members: Optional["TeamMember"] = Relationship(back_populates="missionary")


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


# ---------- Site ----------
class SiteBase(SQLModel):
    name: str
    location: Optional[str] = None


class SiteCreate(SiteBase):
    pass


class Site(SiteBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    teams: Optional["Team"] = Relationship(back_populates="site")


# ---------- Team ----------
class TeamBase(SQLModel):
    site_id: uuid.UUID = Field(foreign_key="site.id")
    name: str
    leader_id: Optional[uuid.UUID] = Field(foreign_key="missionary.id", default=None)


class TeamCreate(TeamBase):
    pass


class Team(TeamBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    site: Optional["Site"] = Relationship(back_populates="teams")
    leader: Optional["Missionary"] = Relationship(back_populates="teams_led")
    members: List["TeamMember"] = Relationship(back_populates="team")


# ---------- TeamMember ----------
class TeamMemberBase(SQLModel):
    team_id: uuid.UUID = Field(foreign_key="team.id")
    missionary_id: uuid.UUID = Field(foreign_key="missionary.id")
    role: str
    experience: bool
    language: LanguageOption


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMember(TeamMemberBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    team: Optional["Team"] = Relationship(back_populates="members")
    missionary: Optional["Missionary"] = Relationship(back_populates="team_members")
