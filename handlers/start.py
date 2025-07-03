from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import add_user
from config import ACCOUNT_RECEIVING_START, ACCOUNT_RECEIVING_END
from utils.helpers import is_account_receiving_open, get_current_time

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """Handle /start command"""
    user = message.from_user
    
    # Add user to database
    await add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Clear any existing state
    await state.clear()
    
    # Check if account receiving is open
    if not is_account_receiving_open():
        current_time = get_current_time()
        await message.answer(
            f"⏰ <b>An rufe karbar Telegram accounts na yau</b>\n\n"
            f"An rufe karbar accounts da karfe {ACCOUNT_RECEIVING_END}:00 na dare (WAT).\n"
            f"Za a sake buɗewa gobe karfe {ACCOUNT_RECEIVING_START}:00 na safe.\n\n"
            f"Lokaci yanzu: {current_time.strftime('%H:%M')} WAT\n"
            f"Don Allah a gwada gobe."
        )
        return
    
    welcome_message = (
        "🤖 <b>Barka da zuwa cibiyar karbar Telegram accounts!</b>\n\n"
        "Don farawa, turo lambar wayar account din da kake son sayarwa.\n"
        "<i>Misali: +2348167757987</i>\n\n"
        "⚠️ <b>Muhimmanci:</b>\n"
        "• Tabbatar ka cire Two-Factor Authentication (2FA) kafin ka tura\n"
        "• Bot zai ba ka minti 1 don tura OTP\n"
        "• Idan ba ka tura OTP ba, account zai zama 'unverified'\n"
        "• Unverified accounts za ka iya sake tura su koyaushe\n"
        "• Verified accounts za a hana su har mako 1\n\n"
        "📋 <b>Commands:</b>\n"
        "/myaccounts - Duba accounts da ka tura\n"
        "/withdraw - Nemi biyan kuɗi\n"
        "/cancel - Soke aikin da ke gudana"
    )
    
    await message.answer(welcome_message)
