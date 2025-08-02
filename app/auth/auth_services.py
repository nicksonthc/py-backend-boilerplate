from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from .token import TokenManager
from app.utils.enum import SettingKey, Role
from app.dto.auth_dto import UserInfoInJWT
from app.controllers.setting_controller import SettingController


class AuthServices:

    @staticmethod
    async def login(username: str, password: str, session: AsyncSession) -> Tuple[bool, str, str]:
        """Function to call when FE trying ot login

        Args:
            username (str): username of the user
            password (str): password of the user

        Returns:
            Tuple[bool, str, str]: [0] is status , [1] is message, [2] is token
        """
        setting_controller = SettingController(session)

        # check for admin muser
        admin_users = await setting_controller.get_setting_value(SettingKey.ADMIN_USER)

        if admin_users:
            for users in admin_users:
                if username == users.get("username") and password == users.get("password"):
                    token = await AuthServices.bypass_official_auth(username)
                    return (True, "Success", token)

        # TODO go through official authentication
        return (False, "Username or password is incorrect", "")

    @staticmethod
    async def bypass_official_auth(username: str) -> str:
        """Generate token without official auth"""
        user_info = UserInfoInJWT(username=username, role=Role.ADMIN)
        token = TokenManager.generate_token(user_info)
        return token

    @staticmethod
    def swagger_auth() -> str:
        """Generate token for swagger"""
        user_info = UserInfoInJWT(username="swagger", role=Role.SWAGGER)
        token = TokenManager.generate_token(user_info)
        return token
