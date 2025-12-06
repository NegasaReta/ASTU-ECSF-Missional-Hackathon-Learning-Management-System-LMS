from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import create_db_and_tables
from app.routers import admin, missionary, recipient, auth, team_generation, site, team, team_member
from app.core.dependencies import get_current_user
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


templates = Jinja2Templates(directory="app/templates")
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


#enable this to use templates from jinja2
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/communication", response_class=HTMLResponse)
def communication(request: Request):
    return templates.TemplateResponse("communication.html", {"request": request})

@app.get("/attendance", response_class=HTMLResponse)
def attendance(request: Request):
    return templates.TemplateResponse("attendance.html", {"request": request})

@app.get("/pairing", response_class=HTMLResponse)
def pairing(request: Request):
    return templates.TemplateResponse("pairing.html", {"request": request})
@app.get("/")
def main(user=Depends(get_current_user)):
    return {"message": "home page"}
