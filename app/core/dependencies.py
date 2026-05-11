import jwt
from fastapi import Depends, HTTPException, status
from typing import AsyncGenerator
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.modules.auth.models import User
from app.core.db import async_session_maker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an async database session."""
    async with async_session_maker() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        secret_key = getattr(settings, "SECRET_KEY", "medistock_super_secret_key")
        algorithm = getattr(settings, "ALGORITHM", "HS256")
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user

