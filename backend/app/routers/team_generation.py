from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import random

from app.database.db import get_db
from app.model.models import Missionary, Site, Team, TeamMember  # ensure these models exist

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
        "amharic_only": amharic_only
    }

@router.post("/generate-teams", response_model=Dict[str, Any])
def generate_teams(db: Session = Depends(get_db)):
    missionaries: List[Missionary] = db.query(Missionary).all()
    sites: List[Site] = db.query(Site).all()

    total_missionaries = len(missionaries)
    n_sites = len(sites)
    min_needed = n_sites * 3
    surplus = total_missionaries - min_needed

    # Categorize missionaries
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
    team_members = []

    # Shuffle all categories for random selection
    random.shuffle(cats["bilingual"])
    random.shuffle(cats["experienced"])
    random.shuffle(cats["fresh"])
    random.shuffle(cats["senior"])

    # Assign core teams
    for site_idx, site in enumerate(sites):
        team_members_list = []
        # Team leader: bilingual & experienced
        leader = None
        leader_candidate = None
        # Try to find bilingual AND experienced
        for m in cats["bilingual"]:
            if m.id in assigned:
                continue
            if m.experience:
                leader = m
                break
            elif not leader_candidate:
                leader_candidate = m

        if not leader:
            # Use bilingual only as leader, add experienced separately
            leader = leader_candidate

        if not leader or leader.id in assigned:
            raise HTTPException(400, f"Cannot assign bilingual leader to site {site.name}")

        assigned.add(leader.id)

        # Team object
        team = Team(site_id=site.id, leader_id=leader.id)
        db.add(team)
        db.flush()  # Get team.id

        team_members_list.append({
            "missionary_id": leader.id,
            "role": "Leader",
            "full_name": leader.full_name,
            "batch": leader.batch,
            "language": leader.language,
            "experience": leader.experience,
        })
        team_member_rec = TeamMember(team_id=team.id, missionary_id=leader.id, role="Leader")
        db.add(team_member_rec)

        # Experienced member (if not already)
        if not leader.experience:
            exp_member = next(m for m in cats["experienced"] if m.id not in assigned)
            assigned.add(exp_member.id)
            team_members_list.append({
                "missionary_id": exp_member.id,
                "role": "Experienced",
                "full_name": exp_member.full_name,
                "batch": exp_member.batch,
                "language": exp_member.language,
                "experience": exp_member.experience,
            })
            team_member_rec = TeamMember(team_id=team.id, missionary_id=exp_member.id, role="Experienced")
            db.add(team_member_rec)

        # Fresh member (not same as leader/exp)
        fresh_member = next(m for m in cats["fresh"] if m.id not in assigned)
        assigned.add(fresh_member.id)
        team_members_list.append({
            "missionary_id": fresh_member.id,
            "role": "Fresh",
            "full_name": fresh_member.full_name,
            "batch": fresh_member.batch,
            "language": fresh_member.language,
            "experience": fresh_member.experience,
        })
        team_member_rec = TeamMember(team_id=team.id, missionary_id=fresh_member.id, role="Fresh")
        db.add(team_member_rec)

        # Senior member (not same as above)
        senior_member = next(m for m in cats["senior"] if m.id not in assigned)
        assigned.add(senior_member.id)
        team_members_list.append({
            "missionary_id": senior_member.id,
            "role": "Senior",
            "full_name": senior_member.full_name,
            "batch": senior_member.batch,
            "language": senior_member.language,
            "experience": senior_member.experience,
        })
        team_member_rec = TeamMember(team_id=team.id, missionary_id=senior_member.id, role="Senior")
        db.add(team_member_rec)

        teams.append({
            "team_id": team.id,
            "site": site.name,
            "leader": leader.full_name,
            "members": team_members_list
        })

    # Distribute surplus missionaries as 4th members
    if surplus > 0:
        # Collect all unassigned Oromo-only or Amharic-only missionaries
        surplus_candidates = [m for m in missionaries if m.id not in assigned and m.language in ["Afan Oromo", "Amharic"]]
        random.shuffle(surplus_candidates)
        # Only as many as available, and not more than number of sites
        n_fourth = min(len(surplus_candidates), n_sites)
        indexes = random.sample(range(n_sites), n_fourth)
        for idx, team_idx in enumerate(indexes):
            m = surplus_candidates[idx]
            assigned.add(m.id)
            team_id = teams[team_idx]["team_id"]

            # Update DB
            team_member_rec = TeamMember(team_id=team_id, missionary_id=m.id, role="Extra")
            db.add(team_member_rec)

            # Update output
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