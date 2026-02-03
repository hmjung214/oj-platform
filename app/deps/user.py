from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.models import User
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    print(">>> [DEBUG] get_current_user called")
    print(">>> [DEBUG] Received token:", token)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        print(">>> [DEBUG] JWT payload:", payload)
        print(">>> [DEBUG] Extracted username:", username)
        if username is None:
            print(">>> [DEBUG] Username is None!")
            raise credentials_exception
    except JWTError as e:
        print(">>> [DEBUG] JWT Decode Error:", str(e))
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if user is None:
        print(">>> [DEBUG] USER NOT FOUND in DB:", username)
        raise credentials_exception

    print(">>> [DEBUG] USER FOUND:", user.username)
    return user

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

