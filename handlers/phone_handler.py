import re
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_pending_submission, is_phone_blocked
from utils.helpers import is_account_receiving_open, validate_phone_number
from services.telegram_client import send_otp_to_phone

router = Router()

class PhoneStates(StatesGroup):
    waiting_for_otp = State()

@router.message(F.text.regexp(r'^\+?[1-9]\d{1,14}$'))
async def phone_number_handler(message: types.Message, state: FSMContext):
    """Handle phone number submission"""
    
    # Check if account receiving is open
    if not is_account_receiving_open():
        await message.answer(
            "⏰ <b>An rufe karbar Telegram accounts na yau</b>\n\n"
            "Don Allah a gwada gobe karfe 8:00 na safe."
        )
        return
    
    phone_number = message.text.strip()
    
    # Validate phone number format
    if not validate_phone_number(phone_number):
        await message.answer(
            "❌ <b>Kuskure a lambar waya!</b>\n\n"
            "Don Allah turo lambar waya da kwance misali:\n"
            "+2348167757987"
        )
        return
    
    # Check if phone is blocked (verified within last week)
    if await is_phone_blocked(phone_number):
        await message.answer(
            "⚠️ <b>Kuskure! An riga an yi rajistar wannan lambar!</b>\n\n"
            f"📱 <b>Lambar:</b> {phone_number}\n"
            f"🌍 <b>Ƙasa:</b> Nigeria\n\n"
            "Ba za ka iya sake tura wannan lambar ba sai nan da mako ɗaya."
        )
        return
    
    # Add to pending submissions
    await add_pending_submission(message.from_user.id, phone_number)
    
    # Store phone number in state
    await state.update_data(phone_number=phone_number)
    await state.set_state(PhoneStates.waiting_for_otp)
    
    # Send processing message
    await message.answer(
        "🔄 <b>Ana sarrafawa... Don Allah a jira.</b>\n\n"
        f"📱 An tura lambar sirri (OTP) zuwa lambar: <code>{phone_number}</code>\n\n"
        "⏱️ <b>Ka da minti 1 don tura OTP</b>\n"
        "Idan ba ka tura OTP ba, account zai zama 'unverified'\n\n"
        "Don Allah ka tura lambar sirrin a nan.\n\n"
        "💡 <i>Za ka iya amfani da /cancel don soke aikin</i>"
    )

@router.message(F.text == "/cancel")
async def cancel_handler(message: types.Message, state: FSMContext):
    """Handle cancellation"""
    await state.clear()
    await message.answer(
        "✅ <b>An soke aikin cikin nasara.</b>\n\n"
        "Ka iya fara sabo ta hanyar tura lambar waya."
  )
