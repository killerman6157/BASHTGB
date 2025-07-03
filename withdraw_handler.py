from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_verified_accounts_count
from utils.helpers import is_payment_time_open, get_current_time
from config import ADMIN_ID, PAYMENT_START_TIME, PAYMENT_END_TIME

router = Router()

class WithdrawStates(StatesGroup):
    waiting_for_bank_details = State()

@router.message(Command("withdraw"))
async def withdraw_command(message: types.Message, state: FSMContext):
    """Handle withdraw request"""
    
    # Check if payment time is open
    if not is_payment_time_open():
        current_time = get_current_time()
        await message.answer(
            f"⏰ <b>An rufe biyan kuɗi na yau</b>\n\n"
            f"Za a fara biyan kuɗi gobe da karfe {PAYMENT_START_TIME}:00 na dare (WAT).\n"
            f"Lokaci yanzu: {current_time.strftime('%H:%M')} WAT\n\n"
            f"Don Allah a jira."
        )
        return
    
    # Check if user has verified accounts
    user_id = message.from_user.id
    account_count = await get_verified_accounts_count(user_id)
    
    if account_count == 0:
        await message.answer(
            "❌ <b>Babu verified accounts</b>\n\n"
            "Ba ka da wani account da aka tabbatar da shi.\n"
            "Ka iya tura lambar waya don karɓar accounts."
        )
        return
    
    # Request bank details
    await state.set_state(WithdrawStates.waiting_for_bank_details)
    
    await message.answer(
        f"💰 <b>BUKATAR BIYA</b>\n\n"
        f"📊 <b>Adadin accounts:</b> {account_count}\n\n"
        f"🏦 <b>Maza turo lambar asusun bankinka da sunan mai asusun:</b>\n\n"
        f"📝 <b>Misali:</b>\n"
        f"<code>9131085651 OPay Bashir Rabiu</code>\n\n"
        f"⏰ Za a fara biyan kuɗi daga karfe {PAYMENT_START_TIME}:00 na dare (WAT).\n"
        f"Admin zai tura maka kuɗin ka akan lokaci.\n\n"
        f"💡 <i>Za ka iya amfani da /cancel don soke</i>"
    )

@router.message(WithdrawStates.waiting_for_bank_details)
async def bank_details_handler(message: types.Message, state: FSMContext):
    """Handle bank details submission"""
    
    if message.text == "/cancel":
        await state.clear()
        await message.answer(
            "✅ <b>An soke bukatar biya</b>\n\n"
            "Ka iya sake yin bukatar biya ta /withdraw"
        )
        return
    
    bank_details = message.text.strip()
    
    # Basic validation
    if len(bank_details) < 10:
        await message.answer(
            "❌ <b>Bayanan banki ba su da cikakken bayani</b>\n\n"
            "Don Allah turo cikakken bayanai:\n"
            "• Lambar account\n"
            "• Sunan banki/OPay\n"
            "• Sunan mai account\n\n"
            "📝 <b>Misali:</b>\n"
            "<code>9131085651 OPay Bashir Rabiu</code>"
        )
        return
    
    # Get user info
    user_id = message.from_user.id
    username = message.from_user.username
    account_count = await get_verified_accounts_count(user_id)
    
    # Save withdrawal request
    await save_withdrawal_request(user_id, account_count, bank_details)
    
    # Send confirmation to user
    await message.answer(
        "✅ <b>An karɓi bukatar biya cikin nasara!</b>\n\n"
        f"📊 <b>Adadin accounts:</b> {account_count}\n"
        f"🏦 <b>Bayanan banki:</b> {bank_details}\n\n"
        "📤 An tura bukatar zuwa admin don biya.\n"
        "⏰ Za a biya ku akan lokaci.\n\n"
        "💡 <i>Za ku karɓi sanarwa idan an biya ku</i>"
    )
    
    # Send notification to admin
    await send_withdrawal_notification(user_id, username, account_count, bank_details)
    
    await state.clear()

async def save_withdrawal_request(user_id, account_count, bank_details):
    """Save withdrawal request to database"""
    from database import DB_NAME
    import aiosqlite
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO withdrawal_requests (user_id, account_count, bank_details)
            VALUES (?, ?, ?)
        ''', (user_id, account_count, bank_details))
        await db.commit()

async def send_withdrawal_notification(user_id, username, account_count, bank_details):
    """Send withdrawal notification to admin"""
    from main import bot
    from database import get_user_accounts
    
    try:
        # Get user's phone numbers
        accounts = await get_user_accounts(user_id)
        verified_phones = [phone for phone, status in accounts if status == 'verified']
        
        notification = (
            "💰 <b>BUKATAR BIYA!</b>\n\n"
            f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
            f"🆔 <b>Username:</b> @{username or 'N/A'}\n"
            f"📊 <b>Bukatar biya don accounts guda:</b> {account_count}\n\n"
            f"📱 <b>Lambobin Accounts da aka karba:</b>\n"
        )
        
        for phone in verified_phones:
            notification += f"• <code>{phone}</code>\n"
        
        notification += (
            f"\n🏦 <b>Bayanan Banki:</b> {bank_details}\n\n"
            f"💡 <b>Don tabbatar da biyan:</b>\n"
            f"<code>/mark_paid {user_id} {account_count}</code>"
        )
        
        await bot.send_message(ADMIN_ID, notification)
        
    except Exception as e:
        print(f"Error sending withdrawal notification: {e}")
