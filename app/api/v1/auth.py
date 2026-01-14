from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, _users


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def token(form: OAuth2PasswordRequestForm = Depends()):
    if form.username in _users and form.password == "test":
        token = create_access_token(subject=form.username, roles=_users[form.username]["roles"])
        return {"access_token": token, "token_type": "bearer"}
    return {"detail": "invalid_credentials"}
