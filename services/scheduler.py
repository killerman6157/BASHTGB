import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from config import TIMEZONE, ACCOUNT_RECEIVING_START, ACCOUNT_RECEIVING_END
from database import cleanup_expired_pending

scheduler = AsyncIOScheduler()

async def setup_scheduler():
    """Setup scheduled tasks"""
    
    # Set timezone
    tz = pytz.timezone(TIMEZONE)
    
    # Schedule cleanup of expired pending submissions every minute
    scheduler.add_job(
        cleanup_expired_submissions,
        CronTrigger(second=0, timezone=tz),
        id='cleanup_expired'
    )
    
    # Schedule account receiving hours (8AM-10PM WAT)
    # These are just markers, the actual logic is in utils/helpers.py
    scheduler.add_job(
        log_account_receiving_status,
        CronTrigger(hour=ACCOUNT_RECEIVING_START, minute=0, timezone=tz),
        id='account_receiving_open'
    )
    
    scheduler.add_job(
        log_account_receiving_status,
        CronTrigger(hour=ACCOUNT_RECEIVING_END, minute=0, timezone=tz),
        id='account_receiving_close'
    )
    
    # Start scheduler
    scheduler.start()
    print("Scheduler started successfully")

async def cleanup_expired_submissions():
    """Clean up expired pending submissions"""
    try:
        expired_count = await cleanup_expired_pending()
        if expired_count > 0:
            print(f"Cleaned up {expired_count} expired pending submissions")
    except Exception as e:
        print(f"Error in cleanup_expired_submissions: {e}")

async def log_account_receiving_status():
    """Log account receiving status changes"""
    from utils.helpers import is_account_receiving_open
    
    current_time = datetime.now(pytz.timezone(TIMEZONE))
    status = "OPEN" if is_account_receiving_open() else "CLOSED"
    
    print(f"Account receiving status at {current_time.strftime('%H:%M WAT')}: {status}")

async def shutdown_scheduler():
    """Shutdown scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler shutdown successfully")
