from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from uuid import UUID

from app.services.supabase import (
    login as supa_login,
    register_in_supabase as supa_register,
)
from app.model.models import Missionary, Admin
from app.database.db import get_session
from app.utils.helpers import add_to_db

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response


# ----------------------
# Login Route
# ----------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
async def login_route(data: LoginRequest, session: Session = Depends(get_session)):
    try:
        login_data = supa_login(data.email, data.password)
        if not login_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        
        token = login_data["access_token"]
        user_id = login_data["user_id"]
        metadata = login_data.get("metadata", {})
        
        # Get role from Supabase metadata
        role = metadata.get("role", "missionary")  # Default to missionary
        
        # Determine redirect URL based on role
        if role == "admin":
            redirect_url = "/dashboard"
        else:
            redirect_url = "/userdashboard"

        return {
            "access_token": token, 
            "token_type": "bearer",
            "role": role,
            "redirect_url": redirect_url
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ----------------------
# Signup Route
# ----------------------
class SignupRequest(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    password: str
    role: str = "missionary" # "admin" or "missionary"
    
    # Missionary specific (optional)
    batch: int = 1
    language: str = "Both"
    experienced: bool = False
    attendance: bool = False
    verified: bool = False


@router.post("/register")
def register_user(
    user_data: SignupRequest,
    session: Session = Depends(get_session),
):
    try:
        # Register in Supabase with role metadata
        supa_id = supa_register(user_data.email, user_data.password, user_data.role)

        if not supa_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register in Supabase (Email might be taken)",
            )

        # Only create local DB record for missionaries
        # Admins exist only in Supabase with role metadata
        if user_data.role == "missionary":
            with session.begin():
                missionary = Missionary(
                    id=supa_id,  # type: ignore
                    full_name=user_data.full_name,
                    attendance=user_data.attendance,
                    batch=user_data.batch,
                    phone=user_data.phone,
                    language=user_data.language,  # type: ignore
                    experienced=user_data.experienced,
                    verified=user_data.verified,
                )
                session.add(missionary)

        return {"message": "User registered successfully", "supabase_id": supa_id, "role": user_data.role}

    except Exception as e:
        # If DB write fails, Supabase user might still exist. 
        # Ideally we should roll back Supabase user creation, but for now we rely on DB transaction.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


# ----------------------
# User Profile Routes
# ----------------------
from app.core.dependencies import get_current_user

@router.get("/user")
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get current authenticated user's profile
    """
    try:
        user_id = current_user.get("sub")  # JWT subject contains user ID
        
        # Try to fetch from Missionary table first
        missionary = session.get(Missionary, user_id)
        if missionary:
            return {
                "id": str(missionary.id),
                "full_name": missionary.full_name,
                "email": current_user.get("email"),  # From JWT
                "phone": missionary.phone,
                "batch": missionary.batch,
                "language": missionary.language,
                "experienced": missionary.experienced,
                "verified": missionary.verified,
                "role": "missionary"
            }
        
        # If not missionary, user is admin (stored only in Supabase)
        return {
            "id": user_id,
            "email": current_user.get("email"),
            "full_name": current_user.get("user_metadata", {}).get("full_name", "Admin User"),
            "role": "admin"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/update")
async def update_user_profile(
    request: Request,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update authenticated user's profile
    """
    try:
        user_id = current_user.get("sub")
        data = await request.json()
        
        # Try to update Missionary record
        missionary = session.get(Missionary, user_id)
        if missionary:
            # Update fields if provided
            if "full_name" in data:
                missionary.full_name = data["full_name"]
            if "phone" in data:
                missionary.phone = data["phone"]
            if "language" in data:
                missionary.language = data["language"]
            
            session.add(missionary)
            session.commit()
            
            return {"message": "Profile updated successfully"}
        
        # Admin users don't have local DB records
        return {"message": "Admin profile update not implemented"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
