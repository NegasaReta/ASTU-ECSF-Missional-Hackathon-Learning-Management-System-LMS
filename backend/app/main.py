from fastapi import FastAPI
from app.database.db import create_db_and_tables
from app.routers import admin, missionary, recipient

app = FastAPI()


app.include_router(admin.router)
app.include_router(missionary.router)
app.include_router(recipient.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def main():
    return {"message": "home page"}
