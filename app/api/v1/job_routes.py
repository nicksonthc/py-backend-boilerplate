from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.job_controller import JobController
from app.core.decorators import async_log_and_return_error
from app.core.response import Response
from app.db.session import get_session
from app.models.schemas.job_schema import JobCreate, JobUpdate, Job, JobOutResponse
from app.utils.enum import JobStatus, JobType
from app.utils.logger import recv_http_logger

router = APIRouter(prefix="/jobs", tags=["jobs"])


# Dependency to get controller
async def get_job_controller(session: AsyncSession = Depends(get_session)) -> JobController:
    return JobController(session)


@router.post("/", response_model=JobOutResponse, status_code=status.HTTP_200_OK)
@async_log_and_return_error(recv_http_logger)
async def create_job(job: JobCreate, controller: JobController = Depends(get_job_controller)):
    """Create a new job"""
    jobs = await controller.create_job(job)
    return Response(
        status=False, code=status.HTTP_400_BAD_REQUEST, message="Not implemented, jobs are created by order creation"
    )


@router.get("/{job_id}", response_model=JobOutResponse)
@async_log_and_return_error(recv_http_logger)
async def get_job(job_id: int, controller: JobController = Depends(get_job_controller)):
    """Get a job by ID"""
    job = await controller.get_job(job_id)
    return Response(api_response_model=JobOutResponse(data=[job]))


@router.get("/", response_model=JobOutResponse)
@async_log_and_return_error(recv_http_logger)
async def get_jobs(
    status: JobStatus | None = Query(None, description="Filter by status"),
    type: JobType | None = Query(None, description="Filter by type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    controller: JobController = Depends(get_job_controller),
):
    """Get all jobs"""
    jobs = await controller.get_jobs(status=status, type=type, page=page, per_page=per_page)
    return Response(api_response_model=JobOutResponse(data=jobs))


@router.put("/{job_id}", response_model=JobOutResponse)
@async_log_and_return_error(recv_http_logger)
async def update_job(job_id: int, job_update: JobUpdate, controller: JobController = Depends(get_job_controller)):
    """Update a job"""
    job = await controller.update_job(job_id, job_update)
    return Response(api_response_model=JobOutResponse(data=[job]))


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
@async_log_and_return_error(recv_http_logger)
async def delete_job(job_id: int, controller: JobController = Depends(get_job_controller)):
    """Delete a job"""
    await controller.delete_job(job_id)
    return Response()
