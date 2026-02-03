# app/routers/auth_admin.py

from fastapi import APIRouter, Request, HTTPException
from app.schemas.auth import LoginSyncRequest
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["Admin Auth"])

@router.post("/login-admin-sync")
async def login_admin_sync(data: LoginSyncRequest, request: Request):
    if request.headers.get("X-Internal-Key") != settings.internal_key:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if not data.is_admin:
        raise HTTPException(status_code=403, detail="Not an admin user")

    token = create_access_token({
        "sub": str(data.user_id),
        "username": data.username,
        "is_admin": True
    })

    return {"access_token": token, "token_type": "bearer"}
