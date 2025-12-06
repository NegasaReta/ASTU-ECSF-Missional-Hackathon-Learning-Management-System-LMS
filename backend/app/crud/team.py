from datetime import datetime
from typing import List, Optional
import uuid
from sqlmodel import Session, select

from app.model.models import Team, TeamCreate
from app.utils.helpers import add_to_db, delete_from_db, update_to_db


def get_team(db: Session, team_id: uuid.UUID):
    return db.get(Team, team_id)


def get_teams(db: Session, skip: int = 0, limit: int = 0) -> List[Team]:
    statement = select(Team).offset(skip).limit(limit)
    return list(db.exec(statement).all())


def create_team(db: Session, team: TeamCreate) -> Team:
    db_team = Team.model_validate(team)
    return add_to_db(db, db_team)


def update_team(db: Session, team_data: dict, team_id: uuid.UUID) -> Optional[Team]:
    team_data["updated_at"] = datetime.now()
    return update_to_db(db, team_id, team_data, Team)


def delete_team(db: Session, team_id: uuid.UUID) -> bool:
    return delete_from_db(db, team_id, Team)