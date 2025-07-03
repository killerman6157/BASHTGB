import asyncio
from datetime import datetime, timedelta
from database import (
    get_pending_submission,
    move_to_unverified,
    move_to_verified,
    DB_NAME
)
import aiosqlite

async def check_and_update_timeouts():
    """Check for timed out pending submissions and move them to unverified"""
    
    async with aiosqlite.connect(DB_NAME) as db:
        # Get all pending submissions that have timed out
        cursor = await db.execute('''
            SELECT user_id, phone_number FROM pending_submissions
            WHERE status = 'pending' AND timeout_at < ?
        ''', (datetime.now(),))
        
        expired_submissions = await cursor.fetchall()
        
        # Move expired submissions to unverified
        for user_id, phone_number in expired_submissions:
            await move_to_unverified(user_id, phone_number)
        
        return len(expired_submissions)

async def get_status_counts():
    """Get counts of accounts by status"""
    
    async with aiosqlite.connect(DB_NAME) as db:
        counts = {}
        
        # Pending
        cursor = await db.execute(
            "SELECT COUNT(*) FROM pending_submissions WHERE status = 'pending'"
        )
        counts['pending'] = (await cursor.fetchone())[0]
        
        # Unverified
        cursor = await db.execute("SELECT COUNT(*) FROM unverified_accounts")
        counts['unverified'] = (await cursor.fetchone())[0]
        
        # Verified
        cursor = await db.execute(
            "SELECT COUNT(*) FROM verified_accounts WHERE status = 'verified'"
        )
        counts['verified'] = (await cursor.fetchone())[0]
        
        # Paid
        cursor = await db.execute(
            "SELECT COUNT(*) FROM verified_accounts WHERE status = 'paid'"
        )
        counts['paid'] = (await cursor.fetchone())[0]
        
        return counts

async def cleanup_old_unverified():
    """Clean up old unverified accounts (older than 30 days)"""
    
    cutoff_date = datetime.now() - timedelta(days=30)
    
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            DELETE FROM unverified_accounts
            WHERE created_at < ?
        ''', (cutoff_date,))
        
        deleted_count = cursor.rowcount
        await db.commit()
        
        return deleted_count

async def get_user_status_summary(user_id):
    """Get status summary for a specific user"""
    
    async with aiosqlite.connect(DB_NAME) as db:
        summary = {}
        
        # Pending
        cursor = await db.execute('''
            SELECT COUNT(*) FROM pending_submissions
            WHERE user_id = ? AND status = 'pending'
        ''', (user_id,))
        summary['pending'] = (await cursor.fetchone())[0]
        
        # Unverified
        cursor = await db.execute('''
            SELECT COUNT(*) FROM unverified_accounts WHERE user_id = ?
        ''', (user_id,))
        summary['unverified'] = (await cursor.fetchone())[0]
        
        # Verified
        cursor = await db.execute('''
            SELECT COUNT(*) FROM verified_accounts
            WHERE user_id = ? AND status = 'verified'
        ''', (user_id,))
        summary['verified'] = (await cursor.fetchone())[0]
        
        # Paid
        cursor = await db.execute('''
            SELECT COUNT(*) FROM verified_accounts
            WHERE user_id = ? AND status = 'paid'
        ''', (user_id,))
        summary['paid'] = (await cursor.fetchone())[0]
        
        return summary

async def can_resubmit_phone(phone_number):
    """Check if a phone number can be resubmitted"""
    
    async with aiosqlite.connect(DB_NAME) as db:
        # Check if it's currently pending
        cursor = await db.execute('''
            SELECT COUNT(*) FROM pending_submissions
            WHERE phone_number = ? AND status = 'pending'
        ''', (phone_number,))
        
        if (await cursor.fetchone())[0] > 0:
            return False  # Already pending
        
        # Check if it's verified and blocked
        cursor = await db.execute('''
            SELECT COUNT(*) FROM verified_accounts
            WHERE phone_number = ? AND blocked_until > ?
        ''', (phone_number, datetime.now()))
        
        if (await cursor.fetchone())[0] > 0:
            return False  # Blocked
        
        return True  # Can resubmit

async def mark_account_as_paid(user_id, phone_number):
    """Mark a specific account as paid"""
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE verified_accounts
            SET status = 'paid'
            WHERE user_id = ? AND phone_number = ? AND status = 'verified'
        ''', (user_id, phone_number))
        
        changes = db.total_changes
        await db.commit()
        
        return changes > 0
