from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt
import requests
from app.core.config import settings

app = FastAPI()
bearer = HTTPBearer()

JWKS_URL = settings.SUPABASE_JWT_KEY
jwks = requests.get(JWKS_URL).json()


def get_public_key(kid):
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    return None


def get_current_user(credentials=Depends(bearer)):
    token = credentials.credentials

    header = jwt.get_unverified_header(token)
    public_key = get_public_key(header["kid"])

    if public_key is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    try:
        payload = jwt.decode(
            token, public_key, algorithms=["ES256"], audience="authenticated"
        )
        return payload
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
