from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid

from app.model.models import TeamMember, TeamMemberCreate
from app.crud.team_member import (
    get_team_member,
    get_team_members,
    create_team_member,
    update_team_member,
    delete_team_member,
)
from app.utils.helpers import database_dependency

router = APIRouter(prefix="/team-member", tags=["Team Member"])


@router.get("/", response_model=List[TeamMember])
def read_team_members(db: database_dependency, skip: int = 0, limit: int = 100):
    return get_team_members(db=db, skip=skip, limit=limit)


@router.get("/{team_member_id}", response_model=TeamMember)
def read_team_member(team_member_id: uuid.UUID, db: database_dependency):
    member = get_team_member(db=db, team_member_id=team_member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return member


@router.post("/", response_model=TeamMember)
def add_team_member(team_member: TeamMemberCreate, db: database_dependency):
    return create_team_member(db=db, team_member=team_member)


@router.put("/", response_model=TeamMember)
def put_team_member(
    team_member_id: uuid.UUID,
    team_member_data: dict,
    db: database_dependency,
):
    updated = update_team_member(
        db=db, team_member_id=team_member_id, team_member_data=team_member_data
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found!!")
    return updated


@router.delete("/", response_model=dict)
def remove_team_member(team_member_id: uuid.UUID, db: database_dependency):
    deleted = delete_team_member(db=db, team_member_id=team_member_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found!!")
    return {"ok": True}