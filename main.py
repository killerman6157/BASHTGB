import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID
from database import init_db
from handlers import start, phone_handler, otp_handler, admin_commands, user_commands, withdraw_handler
from services.scheduler import setup_scheduler
from services.otp_forwarder import setup_otp_forwarder

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot"""
    try:
        # Initialize bot and dispatcher
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher(storage=MemoryStorage())
        
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Include routers
        dp.include_router(start.router)
        dp.include_router(phone_handler.router)
        dp.include_router(otp_handler.router)
        dp.include_router(admin_commands.router)
        dp.include_router(user_commands.router)
        dp.include_router(withdraw_handler.router)
        
        # Setup scheduler for time-based operations
        await setup_scheduler()
        logger.info("Scheduler setup completed")
        
        # Setup OTP forwarder
        await setup_otp_forwarder()
        logger.info("OTP forwarder setup completed")
        
        # Start polling
        logger.info("Bot is starting...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
