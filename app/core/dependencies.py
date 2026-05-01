from typing import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an async database session."""
    async with async_session_maker() as session:
        yield session
