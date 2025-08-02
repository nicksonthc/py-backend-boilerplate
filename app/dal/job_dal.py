from typing import TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, asc

from app.models.entities.job_model import Job
from app.models.schemas.job_schema import JobCreate, JobUpdate
from app.utils.enum import JobStatus, JobType

if TYPE_CHECKING:
    from app.models.entities.order_model import Order


class JobDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job: JobCreate) -> Job:
        """Create a new job"""
        db_job = Job(**job.model_dump())
        self.session.add(db_job)
        await self.session.flush()
        await self.session.refresh(db_job)
        return db_job

    async def get_job_by_id(self, job_id: int) -> Job | None:
        """Get a job by ID"""
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def get_job_with_orders(self, job_id: int) -> Job | None:
        """Get a job with its orders"""
        result = await self.session.execute(select(Job).options(selectinload(Job.orders)).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def get_jobs(
        self,
        status: JobStatus | None = None,
        type: JobType | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> list[Job]:
        """Get jobs with optional filtering"""
        query = select(Job)

        # Apply filters
        filters = []
        if status:
            filters.append(Job.status == status)
        if type:
            filters.append(Job.type == type)

        if filters:
            query = query.where(and_(*filters))

        query = query.offset((page - 1) * per_page).limit(per_page).order_by(asc(Job.created_at))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_job(self, job_id: int, job_update: JobUpdate) -> Job | None:
        """Update a job"""
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        db_job = result.scalar_one_or_none()

        if db_job:
            update_data = job_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_job, field, value)

            await self.session.flush()
            await self.session.refresh(db_job)

        return db_job

    async def delete_job(self, job_id: int) -> bool:
        """Delete a job"""
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        db_job = result.scalar_one_or_none()

        if db_job:
            await self.session.delete(db_job)
            await self.session.flush()
            return True

        return False
