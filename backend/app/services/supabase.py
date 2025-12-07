from supabase import create_client
from app.core.config import settings
from pydantic import EmailStr
from typing import Optional

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def login(email: EmailStr, password: str) -> Optional[dict]:
    response = supabase.auth.sign_in_with_password(
        {"email": email, "password": password}
    )
    # Access token as an attribute
    token = getattr(response.session, "access_token", None)
    user_id = response.user.id if response.user else None
    user_metadata = response.user.user_metadata if response.user else {}
    
    if token and user_id:
        return {
            "access_token": token, 
            "user_id": user_id,
            "metadata": user_metadata
        }
    return None


def register_in_supabase(email: EmailStr, password: str, role: str = "missionary") -> Optional[str]:
    """
    Register user in Supabase with role metadata.
    role: "admin" or "missionary"
    """
    response = supabase.auth.sign_up({
        "email": email, 
        "password": password,
        "options": {
            "data": {
                "role": role
            }
        }
    })

    if response.user is None:
        return None

    return response.user.id  # Supabase UUID
