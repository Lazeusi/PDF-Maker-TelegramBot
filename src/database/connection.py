from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_DB_URI)
        self.db = self.client[settings.MONGO_DB_NAME]

        # collections
        self.users = self.db["users"]
        self.admins = self.db["admins"]
        self.channels = self.db["channels"]
    async def connect(self):
        try:
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            print(f"""
            \n             -------Database connected!-------            \n
              -   Database name: {settings.MONGO_DB_NAME}\n
                \n             ------------------------------             \n
                  """)
        except Exception as e:
            print(f"""
            \n             -------Database connection failed!-------            \n
              -   Error: {e}\n
                \n             ------------------------------             \n
                  """)
            
db = Database()