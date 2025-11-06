from .user_middleware import UserMiddleware
from .force_subscribe import ForceSubscribeMiddleware

async def setup_middlewares(dp , bot = None):
    dp.message.middleware(UserMiddleware())
    dp.message.middleware(ForceSubscribeMiddleware(bot=bot))
