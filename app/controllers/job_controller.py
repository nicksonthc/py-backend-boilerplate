from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.dal.job_dal import JobDAL
from app.models.schemas.job_schema import JobCreate, JobUpdate, Job, JobOut
from app.models.entities.job_model import Job as JobEntity
from app.utils.enum import JobStatus, JobType


class JobController:
    def __init__(self, session: AsyncSession):
        self.dal = JobDAL(session)
        self.session = session

    async def create_job(self, job: JobCreate) -> JobOut:
        """Create a new job"""
        db_job = await self.dal.create_job(job)
        return await JobOut.from_sqlmodel(db_job)

    async def get_job(self, job_id: int) -> JobOut:
        """Get a job by ID"""
        db_job = await self.dal.get_job_by_id(job_id)
        return await JobOut.from_sqlmodel(db_job)

    async def get_jobs(
        self,
        status: JobStatus | None = None,
        type: JobType | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> List[JobOut]:
        """Get jobs with optional filtering"""
        db_jobs = await self.dal.get_jobs(
            status=status,
            type=type,
            page=page,
            per_page=per_page,
        )
        return [await JobOut.from_sqlmodel(job) for job in db_jobs]

    async def update_job(self, job_id: int, job_update: JobUpdate) -> JobOut:
        """Update a job"""
        db_job = await self.dal.update_job(job_id, job_update)
        return await JobOut.from_sqlmodel(db_job)

    async def delete_job(self, job_id: int) -> bool:
        """Delete a job"""
        success = await self.dal.delete_job(job_id)
        return success
