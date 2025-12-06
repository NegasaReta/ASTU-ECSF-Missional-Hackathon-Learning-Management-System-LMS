from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from app.services.supabase import login

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
async def login_route(request: Request, data: LoginRequest):
    try:
        token = login(data.email, data.password)
        if not token:
            # This will properly return 401 to the user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        # Re-raise so FastAPI handles it properly
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
