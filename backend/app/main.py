from fastapi import FastAPI, Depends
from app.database.db import create_db_and_tables
from app.routers import admin, missionary, recipient, auth
from app.core.dependencies import get_current_user

app = FastAPI()


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
