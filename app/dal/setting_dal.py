from typing import Dict, Any
from sqlalchemy import update, delete
from sqlalchemy.future import select

from .base_dal import BaseDAL
from app.models.entities.setting_model import Setting
from app.core.decorators import decorateAllFunctionInClass
from app.core.circuit_breaker import CircuitBreaker


@decorateAllFunctionInClass(CircuitBreaker.circuit_breaker)
class SettingDAL(BaseDAL):

    async def create_setting(self, setting: Setting) -> Setting:
        self.session.add(setting)
        await self.session.flush()
        await self.session.refresh(setting)
        return setting

    async def get_setting(self, key: str) -> Setting | None:
        result = await self.session.scalar(select(Setting).where(Setting.name == key))
        return result

    async def update_setting(self, key: str, update_dict: Dict[str, Any]) -> Setting | None:
        result = await self.session.scalar(
            update(Setting).where(Setting.name == key).values(update_dict).returning(Setting)
        )
        await self.session.flush()
        return result

    async def delete_setting(self, key: str) -> bool:
        result = await self.session.execute(delete(Setting).where(Setting.name == key))
        await self.session.flush()
        return result.rowcount > 0
