from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import create_db_and_tables
from app.routers import admin, missionary, recipient, auth, team_generation
from app.core.dependencies import get_current_user

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:5500",  # your frontend port
    "http://127.0.0.1:3000",
    # Add your deployed frontend URL if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # can also use ["*"] to allow all
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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def main(user=Depends(get_current_user)):
    return {"message": "home page"}
