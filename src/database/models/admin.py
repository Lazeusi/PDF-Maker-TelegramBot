from src.database.connection import db
from pydantic import BaseModel
from typing import Optional, ClassVar
from motor.motor_asyncio import AsyncIOMotorCollection

from src.logger import log


class Admin(BaseModel):
    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_owner : Optional[bool] = False

    collection: ClassVar[AsyncIOMotorCollection] = db.admins

    @classmethod
    async def find_admin_by_telegram_id(cls, telegram_id: int) -> Optional["Admin"]:
        
        data = await cls.collection.find_one({"telegram_id": telegram_id})
        if data:
            return Admin(**data)
        return None
    
    @classmethod
    async def get_all_admins(cls) -> list["Admin"]:
        admins_data = await cls.collection.find().to_list(None)
        return [Admin(**data) for data in admins_data]

    @classmethod
    async def create_admin(
    cls,
    telegram_id: int,
    first_name: Optional[str],
    last_name: Optional[str],
    username: Optional[str],
    is_owner: Optional[bool] = False
) -> "Admin":
        
        if username:
            username = username.lower()

        await cls.collection.insert_one({
            "telegram_id": telegram_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "is_owner": is_owner
        })
        log.info(f"""
        \n             -------New admin added!-------            \n
        -   telegram_id: {telegram_id}\n
        -   first_name: {first_name}\n
        -   last_name: {last_name}\n
        -   username: {username}\n                         
           \n             ------------------------------             \n
                 """)
        