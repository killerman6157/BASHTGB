import re
from aiogram import Router, types, F
from aiogram.filters import Command

from database import (
    get_verified_accounts_count,
    move_to_verified,
    add_admin_notification
)
from config import ADMIN_ID, CHANNEL_ID
from utils.helpers import is_admin

router = Router()

@router.message(Command("accept"), F.from_user.id == ADMIN_ID)
async def accept_account(message: types.Message):
    """Accept a verified account - /accept [user_id] [phone_number]"""
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer(
                "❌ <b>Kuskure a umarni!</b>\n\n"
                "Amfani: <code>/accept [user_id] [phone_number]</code>\n"
                "Misali: <code>/accept 123456789 +2348167757987</code>"
            )
            return
        
        user_id = int(parts[1])
        phone_number = parts[2]
        
        # Verify this is a verified account
        # In a real implementation, you'd check if this account is actually verified
        # For now, we'll just confirm the acceptance
        
        await message.answer(
            "✅ <b>An karɓi account cikin nasara!</b>\n\n"
            f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
            f"📱 <b>Phone:</b> <code>{phone_number}</code>\n\n"
            "User na iya yanzu yin request don biya ta /withdraw"
        )
        
        # Log the acceptance
        await add_admin_notification(user_id, phone_number, "admin_accepted")
        
    except ValueError:
        await message.answer(
            "❌ <b>Kuskure a lambobi!</b>\n\n"
            "Tabbatar User ID ya kasance lamba."
        )
    except Exception as e:
        await message.answer(
            f"❌ <b>Kuskure:</b> {str(e)}"
        )

@router.message(Command("stats"), F.from_user.id == ADMIN_ID)
async def admin_stats(message: types.Message):
    """Show admin statistics"""
    
    from database import DB_NAME
    import aiosqlite
    
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            # Get counts by status
            stats = {}
            
            # Pending submissions
            cursor = await db.execute(
                "SELECT COUNT(*) FROM pending_submissions WHERE status = 'pending'"
            )
            stats['pending'] = (await cursor.fetchone())[0]
            
            # Unverified accounts
            cursor = await db.execute(
                "SELECT COUNT(*) FROM unverified_accounts"
            )
            stats['unverified'] = (await cursor.fetchone())[0]
            
            # Verified accounts
            cursor = await db.execute(
                "SELECT COUNT(*) FROM verified_accounts WHERE status = 'verified'"
            )
            stats['verified'] = (await cursor.fetchone())[0]
            
            # Paid accounts
            cursor = await db.execute(
                "SELECT COUNT(*) FROM verified_accounts WHERE status = 'paid'"
            )
            stats['paid'] = (await cursor.fetchone())[0]
            
            # Total users
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = (await cursor.fetchone())[0]
            
            response = (
                "📊 <b>BOT STATISTICS</b>\n\n"
                f"⏳ <b>Pending:</b> {stats['pending']}\n"
                f"❌ <b>Unverified:</b> {stats['unverified']}\n"
                f"✅ <b>Verified:</b> {stats['verified']}\n"
                f"💰 <b>Paid:</b> {stats['paid']}\n"
                f"👥 <b>Total Users:</b> {stats['total_users']}\n\n"
                f"🔢 <b>Total Accounts:</b> {stats['pending'] + stats['unverified'] + stats['verified'] + stats['paid']}"
            )
            
            await message.answer(response)
            
    except Exception as e:
        await message.answer(f"❌ <b>Kuskure:</b> {str(e)}")

@router.message(Command("user_accounts"), F.from_user.id == ADMIN_ID)
async def user_accounts_admin(message: types.Message):
    """Check user accounts - /user_accounts [user_id]"""
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer(
                "❌ <b>Kuskure a umarni!</b>\n\n"
                "Amfani: <code>/user_accounts [user_id]</code>\n"
                "Misali: <code>/user_accounts 123456789</code>"
            )
            return
        
        user_id = int(parts[1])
        
        # Get user accounts
        from database import get_user_accounts
        accounts = await get_user_accounts(user_id)
        
        if not accounts:
            await message.answer(
                f"📋 <b>User ID {user_id} ba shi da accounts.</b>"
            )
            return
        
        response = f"📋 <b>ACCOUNTS FOR USER {user_id}</b>\n\n"
        
        for phone, status in accounts:
            status_emoji = {
                'pending': '⏳',
                'unverified': '❌',
                'verified': '✅',
                'paid': '💰'
            }.get(status, '❓')
            
            response += f"{status_emoji} <code>{phone}</code> — <b>{status}</b>\n"
        
        response += f"\n🔢 <b>Total:</b> {len(accounts)} accounts"
        
        await message.answer(response)
        
    except ValueError:
        await message.answer(
            "❌ <b>Kuskure a lambobi!</b>\n\n"
            "Tabbatar User ID ya kasance lamba."
        )
    except Exception as e:
        await message.answer(f"❌ <b>Kuskure:</b> {str(e)}")

@router.message(Command("mark_paid"), F.from_user.id == ADMIN_ID)
async def mark_paid(message: types.Message):
    """Mark accounts as paid - /mark_paid [user_id] [count]"""
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer(
                "❌ <b>Kuskure a umarni!</b>\n\n"
                "Amfani: <code>/mark_paid [user_id] [count]</code>\n"
                "Misali: <code>/mark_paid 123456789 5</code>"
            )
            return
        
        user_id = int(parts[1])
        count = int(parts[2])
        
        # Update verified accounts to paid status
        from database import DB_NAME
        import aiosqlite
        
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('''
                UPDATE verified_accounts 
                SET status = 'paid' 
                WHERE user_id = ? AND status = 'verified'
                ORDER BY created_at ASC
                LIMIT ?
            ''', (user_id, count))
            
            changes = db.total_changes
            await db.commit()
        
        if changes > 0:
            await message.answer(
                f"✅ <b>An yiwa User ID {user_id} alamar biya don accounts guda {changes}.</b>\n\n"
                "An cire su daga jerin biyan da ake jira, an kuma sanya su a matsayin wanda aka biya."
            )
        else:
            await message.answer(
                f"❌ <b>Ba a sami verified accounts don User ID {user_id} ba.</b>"
            )
            
    except ValueError:
        await message.answer(
            "❌ <b>Kuskure a lambobi!</b>\n\n"
            "Tabbatar User ID da count sun kasance lambobi."
        )
    except Exception as e:
        await message.answer(f"❌ <b>Kuskure:</b> {str(e)}")

@router.message(Command("completed_today_payment"), F.from_user.id == ADMIN_ID)
async def completed_today_payment(message: types.Message):
    """Announce completion of today's payments"""
    
    try:
        # Send notification to channel
        from main import bot
        
        announcement = (
            "🔔 <b>SANARWA:</b> An biya duk wanda ya nemi biya yau!\n\n"
            "💰 An gama duk biyan kuɗi na yau\n"
            "⏰ Muna maku fatan alheri, sai gobe karfe 8:00 na safe.\n\n"
            "🤖 Bot zai buɗe karɓar accounts gobe da safe."
        )
        
        await bot.send_message(CHANNEL_ID, announcement)
        
        await message.answer(
            "✅ <b>An tura sanarwa zuwa channel cikin nasara!</b>\n\n"
            "Sanarwar gama biyan kuɗi na yau."
        )
        
    except Exception as e:
        await message.answer(f"❌ <b>Kuskure a turawa channel:</b> {str(e)}")
