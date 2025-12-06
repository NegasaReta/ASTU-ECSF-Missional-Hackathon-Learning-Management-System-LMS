from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import create_db_and_tables
from app.routers import admin, missionary, recipient, auth, team_generation, site, team, team_member
from app.core.dependencies import get_current_user

app = FastAPI()

# Configure CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(team_generation.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(missionary.router)
app.include_router(recipient.router)
app.include_router(site.router)
app.include_router(team.router)
app.include_router(team_member.router)  



@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def main(user=Depends(get_current_user)):
    return {"message": "home page"}
