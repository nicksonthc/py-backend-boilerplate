from fastapi import APIRouter

from app.utils.enum import HTTPStatus
from app.utils.logger import recv_http_logger
from app.db.session import SessionDep
from app.core.response import Response
from app.dto.setting_dto import CreateSetting, UpdateSetting
from app.core.decorators import async_log_and_return_error
from app.models.schemas.setting_schema import CreateSettingResponse, UpdateSettingResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/{key}", description="Get a setting value by key")
@async_log_and_return_error(recv_http_logger)
async def get_setting(key: str, session: SessionDep):
    from app.controllers.setting_controller import SettingController

    setting_controller = SettingController(session)
    setting_value = await setting_controller.get_setting_value(key)
    return Response(data=setting_value)


@router.post("/", description="Create a new setting", response_model=CreateSettingResponse)
@async_log_and_return_error(recv_http_logger)
async def create_setting(setting_data: CreateSetting, session: SessionDep):
    from app.controllers.setting_controller import SettingController

    setting_controller = SettingController(session)
    # Check if setting with key already exists
    existing_setting = await setting_controller.get_setting(setting_data.key)
    if existing_setting:
        return Response(
            status=False,
            data=existing_setting,
            code=HTTPStatus.CONFLICT,
            message=f"Setting with key '{setting_data.key}' already exists",
        )

    # Create new setting
    new_setting = await setting_controller.create_setting(
        key=setting_data.key,
        value=setting_data.value,
        description=setting_data.description,
    )

    return Response(api_response_model=CreateSettingResponse(data=new_setting))


@router.patch("/{key}", description="Update column of a setting", response_model=UpdateSettingResponse)
@async_log_and_return_error(recv_http_logger)
async def update_setting(key: str, update_field: UpdateSetting, session: SessionDep):
    from app.controllers.setting_controller import SettingController

    if update_field.value is None and update_field.description is None:
        return Response(
            status=False,
            code=HTTPStatus.BAD_REQUEST,
            message="At least one field (value or description) must be provided for update",
        )

    setting_controller = SettingController(session)
    # only update if the field is provided
    update_dict = {}
    if update_field.value:
        update_dict["value"] = update_field.value
    if update_field.description:
        update_dict["description"] = update_field.description
    existing_setting = await setting_controller.update_setting(key, update_dict)
    return Response(api_response_model=UpdateSettingResponse(data=existing_setting))


@router.delete("/{key}", description="Delete a setting by key")
@async_log_and_return_error(recv_http_logger)
async def delete_setting(key: str, session: SessionDep):
    from app.controllers.setting_controller import SettingController

    setting_controller = SettingController(session)
    is_deleted = await setting_controller.delete_setting(key)
    if not is_deleted:
        return Response(
            status=False,
            code=HTTPStatus.BAD_REQUEST,
            message=f"Setting with key '{key}' not found",
        )
    return Response(message=f"Setting with key '{key}' deleted")
