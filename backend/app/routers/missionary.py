from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.model.models import Missionary, MissionaryCreate
import uuid
from app.crud.missionary import (
    get_missionary,
    get_missionarys,
    create_missionary,
    delete_missionary,
    update_missionary,
)
from app.utils.helpers import database_dependency

router = APIRouter(prefix="/missionary", tags=["Missionary"])


@router.get("/", response_model=List[Missionary])
def read_missionarys(db: database_dependency, skip: int = 0, limit: int = 100):
    return get_missionarys(db=db, skip=skip, limit=limit)


@router.get("/{missionary_id}", response_model=Missionary)
def read_missionary(missionary_id: uuid.UUID, db: database_dependency):
    missionary = get_missionary(db=db, missionary_id=missionary_id)
    if not missionary:
        raise HTTPException(detail="Not found!", status_code=status.HTTP_404_NOT_FOUND)
    return missionary


@router.post("/", response_model=Missionary)
def add_missionary(missionary: MissionaryCreate, db: database_dependency):
    return create_missionary(db=db, missionary=missionary)


@router.put("/", response_model=Missionary)
def put_missionary(
    missionary_id: uuid.UUID,
    missionary_data: dict,
    db: database_dependency,
):
    update = update_missionary(
        db=db, missionary_id=missionary_id, missionary_data=missionary_data
    )
    if not update:
        raise HTTPException(detail="Not Found!!", status_code=status.HTTP_404_NOT_FOUND)
    return update


@router.delete("/", response_model=dict)
def remove_missionary(missionary_id: uuid.UUID, db: database_dependency):
    delete = delete_missionary(db=db, missionary_id=missionary_id)
    if not delete:
        raise HTTPException(detail="Not Found!!", status_code=status.HTTP_404_NOT_FOUND)
    return {"ok": True}
