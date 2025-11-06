from pydantic import BaseModel
from typing import Optional, ClassVar
from motor.motor_asyncio import AsyncIOMotorCollection
from src.database.connection import db

class Channel(BaseModel):
    chat_id: int
    title: Optional[str] = None
    username: Optional[str] = None
    type: str  # "public" | "private"

    collection: ClassVar[AsyncIOMotorCollection] = db.channels

    @classmethod
    async def add_channel(cls, chat_id: int,
                          title: str,
                          username: Optional[str],
                          type: str):
        exists = await cls.collection.find_one({"chat_id": chat_id})
        if not exists:
            await cls.collection.insert_one({
                "chat_id": chat_id,
                "title": title,
                "username": username,
                "type": type
            })

    @classmethod
    async def get_all_channels(cls):
        return await cls.collection.find().to_list(None)
