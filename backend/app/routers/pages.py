from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/communication", response_class=HTMLResponse)
async def communication_page(request: Request):
    return templates.TemplateResponse("communication.html", {"request": request})

@router.get("/attendance", response_class=HTMLResponse)
async def attendance_page(request: Request):
    return templates.TemplateResponse("attendance.html", {"request": request})

@router.get("/pairing", response_class=HTMLResponse)
async def pairing_page(request: Request):
    return templates.TemplateResponse("pairing.html", {"request": request})

@router.get("/media", response_class=HTMLResponse)
async def media_page(request: Request):
    return templates.TemplateResponse("media.html", {"request": request})

@router.get("/members", response_class=HTMLResponse)
async def members_page(request: Request):
    return templates.TemplateResponse("members.html", {"request": request})

@router.get("/mission", response_class=HTMLResponse)
async def mission_page(request: Request):
    return templates.TemplateResponse("mission.html", {"request": request})

@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

@router.get("/userdashboard", response_class=HTMLResponse)
async def user_dashboard_page(request: Request):
    return templates.TemplateResponse("userdashboard.html", {"request": request})

@router.get("/password-reset", response_class=HTMLResponse)
async def password_reset_page(request: Request):
    return templates.TemplateResponse("password-reset.html", {"request": request})

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("adminlogin.html", {"request": request})
