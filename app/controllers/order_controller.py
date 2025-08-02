from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.response import Response as StandardResponse, Pagination
from app.dal.order_dal import OrderDAL
from app.dal.job_dal import JobDAL
from app.models.schemas.order_schema import OrderCreate, OrderUpdate, OrderOut
from app.models.schemas.job_schema import JobCreate, JobUpdate
from app.models.entities.order_model import Order
from app.utils.enum import OrderType, OrderStatus, JobType, JobStatus


class OrderController:
    def __init__(self, session: AsyncSession):
        self.dal = OrderDAL(session)
        self.job_dal = JobDAL(session)
        self.session = session

    async def create_order(self, order: OrderCreate) -> OrderOut:
        """Create a new order"""
        try:
            db_order = await self.dal.create_order(order)
            return await OrderOut.from_sqlmodel(db_order)
        except Exception as e:
            raise Exception(f"Failed to create order: {str(e)}")

    async def get_order(self, order_id: int) -> OrderOut:
        """Get an order by ID"""
        db_order = await self.dal.get_order_by_id(order_id)
        if not db_order:
            raise Exception(f"Order with ID {order_id} not found")
        return await OrderOut.from_sqlmodel(db_order)

    async def get_orders(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        status: Optional[OrderStatus] = None,
        order_type: Optional[OrderType] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[List[OrderOut], Pagination]:
        """Get orders with criteria and pagination"""
        try:
            # Get total count for pagination
            total_count = await self.dal.get_orders_count(
                start_date=start_date, end_date=end_date, status=status, order_type=order_type
            )

            # Calculate pagination
            pagination = Pagination(page=page, per_page=per_page, total_items=total_count)

            # Get paginated orders
            db_orders = await self.dal.get_orders_with_criteria(
                start_date=start_date,
                end_date=end_date,
                status=status,
                order_type=order_type,
                skip=(page - 1) * per_page,
                limit=per_page,
            )

            # Convert to OrderOut
            orders = [await OrderOut.from_sqlmodel(order) for order in db_orders]
            return orders, pagination

        except Exception as e:
            raise Exception(f"Failed to get orders: {str(e)}")

    async def update_order(self, order_id: int, order_update: OrderUpdate) -> OrderOut:
        """Update an order"""
        db_order = await self.dal.update_order(order_id, order_update)
        if not db_order:
            raise Exception(f"Order with ID {order_id} not found")
        return await OrderOut.from_sqlmodel(db_order)

    async def delete_order(self, order_id: int) -> bool:
        """Delete an order"""
        success = await self.dal.delete_order(order_id)
        if not success:
            raise Exception(f"Order with ID {order_id} not found")
        return success

    async def create_mock_order_with_jobs(self) -> OrderOut:
        """Create a mock order with 2 jobs"""
        try:
            # Create a mock order
            mock_order = OrderCreate(type=OrderType.DEPOSIT)

            db_order = await self.dal.create_order(mock_order)

            # Create 2 jobs for this order
            job1 = JobCreate(
                type=JobType.DEPOSIT,
                status=JobStatus.AVAILABLE,
                priority=1,
                assigned_to="John Doe",
                order_id=db_order.id,
            )

            job2 = JobCreate(
                type=JobType.WITHDRAW,
                status=JobStatus.PROCESSING,
                priority=2,
                assigned_to="Jane Smith",
                order_id=db_order.id,
            )

            # Create jobs
            job1_db = await self.job_dal.create_job(job1)
            job2_db = await self.job_dal.create_job(job2)

            # Commit the transaction
            await self.session.commit()

            # Return the order with jobs
            if db_order.id:
                return await self.get_order(db_order.id)
            else:
                raise Exception("Failed to create order")

        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to create mock order: {str(e)}")
