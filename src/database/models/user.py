from pydantic import BaseModel
from typing import Optional, ClassVar
from motor.motor_asyncio import AsyncIOMotorCollection

from src.database.connection import db
from src.logger import log


class User(BaseModel):
    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


    collection: ClassVar[AsyncIOMotorCollection] = db.users

    @classmethod
    async def find_user_by_telegram_id(cls, telegram_id: int):
        user_data = await cls.collection.find_one({"telegram_id": telegram_id})
        if user_data:
            return cls(**user_data)
        return None

    @classmethod
    async def create_user(cls, telegram_id: int, first_name: str, last_name: str = None, username: str = None):
        user = cls(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        await cls.collection.insert_one(user.model_dump())  # در Pydantic v2 باید از model_dump() استفاده کنی
        log.info(f"""\n\n
        -------New user joined!-------
        - Telegram ID: {telegram_id}
        - Username: @{username}
        - First Name: {first_name}
        - Last Name: {last_name}
        ------------------------------\n
        """)
