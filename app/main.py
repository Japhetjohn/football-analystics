import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.bot.handlers import analysis

async def main():
    if settings.bot_token == "TBD":
        logging.warning("Bot token not set! Exiting gracefully.")
        return
        
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    dp.include_router(analysis.router)
    
    logging.info("Starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
