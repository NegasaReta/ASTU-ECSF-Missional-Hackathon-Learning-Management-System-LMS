from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid

from app.model.models import Site, SiteCreate
from app.crud.site import (
    get_site,
    get_sites,
    create_site,
    update_site,
    delete_site,
)
from app.utils.helpers import database_dependency

router = APIRouter(prefix="/site", tags=["Site"])


@router.get("/", response_model=List[Site])
def read_sites(db: database_dependency, skip: int = 0, limit: int = 100):
    return get_sites(db=db, skip=skip, limit=limit)


@router.get("/{site_id}", response_model=Site)
def read_site(site_id: uuid.UUID, db: database_dependency):
    site = get_site(db=db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return site


@router.post("/", response_model=Site)
def add_site(site: SiteCreate, db: database_dependency):
    return create_site(db=db, site=site)


@router.put("/", response_model=Site)
def put_site(site_id: uuid.UUID, site_data: dict, db: database_dependency):
    updated = update_site(db=db, site_id=site_id, site_data=site_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found!!")
    return updated


@router.delete("/", response_model=dict)
def remove_site(site_id: uuid.UUID, db: database_dependency):
    deleted = delete_site(db=db, site_id=site_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found!!")
    return {"ok": True}