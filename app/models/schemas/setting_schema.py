from pydantic import BaseModel

from app.core.response import APIResponse
from app.models.entities.setting_model import Setting
from app.utils.conversion import convert_utc_to_local_iso


class SettingBase(BaseModel):
    """Class that used to convert ORM object to pydantic model for out of context use"""

    id: int
    name: str
    value: dict
    description: str | None = None
    created_at: str
    updated_at: str | None = None


class SettingOut(SettingBase):
    """Class that used to convert ORM object to pydantic model for out of context use"""

    class Config:
        from_attributes = True

    @classmethod
    def from_sqlmodel(cls, sqlmodel_obj: "Setting"):
        if sqlmodel_obj is None:
            return None
        return cls(
            id=sqlmodel_obj.id,
            name=sqlmodel_obj.name,
            value=sqlmodel_obj.value,
            description=sqlmodel_obj.description,
            created_at=convert_utc_to_local_iso(sqlmodel_obj.created_at),
            updated_at=convert_utc_to_local_iso(sqlmodel_obj.updated_at) if sqlmodel_obj.updated_at else None,
        )


class CreateSettingResponse(APIResponse):
    data: SettingOut


class UpdateSettingResponse(APIResponse):
    data: SettingOut
