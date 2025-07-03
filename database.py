import aiosqlite
import asyncio
from datetime import datetime, timedelta
from config import DB_NAME, STATUS_PENDING, STATUS_UNVERIFIED, STATUS_VERIFIED, STATUS_PAID

async def init_db():
    """Initialize database tables"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pending submissions table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pending_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phone_number TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                timeout_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Unverified accounts table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS unverified_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phone_number TEXT,
                attempts INTEGER DEFAULT 1,
                last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Verified accounts table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS verified_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phone_number TEXT,
                buyer_id INTEGER,
                session_string TEXT,
                status TEXT DEFAULT 'verified',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked_until TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Withdrawal requests table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS withdrawal_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                account_count INTEGER,
                bank_details TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Admin notifications table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admin_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phone_number TEXT,
                notification_type TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        await db.commit()

async def add_user(user_id, username=None, first_name=None, last_name=None):
    """Add or update user in database"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        await db.commit()

async def add_pending_submission(user_id, phone_number):
    """Add pending submission with timeout"""
    timeout_at = datetime.now() + timedelta(minutes=1)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO pending_submissions (user_id, phone_number, timeout_at)
            VALUES (?, ?, ?)
        ''', (user_id, phone_number, timeout_at))
        await db.commit()

async def get_pending_submission(user_id):
    """Get user's pending submission"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT phone_number, timeout_at FROM pending_submissions
            WHERE user_id = ? AND status = 'pending'
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        return await cursor.fetchone()

async def move_to_unverified(user_id, phone_number):
    """Move submission to unverified status"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Update pending submission
        await db.execute('''
            UPDATE pending_submissions SET status = 'unverified'
            WHERE user_id = ? AND phone_number = ? AND status = 'pending'
        ''', (user_id, phone_number))
        
        # Add to unverified accounts
        await db.execute('''
            INSERT OR REPLACE INTO unverified_accounts (user_id, phone_number)
            VALUES (?, ?)
        ''', (user_id, phone_number))
        
        await db.commit()

async def move_to_verified(user_id, phone_number, session_string=None):
    """Move submission to verified status"""
    blocked_until = datetime.now() + timedelta(days=7)
    async with aiosqlite.connect(DB_NAME) as db:
        # Update pending submission
        await db.execute('''
            UPDATE pending_submissions SET status = 'verified'
            WHERE user_id = ? AND phone_number = ? AND status = 'pending'
        ''', (user_id, phone_number))
        
        # Add to verified accounts
        await db.execute('''
            INSERT INTO verified_accounts (user_id, phone_number, session_string, blocked_until)
            VALUES (?, ?, ?, ?)
        ''', (user_id, phone_number, session_string, blocked_until))
        
        # Remove from unverified if exists
        await db.execute('''
            DELETE FROM unverified_accounts WHERE user_id = ? AND phone_number = ?
        ''', (user_id, phone_number))
        
        await db.commit()

async def is_phone_blocked(phone_number):
    """Check if phone number is blocked from resubmission"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT blocked_until FROM verified_accounts
            WHERE phone_number = ? AND blocked_until > ?
        ''', (phone_number, datetime.now()))
        result = await cursor.fetchone()
        return result is not None

async def get_user_accounts(user_id):
    """Get all accounts for a user with their status"""
    async with aiosqlite.connect(DB_NAME) as db:
        accounts = []
        
        # Get pending
        cursor = await db.execute('''
            SELECT phone_number, 'pending' as status FROM pending_submissions
            WHERE user_id = ? AND status = 'pending'
        ''', (user_id,))
        accounts.extend(await cursor.fetchall())
        
        # Get unverified
        cursor = await db.execute('''
            SELECT phone_number, 'unverified' as status FROM unverified_accounts
            WHERE user_id = ?
        ''', (user_id,))
        accounts.extend(await cursor.fetchall())
        
        # Get verified
        cursor = await db.execute('''
            SELECT phone_number, status FROM verified_accounts
            WHERE user_id = ?
        ''', (user_id,))
        accounts.extend(await cursor.fetchall())
        
        return accounts

async def get_verified_accounts_count(user_id):
    """Get count of verified accounts for user"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT COUNT(*) FROM verified_accounts WHERE user_id = ?
        ''', (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 0

async def add_admin_notification(user_id, phone_number, notification_type):
    """Add admin notification for verified accounts only"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO admin_notifications (user_id, phone_number, notification_type)
            VALUES (?, ?, ?)
        ''', (user_id, phone_number, notification_type))
        await db.commit()

async def cleanup_expired_pending():
    """Clean up expired pending submissions"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Get expired submissions
        cursor = await db.execute('''
            SELECT user_id, phone_number FROM pending_submissions
            WHERE status = 'pending' AND timeout_at < ?
        ''', (datetime.now(),))
        expired = await cursor.fetchall()
        
        # Move to unverified
        for user_id, phone_number in expired:
            await move_to_unverified(user_id, phone_number)
        
        return len(expired)
