from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.model.models import Admin, AdminCreate
import uuid
from app.crud.admin import (
    get_admin,
    get_admins,
    create_admin,
    delete_admin,
    update_admin,
)
from app.utils.helpers import database_dependency

router = APIRouter(prefix="/admins", tags=["Admin"])


@router.get("/", response_model=List[Admin])
def read_admins(db: database_dependency, skip: int = 0, limit: int = 100):
    return get_admins(db=db, skip=skip, limit=limit)


@router.get("/{admin_id}", response_model=Admin)
def read_admin(admin_id: uuid.UUID, db: database_dependency):
    admin = get_admin(db=db, admin_id=admin_id)
    if not admin:
        raise HTTPException(detail="Not found!", status_code=status.HTTP_404_NOT_FOUND)
    return admin


@router.post("/", response_model=Admin)
def add_admin(admin: AdminCreate, db: database_dependency):
    return create_admin(db=db, admin=admin)


@router.put("/", response_model=Admin)
def put_admin(
    admin_id: uuid.UUID,
    admin_data: dict,
    db: database_dependency,
):
    update = update_admin(db=db, admin_id=admin_id, admin_data=admin_data)
    if not update:
        raise HTTPException(detail="Not Found!!", status_code=status.HTTP_404_NOT_FOUND)
    return update


@router.delete("/", response_model=dict)
def remove_admin(admin_id: uuid.UUID, db: database_dependency):
    delete = delete_admin(db=db, admin_id=admin_id)
    if not delete:
        raise HTTPException(detail="Not Found!!", status_code=status.HTTP_404_NOT_FOUND)
    return {"ok": True}
