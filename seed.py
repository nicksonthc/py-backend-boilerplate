import asyncio

from sqlmodel import select


class SeedSetting:
    data = [
        {
            "name": "ADMIN_USER",
            "value": {
                "ADMIN_USER": [
                    {"username": "admin", "password": "admin"},
                    {"username": "admin2", "password": "admin2"},
                    {"username": "admin3", "password": "admin3"},
                    {"username": "adminn", "password": "adminn"},
                ]
            },
            "description": "Admin user credentials",
        }
    ]

    @classmethod
    async def seed(cls):
        from app.db.session import get_session_context
        from app.models.entities.setting_model import Setting

        async with get_session_context() as session:
            for setting_data in cls.data:
                query = select(Setting).where(Setting.name == setting_data["name"])
                result = await session.execute(query)
                existing_setting = result.first()

                if not existing_setting:
                    setting = Setting(**setting_data)
                    session.add(setting)
            print("✅ Settings seeding completed successfully.")


if __name__ == "__main__":
    try:
        asyncio.run(SeedSetting.seed())
    except Exception as e:
        print(f"An error occurred during execution: {e}")
