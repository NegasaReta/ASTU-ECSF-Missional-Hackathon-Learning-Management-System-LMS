from supabase import create_client
from app.core.config import settings
from pydantic import EmailStr
from typing import Optional

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def login(email: EmailStr, password: str) -> Optional[str]:
    response = supabase.auth.sign_in_with_password(
        {"email": email, "password": password}
    )
    # Access token as an attribute
    token = getattr(response.session, "access_token", None)
    return token


def register_in_supabase(email: EmailStr, password: str) -> Optional[str]:
    response = supabase.auth.sign_up({"email": email, "password": password})

    if response.user is None:
        return None

    return response.user.id  # Supabase UUID
