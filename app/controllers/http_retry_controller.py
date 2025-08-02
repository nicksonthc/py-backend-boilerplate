from dateutil.relativedelta import relativedelta

from app.dal.http_retry_dal import HttpRetryDAL
from app.models.schemas.http_retry_schema import HttpRetryCreate, HttpRetryOut


class HttpRetryController:

    def __init__(self) -> None:
        self.dal = HttpRetryDAL()

    async def create_http_retry(self, http_retry: HttpRetryCreate):
        async with self.dal.create_http_retry(http_retry) as db_obj:
            return HttpRetryOut(**db_obj.model_dump())

    async def read_http_retry(self, id: int):
        async with self.dal.read_http_retry(id) as db_obj:
            if db_obj:
                return HttpRetryOut(**db_obj.model_dump())

    async def incr_http_retry_attempts(self, id: int):
        return await self.dal.incr_http_retry_attempts(id)

    async def complete_http_retry(self, id: int, response: dict):
        return await self.dal.complete_http_retry(id, response)

    async def delete_http_retry(self, id: int):
        return await self.dal.delete_http_retry(id)

    async def get_incompleted_http_retry(self):
        async with self.dal.get_incompleted_http_retry() as db_objs:
            for db_obj in db_objs:
                yield HttpRetryOut(**db_obj.model_dump())

    async def clean_http_retry(self, remove_period: relativedelta):
        return await self.dal.clean_http_retry(remove_period)
