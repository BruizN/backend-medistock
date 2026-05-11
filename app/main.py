from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine
from app.core.exceptions import add_exception_handlers
from app.models.base import BaseTable
from app.modules.inventory.models import Product  # noqa: F401
from app.modules.auth.models import User  # noqa: F401
from app.modules.orders.models import Order, OrderItem  # noqa: F401
from app.modules.inventory.router import router as inventory_router
from app.modules.auth.router import router as auth_router
from app.modules.orders.router import router as orders_router


from sqlmodel import select
from app.core.db import async_session_maker
from app.core.security import hash_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (in production use Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.create_all)
        
    # Seed data
    async with async_session_maker() as session:
        # Check if user exists
        result = await session.exec(select(User).where(User.email == "admin@medistock.com"))
        user = result.first()
        if not user:
            # Create seed user
            hashed_pw = hash_password("Gamer_2026")
            seed_user = User(email="admin@medistock.com", hashed_password=hashed_pw, role="admin")
            session.add(seed_user)
            
            # Create seed products
            products = [
                Product(code="M-SIGNOS-01", name="Monitor Multiparámetro", description="Monitor clínico avanzado para UCI", price=1200000.0, stock=10),
                Product(code="G-NIT-01", name="Guantes de Nitrilo (Caja 100u)", description="Guantes desechables sin polvo", price=8500.0, stock=500),
                Product(code="J-5ML-01", name="Jeringas 5ml (Caja 50u)", description="Jeringas con aguja 21G", price=4500.0, stock=200),
                Product(code="S-FIS-01", name="Suero Fisiológico 500ml", description="Solución salina 0.9%", price=1200.0, stock=1000)
            ]
            session.add_all(products)
            await session.commit()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allowing all origins. Should be specific in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(inventory_router, prefix=settings.API_V1_STR)
app.include_router(orders_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to MEDISTOCK API"}