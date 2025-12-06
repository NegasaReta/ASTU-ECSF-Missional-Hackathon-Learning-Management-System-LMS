from datetime import datetime
from typing import List, Optional
from app.model.models import Missionary, MissionaryCreate
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
import uuid

from app.utils.helpers import add_to_db, delete_from_db, update_to_db


def get_missionary(db: Session, missionary_id: uuid.UUID):
    return db.get(Missionary, missionary_id)


def get_missionarys(db: Session, skip: int = 0, limit: int = 0) -> List[Missionary]:
    statement = select(Missionary).offset(skip).limit(limit)
    return list(db.exec(statement).all())


def create_missionary(db: Session, missionary: MissionaryCreate) -> Missionary:
    db_missionary = Missionary.model_validate(missionary)
    return add_to_db(db, db_missionary)


def update_missionary(
    db: Session, missionary_data: dict, missionary_id: uuid.UUID
) -> Optional[Missionary]:
    missionary_data["updated_at"] = datetime.now()
    return update_to_db(db, missionary_id, missionary_data, Missionary)


def delete_missionary(db: Session, missionary_id: uuid.UUID) -> bool:
    return delete_from_db(db, missionary_id, Missionary)


def get_missionary_full(db: Session, missionary_id: uuid.UUID):
    statement = (
        select(Missionary)
        .where(Missionary.id == missionary_id)
        .options(selectinload(Missionary.recipients))  # type: ignore
    )
    result = db.exec(statement).first()
    return result
