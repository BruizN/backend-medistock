import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.schemas import Token, UserCreate


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)
        return result.first()

    async def create_user(self, user_in: UserCreate) -> User:
        existing_user = await self.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_pw = hash_password(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_pw,
            role=user_in.role
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def authenticate(self, email: str, password: str) -> Token:
        user = await self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
        return Token(access_token=access_token, token_type="bearer")
