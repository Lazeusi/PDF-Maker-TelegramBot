import asyncio
from aiogram import Bot, Dispatcher , types
import sys

from src.config import settings
from src.handlers import start_handler
from src.logger import log
from src.database.connection import db
from src.middlewares import setup_middlewares


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    await db.connect()
    
    await setup_middlewares(dp, bot=bot)
    
    await start_handler(dp)
    
    commands = [
        types.BotCommand(command="start" , description="Start the bot🚀")
    ]
    await bot.set_my_commands(commands)
    
    bot_info = await bot.get_me()
    
    system_info = {
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "implementation": sys.implementation.name,
        "bot_framework": "aiogram"
    }
    log.info(f"""\n\n
            \n             -------The bot started!-------            \n
        -   python version: {system_info['python_version']}\n
        -   platform: {system_info['platform']}\n
        -   implementation: {system_info['implementation']}\n
        -   bot framework: {system_info['bot_framework']}\n
        -   bot name: {bot_info.full_name}\n                         
        -   bot username: @{bot_info.username}\n                      
        -   bot id: {bot_info.id}\n                                   
           \n             ------------------------------             \n
           
             """)
    await dp.start_polling(bot)

    
    
if __name__ == "__main__":
    try:     
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("""
                 \n             -------The bot stopped!-------            \n
                 
               \n             ------------------------------             \n
                 """)