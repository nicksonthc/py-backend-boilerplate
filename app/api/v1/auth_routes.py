from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import SessionDep
from app.utils.enum import HTTPStatus
from app.utils.logger import recv_http_logger
from app.core.response import Response
from app.dto.auth_dto import UserLoginBody
from app.core.decorators import async_log_and_return_error

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
@async_log_and_return_error(recv_http_logger)
async def login(args: UserLoginBody, session: SessionDep):
    """
    Login api for FE to call \n
    Return token under data field
    """
    from app.auth.auth_services import AuthServices

    is_success, msg, token = await AuthServices.login(args.username, args.password, session)
    if is_success:
        return Response(data=token)
    else:
        return Response(False, HTTPStatus.UNAUTHORIZED, msg)


@router.post("/token", description="Used by swagger to get token header")
@async_log_and_return_error(recv_http_logger)
async def post_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Only used by swagger"""
    from app.auth.auth_services import AuthServices

    if form_data.username != "swagger" or form_data.password != "swagger":
        return Response(
            False, HTTPStatus.UNAUTHORIZED, "Invalid Username and Password for getting token for Swagger UI"
        )

    token = AuthServices.swagger_auth()
    return {"access_token": token, "token_type": "bearer"}
