from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, func, asc, desc

from app.models.entities.order_model import Order
from app.models.schemas.order_schema import OrderCreate, OrderUpdate
from app.utils.enum import OrderType, OrderStatus


class OrderDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order: OrderCreate) -> Order:
        """Create a new order"""
        db_order = Order(**order.model_dump())
        self.session.add(db_order)
        await self.session.flush()
        await self.session.refresh(db_order)
        return db_order

    async def get_all_orders(self) -> List[Order]:
        """Get all orders"""
        result = await self.session.execute(select(Order))
        return list(result.scalars().all())

    async def get_order_by_id(self, order_id: int) -> Order | None:
        """Get an order by ID"""
        result = await self.session.execute(select(Order).options(selectinload(Order.jobs)).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def update_order(self, order_id: int, order_update: OrderUpdate) -> Order | None:
        """Update an order"""
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        db_order = result.scalar_one_or_none()

        if db_order:
            update_data = order_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_order, field, value)

            await self.session.flush()
            await self.session.refresh(db_order)

        return db_order

    async def delete_order(self, order_id: int) -> bool:
        """Delete an order"""
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        db_order = result.scalar_one_or_none()

        if db_order:
            await self.session.delete(db_order)
            await self.session.flush()
            return True

        return False

    async def get_orders_count(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        status: Optional[OrderStatus] = None,
        order_type: Optional[OrderType] = None,
    ) -> int:
        """Get total count of orders with criteria"""
        query = select(func.count(Order.id))
        conditions = []
        if start_date:
            conditions.append(Order.created_at >= start_date)
        if end_date:
            conditions.append(Order.created_at <= end_date)
        if status:
            conditions.append(Order.status == status)
        if order_type:
            conditions.append(Order.type == order_type)

        query = query.where(and_(*conditions))
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_orders_with_criteria(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[OrderStatus] = None,
        order_type: Optional[OrderType] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Order]:
        """Get orders with criteria and pagination"""
        query = select(Order).options(selectinload(Order.jobs))

        # Build where conditions
        conditions = []
        if start_date:
            conditions.append(Order.created_at >= start_date)
        if end_date:
            conditions.append(Order.created_at <= end_date)
        if status:
            conditions.append(Order.status == status)
        if order_type:
            conditions.append(Order.type == order_type)

        query = query.where(and_(*conditions)).offset(skip).limit(limit).order_by(asc(Order.created_at))
        result = await self.session.execute(query)
        return list(result.scalars().all())
