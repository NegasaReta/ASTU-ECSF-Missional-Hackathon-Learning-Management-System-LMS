from datetime import datetime
from typing import List, Optional
import uuid
from sqlmodel import Session, select

from app.model.models import Site, SiteCreate
from app.utils.helpers import add_to_db, delete_from_db, update_to_db


def get_site(db: Session, site_id: uuid.UUID):
    return db.get(Site, site_id)


def get_sites(db: Session, skip: int = 0, limit: int = 0) -> List[Site]:
    statement = select(Site).offset(skip).limit(limit)
    return list(db.exec(statement).all())


def create_site(db: Session, site: SiteCreate) -> Site:
    db_site = Site.model_validate(site)
    return add_to_db(db, db_site)


def update_site(db: Session, site_data: dict, site_id: uuid.UUID) -> Optional[Site]:
    site_data["updated_at"] = datetime.now()
    return update_to_db(db, site_id, site_data, Site)


def delete_site(db: Session, site_id: uuid.UUID) -> bool:
    return delete_from_db(db, site_id, Site)