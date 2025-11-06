from .start import router as start_router
from .admin import router as admin_router
from .callbacks import router as callbacks_router
from .check_subscribe import router as check_subscribe_router


async def start_handler(dp):
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(callbacks_router)
    dp.include_router(check_subscribe_router)