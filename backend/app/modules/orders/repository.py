import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.modules.orders.models import Order, OrderItem

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()
        return order
        
    async def create_order_item(self, item: OrderItem) -> OrderItem:
        self.session.add(item)
        await self.session.flush()
        return item
        
    async def get_order(self, order_id: uuid.UUID) -> Order | None:
        return await self.session.get(Order, order_id)
        
    async def get_order_items(self, order_id: uuid.UUID) -> list[OrderItem]:
        statement = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await self.session.exec(statement)
        return list(result.all())

    async def update_order(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
