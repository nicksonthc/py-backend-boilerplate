from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.job_controller import JobController
from app.controllers.order_controller import OrderController
from app.models.schemas.order_schema import OrderCreate, OrderOutResponse, OrderUpdate, OrderOut
from app.db.session import get_session
from app.core.decorators import async_log_and_return_error
from app.core.response import APIResponse, Pagination, Response
from app.utils.conversion import get_date_now_iso, get_utc_dt
from app.utils.enum import OrderStatus, OrderType
from app.utils.logger import recv_http_logger

router = APIRouter(prefix="/orders", tags=["orders"])


# Dependency to get controller
async def get_order_controller(
    session: AsyncSession = Depends(get_session),
) -> OrderController:
    return OrderController(session)


@router.post("/", response_model=OrderOutResponse, status_code=status.HTTP_200_OK)
@async_log_and_return_error(recv_http_logger)
async def create_order(order: OrderCreate, controller: OrderController = Depends(get_order_controller)):
    """Create a new order"""
    orders = await controller.create_order(order)
    return Response(api_response_model=OrderOutResponse(data=[orders]))


@router.get("/{order_id}", response_model=OrderOut)
@async_log_and_return_error(recv_http_logger)
async def get_order(order_id: int, controller: OrderController = Depends(get_order_controller)):
    """Get an order by ID"""
    order = await controller.get_order(order_id)
    return Response(api_response_model=OrderOutResponse(data=[order]))


@router.get("/", response_model=OrderOutResponse)
@async_log_and_return_error(recv_http_logger)
async def get_orders(
    status: OrderStatus | None = Query(None, description="Filter by status"),
    type: OrderType | None = Query(None, description="Filter by type"),
    created_at_from: str | None = Query(
        None,
        description="Start date in ISO format GMT+8",
        examples=["2024-11-20T00:00:00"],
    ),
    created_at_to: str | None = Query(
        None,
        description="End date in ISO format GMT+8",
        examples=["2024-11-22T12:00:00"],
    ),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    controller: OrderController = Depends(get_order_controller),
):
    """Get orders with filtering and pagination"""
    start = None
    end = None
    if created_at_from:
        start = get_utc_dt(datetime.fromisoformat(created_at_from))
    if created_at_to:
        end = get_utc_dt(datetime.fromisoformat(created_at_to))

    orders, pagination = await controller.get_orders(
        start_date=start, end_date=end, status=status, order_type=type, page=page, per_page=per_page
    )
    return Response(api_response_model=OrderOutResponse(data=orders, pagination=pagination))


@router.put("/{order_id}", response_model=OrderOut)
@async_log_and_return_error(recv_http_logger)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    controller: OrderController = Depends(get_order_controller),
):
    """Update an order"""
    order = await controller.update_order(order_id, order_update)

    return Response(api_response_model=OrderOutResponse(data=[order]))


@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
@async_log_and_return_error(recv_http_logger)
async def delete_order(order_id: int, controller: OrderController = Depends(get_order_controller)):
    """Delete an order"""
    await controller.delete_order(order_id)
    return Response()


@router.post("/mock", status_code=status.HTTP_200_OK)
@async_log_and_return_error(recv_http_logger)
async def create_mock_order_with_jobs(controller: OrderController = Depends(get_order_controller)):
    """Create a mock order with 2 jobs"""
    order = await controller.create_mock_order_with_jobs()
    return Response(api_response_model=OrderOutResponse(data=[order]))
