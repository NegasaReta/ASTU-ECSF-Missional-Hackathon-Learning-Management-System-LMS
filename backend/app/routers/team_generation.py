from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import random
from sqlmodel import Session

from app.database.db import get_session
from app.model.models import Missionary, Site, Team, TeamMember

router = APIRouter()

def get_categories(missionaries: List[Missionary]):
    bilingual = [m for m in missionaries if m.language == "Both"]
    experienced = [m for m in missionaries if m.experience]
    fresh = [m for m in missionaries if m.batch in [1, 2]]
    senior = [m for m in missionaries if m.batch in [3, 4, 5]]
    oromo_only = [m for m in missionaries if m.language == "Afan Oromo"]
    amharic_only = [m for m in missionaries if m.language == "Amharic"]
    return {
        "bilingual": bilingual,
        "experienced": experienced,
        "fresh": fresh,
        "senior": senior,
        "oromo_only": oromo_only,
        "amharic_only": amharic_only,
    }

@router.post("/generate-teams", response_model=Dict[str, Any])
def generate_teams(db: Session = Depends(get_session)):
    missionaries: List[Missionary] = db.query(Missionary).all()
    sites: List[Site] = db.query(Site).all()

    total_missionaries = len(missionaries)
    n_sites = len(sites)
    min_needed = n_sites * 3
    surplus = total_missionaries - min_needed

    cats = get_categories(missionaries)
    if len(cats["bilingual"]) < n_sites:
        raise HTTPException(400, f"Not enough bilingual missionaries: {len(cats['bilingual'])} available, {n_sites} needed")
    if len(cats["experienced"]) < n_sites:
        raise HTTPException(400, f"Not enough experienced missionaries: {len(cats['experienced'])} available, {n_sites} needed")
    if len(cats["fresh"]) < n_sites:
        raise HTTPException(400, f"Not enough fresh missionaries: {len(cats['fresh'])} available, {n_sites} needed")
    if len(cats["senior"]) < n_sites:
        raise HTTPException(400, f"Not enough senior missionaries: {len(cats['senior'])} available, {n_sites} needed")

    assigned = set()
    teams = []

    random.shuffle(cats["bilingual"])
    random.shuffle(cats["experienced"])
    random.shuffle(cats["fresh"])
    random.shuffle(cats["senior"])

    for site in sites:
        team_members_list = []

        leader = None
        leader_candidate = None
        for m in cats["bilingual"]:
            if m.id in assigned:
                continue
            if m.experience:
                leader = m
                break
            elif not leader_candidate:
                leader_candidate = m

        if not leader:
            leader = leader_candidate
        if not leader or leader.id in assigned:
            raise HTTPException(400, f"Cannot assign bilingual leader to site {site.name}")

        assigned.add(leader.id)

        team = Team(site_id=site.id, leader_id=leader.id)
        db.add(team)
        db.flush()

        def add_member(m: Missionary, role: str):
            team_members_list.append({
                "missionary_id": m.id,
                "role": role,
                "full_name": m.full_name,
                "batch": m.batch,
                "language": m.language,
                "experience": m.experience,
            })
            db.add(TeamMember(
                team_id=team.id,
                missionary_id=m.id,
                role=role,
                experience=m.experience,
                language=m.language,
            ))
            assigned.add(m.id)

        add_member(leader, "Leader")

        if not leader.experience:
            exp_member = next(m for m in cats["experienced"] if m.id not in assigned)
            add_member(exp_member, "Experienced")

        fresh_member = next(m for m in cats["fresh"] if m.id not in assigned)
        add_member(fresh_member, "Fresh")

        senior_member = next(m for m in cats["senior"] if m.id not in assigned)
        add_member(senior_member, "Senior")

        teams.append({
            "team_id": team.id,
            "site": site.name,
            "leader": leader.full_name,
            "members": team_members_list,
        })

    if surplus > 0:
        surplus_candidates = [m for m in missionaries if m.id not in assigned and m.language in ["Afan Oromo", "Amharic"]]
        random.shuffle(surplus_candidates)
        n_fourth = min(len(surplus_candidates), n_sites)
        indexes = random.sample(range(n_sites), n_fourth)
        for idx, team_idx in enumerate(indexes):
            m = surplus_candidates[idx]
            assigned.add(m.id)
            team_id = teams[team_idx]["team_id"]
            db.add(TeamMember(
                team_id=team_id,
                missionary_id=m.id,
                role="Extra",
                experience=m.experience,
                language=m.language,
            ))
            teams[team_idx]["members"].append({
                "missionary_id": m.id,
                "role": "Extra",
                "full_name": m.full_name,
                "batch": m.batch,
                "language": m.language,
                "experience": m.experience,
            })

    db.commit()
    return {"teams": teams}