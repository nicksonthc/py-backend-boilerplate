from typing import Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from .base_controller import BaseController
from app.dal.setting_dal import SettingDAL
from app.models.entities.setting_model import Setting
from app.models.schemas.setting_schema import SettingOut


class SettingController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.dal = SettingDAL(session)

    async def create_setting(self, key: str, value: Dict, description: Optional[str] = None) -> SettingOut:
        setting = await self.dal.create_setting(Setting(name=key, value=value, description=description))
        return SettingOut.from_sqlmodel(setting)

    async def get_setting(self, key: str) -> SettingOut:
        setting = await self.dal.get_setting(key)
        return SettingOut.from_sqlmodel(setting)

    async def get_setting_value(self, key: str) -> Any:
        """
        Get a setting by key

        Return:
            Any: The value of the setting
        """
        setting = await self.dal.get_setting(key)
        if setting:
            return setting.value.get(key)
        else:
            return None

    async def update_setting(self, key: str, update_dict: Dict) -> SettingOut:
        setting = await self.dal.update_setting(key, update_dict)
        return SettingOut.from_sqlmodel(setting)

    async def delete_setting(self, key: str) -> bool:
        is_deleted = await self.dal.delete_setting(key)
        return is_deleted
