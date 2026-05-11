from contextlib import asynccontextmanager
from fastapi import FastAPI
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (in production use Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

add_exception_handlers(app)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(inventory_router, prefix=settings.API_V1_STR)
app.include_router(orders_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to MEDISTOCK API"}