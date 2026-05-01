import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import get_db_session
from app.modules.inventory.repository import ProductRepository
from app.modules.inventory.schemas import ProductCreate, ProductResponse, ProductUpdate
from app.modules.inventory.service import ProductService

router = APIRouter(prefix="/products", tags=["inventory"])


def get_product_service(session: AsyncSession = Depends(get_db_session)) -> ProductService:
    repository = ProductRepository(session)
    return ProductService(repository)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate, service: ProductService = Depends(get_product_service)
):
    return await service.create_product(product_in)


@router.get("/", response_model=List[ProductResponse])
async def read_products(
    skip: int = 0, limit: int = 100, service: ProductService = Depends(get_product_service)
):
    return await service.get_products(skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: uuid.UUID, service: ProductService = Depends(get_product_service)
):
    return await service.get_product(product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    product_in: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    return await service.update_product(product_id, product_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID, service: ProductService = Depends(get_product_service)
):
    await service.delete_product(product_id)
