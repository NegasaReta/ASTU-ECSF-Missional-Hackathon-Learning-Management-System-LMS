from typing import Annotated, Type
import uuid
from fastapi import Depends, HTTPException, status
from typing import Any
from sqlmodel import SQLModel, Session
from app.database.db import get_session


database_dependency = Annotated[Session, Depends(get_session)]


def add_to_db(db: Session, model: Any):
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def delete_from_db(db: Session, id: uuid.UUID, model: Type[SQLModel]) -> bool:
    delete = db.get(model, id)
    if not delete:
        return False
    db.delete(delete)
    db.commit()
    return True


def update_to_db(db: Session, id: uuid.UUID, data: dict, model: Type[SQLModel]):
    update = db.get(model, id)
    if not update:
        return None
    for key, value in data.items():
        setattr(update, key, value)
    return add_to_db(db, update)


raised_error = HTTPException(
    detail="Not Found!!", status_code=status.HTTP_404_NOT_FOUND
)
