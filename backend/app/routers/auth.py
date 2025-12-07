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
from app.model.models import Missionary
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
async def login_route(data: LoginRequest):
    try:
        token = supa_login(data.email, data.password)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ----------------------
# Signup Route
# ----------------------
class SignupMissionary(BaseModel):
    full_name: str
    batch: int
    phone: str
    language: str
    experienced: bool
    attendance: bool
    verified: bool
    email: EmailStr
    password: str


from fastapi import Form


@router.post("/register")
def register_user(
    user_data: SignupMissionary,
    session: Session = Depends(get_session),
):
    try:
        with session.begin():
            supa_id = supa_register(user_data.email, user_data.password)

            if not supa_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to register in Supabase",
                )

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

        return {"message": "User registered successfully", "supabase_id": supa_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )
