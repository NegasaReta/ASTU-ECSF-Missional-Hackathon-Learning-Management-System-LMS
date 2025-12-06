from datetime import datetime
from typing import List, Optional
import uuid
from sqlmodel import Session, select

from app.model.models import TeamMember, TeamMemberCreate
from app.utils.helpers import add_to_db, delete_from_db, update_to_db


def get_team_member(db: Session, team_member_id: uuid.UUID):
    return db.get(TeamMember, team_member_id)


def get_team_members(db: Session, skip: int = 0, limit: int = 0) -> List[TeamMember]:
    statement = select(TeamMember).offset(skip).limit(limit)
    return list(db.exec(statement).all())


def create_team_member(db: Session, team_member: TeamMemberCreate) -> TeamMember:
    db_team_member = TeamMember.model_validate(team_member)
    return add_to_db(db, db_team_member)


def update_team_member(
    db: Session, team_member_data: dict, team_member_id: uuid.UUID
) -> Optional[TeamMember]:
    team_member_data["updated_at"] = datetime.now()
    return update_to_db(db, team_member_id, team_member_data, TeamMember)


def delete_team_member(db: Session, team_member_id: uuid.UUID) -> bool:
    return delete_from_db(db, team_member_id, TeamMember)