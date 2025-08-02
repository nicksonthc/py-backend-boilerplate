from fastapi import APIRouter

from app.core.http_retry_manager import HttpRetryManager
from app.core.response import Response
from app.models.schemas.http_retry_schema import HttpRetryIn, HttpRetryOutResponse

router = APIRouter(prefix="/http-retry", tags=["http_retry"])


@router.get("/{id}", response_model=HttpRetryOutResponse)
async def get_http_retry(id: int):
    data = await HttpRetryManager.read(id)
    return Response(data=[data.model_dump(mode="json")])


@router.get("/", response_model=HttpRetryOutResponse)
async def get_incompleted_http_retry():
    """
    Get all in processing HttpRetry.
    """
    return Response(data=[data.model_dump(mode="json") async for data in HttpRetryManager.read_incompleted()])


@router.post("/")
async def create_http_retry(data: HttpRetryIn):
    await HttpRetryManager.create(**data.model_dump())
    return Response()


@router.put("/")
async def reinitialize_http_retry():
    """
    Reinitialize to ensure runtime is in sync with database.
    """
    await HttpRetryManager.initialize()
    return Response()


@router.delete("/{id}")
async def delete_http_retry(id: int):
    """
    Cancel a HttpRetry.
    """
    await HttpRetryManager.delete(id)
    return Response()
