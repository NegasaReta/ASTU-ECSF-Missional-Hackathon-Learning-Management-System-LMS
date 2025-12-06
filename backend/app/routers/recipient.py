from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.model.models import Recipient, RecipientCreate
import uuid
from app.crud.recipient import (
    get_recipient,
    get_recipients,
    create_recipient,
    delete_recipient,
    update_recipient,
)
from app.utils.helpers import database_dependency

router = APIRouter(prefix="/recipient", tags=["Recipient"])


@router.get("/", response_model=List[Recipient])
def read_recipients(
    db: database_dependency,
    skip: int = 0,
    limit: int = 100,
):
    return get_recipients(db=db, skip=skip, limit=limit)


@router.get("/{recipient_id}", response_model=Recipient)
def read_recipient(recipient_id: uuid.UUID, db: database_dependency):
    recipient = get_recipient(db=db, recipient_id=recipient_id)
    if not recipient:
        raise HTTPException(detail="Not found!", status_code=status.HTTP_404_NOT_FOUND)
    return recipient


@router.post("/", response_model=Recipient)
def add_recipient(recipient: RecipientCreate, db: database_dependency):
    return create_recipient(db=db, recipient=recipient)


@router.put("/", response_model=Recipient)
def put_recipient(
    recipient_id: uuid.UUID,
    recipient_data: dict,
    db: database_dependency,
):
    update = update_recipient(
        db=db, recipient_id=recipient_id, recipient_data=recipient_data
    )
    if not update:
        raise HTTPException(detail="Not Found!!", status_code=status.HTTP_404_NOT_FOUND)
    return update


@router.delete("/", response_model=dict)
def remove_recipient(recipient_id: uuid.UUID, db: database_dependency):
    delete = delete_recipient(db=db, recipient_id=recipient_id)
    if not delete:
        raise HTTPException(detail="Not Found!!", status_code=status.HTTP_404_NOT_FOUND)
    return {"ok": True}
