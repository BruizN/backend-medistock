import uuid
from typing import List

from fastapi import HTTPException

from app.modules.inventory.repository import ProductRepository
from app.modules.inventory.schemas import ProductCreate, ProductUpdate, ProductResponse


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def create_product(self, product_in: ProductCreate) -> ProductResponse:
        existing = await self.repository.get_by_code(product_in.code)
        if existing:
            raise HTTPException(status_code=400, detail="Product code already exists")
        return await self.repository.create(product_in)

    async def get_product(self, product_id: uuid.UUID) -> ProductResponse:
        product = await self.repository.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def get_products(self, skip: int = 0, limit: int = 100) -> List[ProductResponse]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update_product(self, product_id: uuid.UUID, product_in: ProductUpdate) -> ProductResponse:
        product = await self.repository.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return await self.repository.update(product, product_in)

    async def delete_product(self, product_id: uuid.UUID) -> None:
        product = await self.repository.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        await self.repository.delete(product)
