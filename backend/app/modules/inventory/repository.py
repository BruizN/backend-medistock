import uuid
from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.inventory.models import Product
from app.modules.inventory.schemas import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, product_in: ProductCreate) -> Product:
        db_product = Product(**product_in.model_dump())
        self.session.add(db_product)
        await self.session.commit()
        await self.session.refresh(db_product)
        return db_product

    async def get(self, product_id: uuid.UUID) -> Optional[Product]:
        return await self.session.get(Product, product_id)

    async def get_by_code(self, code: str) -> Optional[Product]:
        statement = select(Product).where(Product.code == code)
        result = await self.session.exec(statement)
        return result.first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        statement = select(Product).offset(skip).limit(limit)
        result = await self.session.exec(statement)
        return list(result.all())

    async def update(self, db_product: Product, product_in: ProductUpdate) -> Product:
        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        self.session.add(db_product)
        await self.session.commit()
        await self.session.refresh(db_product)
        return db_product

    async def delete(self, db_product: Product) -> None:
        db_product.is_active = False
        self.session.add(db_product)
        await self.session.commit()
