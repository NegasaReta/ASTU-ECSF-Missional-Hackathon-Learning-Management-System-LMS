from fastapi import APIRouter, Depends, HTTPException, status
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


@router.post("/register")
def register_user(data: SignupMissionary, session: Session = Depends(get_session)):
    try:
        # Start a database transaction
        with session.begin():  # SQLAlchemy automatically handles commit/rollback
            # 1. Create user in Supabase
            supa_id = supa_register(data.email, data.password)  # type: ignore
            if not supa_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to register in Supabase",
                )

            # 2. Save additional info in your DB
            missionary = Missionary(
                id=supa_id,  # type: ignore
                full_name=data.full_name,
                attendance=data.attendance,
                batch=data.batch,
                phone=data.phone,
                language=data.language,  # type: ignore
                experienced=data.experienced,
                verified=data.verified,
            )

            session.add(missionary)
            # session.commit() is **not** needed here; handled by `with session.begin()`

        # If we reach here, everything succeeded (Atomic + Consistent + Durable)
        return {"message": "User registered successfully", "supabase_id": supa_id}

    except Exception as e:
        # SQLAlchemy automatically rolls back on exception in `session.begin()`
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )
