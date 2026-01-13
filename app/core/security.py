import os
import time
import secrets
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


SECRET_KEY = os.getenv("DELIVERY_API_SECRET", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")

# demo users for in-memory auth
_users = {
    "admin": {"username": "admin", "roles": ["admin", "dispatcher"]},
    "courier": {"username": "courier", "roles": ["courier"]},
    "customer": {"username": "customer", "roles": ["customer"]},
}


def create_access_token(subject: str, roles: Optional[list] = None, expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    now = int(time.time())
    payload = {"sub": subject, "roles": roles or [], "iat": now, "exp": now + expires_in}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token_expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    payload = decode_token(token)
    username = payload.get("sub")
    if not username or username not in _users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found")        
    return {"username": username, "roles": payload.get("roles", [])}


async def login(form: OAuth2PasswordRequestForm = Depends()):
    # demo: accept password "test" for predefined users
    if form.username in _users and form.password == "test":
        token = create_access_token(subject=form.username, roles=_users[form.username]["roles"])      
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")       
