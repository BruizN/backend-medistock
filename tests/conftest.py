import os
from dotenv import load_dotenv
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.main import app
from app.core.dependencies import get_db_session 
from app.modules.inventory.models import Product

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("❌ ERROR: No se encontró la variable TEST_DATABASE_URL. Revisa tu .env o tu CI.")

@pytest.fixture(scope="session")
def engine():
    return create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            join_transaction_mode="create_savepoint"
        )
        async with session_factory() as session:
            yield session
        await transaction.rollback()

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture
async def product_factory(db_session):
    async def _create_product(
        code: str, 
        name: str, 
        description: str | None = None, 
        price: float = 0.0,
        stock: int = 0,
        is_active: bool = True
    ):
        product = Product(
            code=code,
            name=name, 
            description=description, 
            price=price,
            stock=stock,
            is_active=is_active
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product
    return _create_product
