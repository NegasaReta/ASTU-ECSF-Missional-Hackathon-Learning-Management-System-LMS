from datetime import datetime
from typing import List, Optional
from app.model.models import Admin, AdminCreate
from sqlmodel import Session, select
import uuid

from app.utils.helpers import add_to_db, delete_from_db, update_to_db


def get_admin(db: Session, admin_id: uuid.UUID):
    return db.get(Admin, admin_id)


def get_admins(db: Session, skip: int = 0, limit: int = 0) -> List[Admin]:
    statement = select(Admin).offset(skip).limit(limit)
    return list(db.exec(statement).all())


def create_admin(db: Session, admin: AdminCreate) -> Admin:
    db_admin = Admin.model_validate(admin)
    return add_to_db(db, db_admin)


def update_admin(db: Session, admin_data: dict, admin_id: uuid.UUID) -> Optional[Admin]:
    admin_data["updated_at"] = datetime.now()
    return update_to_db(db, admin_id, admin_data, Admin)


def delete_admin(db: Session, admin_id: uuid.UUID) -> bool:
    return delete_from_db(db, admin_id, Admin)
