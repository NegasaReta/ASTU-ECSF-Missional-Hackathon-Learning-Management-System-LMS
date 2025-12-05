from datetime import datetime
from typing import List, Optional
from app.model.models import Recipient, RecipientCreate
from sqlmodel import Session, select
import uuid

from app.utils.helpers import add_to_db, delete_from_db, update_to_db


def get_recipient(db: Session, recipient_id: uuid.UUID):
    return db.get(Recipient, recipient_id)


def get_recipients(db: Session, skip: int = 0, limit: int = 0) -> List[Recipient]:
    statement = select(Recipient).offset(skip).limit(limit)
    return list(db.exec(statement).all())


def create_recipient(db: Session, recipient: RecipientCreate) -> Recipient:
    db_recipient = Recipient.model_validate(recipient)
    return add_to_db(db, db_recipient)


def update_recipient(
    db: Session, recipient_data: dict, recipient_id: uuid.UUID
) -> Optional[Recipient]:
    recipient_data["updated_at"] = datetime.now()
    return update_to_db(db, recipient_id, recipient_data, Recipient)


def delete_recipient(db: Session, recipient_id: uuid.UUID) -> bool:
    return delete_from_db(db, recipient_id, Recipient)
