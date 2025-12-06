from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid

from app.model.models import Team, TeamCreate
from app.crud.team import (
    get_team,
    get_teams,
    create_team,
    update_team,
    delete_team,
)
from app.utils.helpers import database_dependency

router = APIRouter(prefix="/team", tags=["Team"])


@router.get("/", response_model=List[Team])
def read_teams(db: database_dependency, skip: int = 0, limit: int = 100):
    return get_teams(db=db, skip=skip, limit=limit)


@router.get("/{team_id}", response_model=Team)
def read_team(team_id: uuid.UUID, db: database_dependency):
    team = get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return team


@router.post("/", response_model=Team)
def add_team(team: TeamCreate, db: database_dependency):
    return create_team(db=db, team=team)


@router.put("/", response_model=Team)
def put_team(team_id: uuid.UUID, team_data: dict, db: database_dependency):
    updated = update_team(db=db, team_id=team_id, team_data=team_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found!!")
    return updated


@router.delete("/", response_model=dict)
def remove_team(team_id: uuid.UUID, db: database_dependency):
    deleted = delete_team(db=db, team_id=team_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found!!")
    return {"ok": True}