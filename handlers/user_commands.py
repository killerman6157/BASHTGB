from aiogram import Router, types, F
from aiogram.filters import Command

from database import get_user_accounts
from utils.helpers import is_account_receiving_open

router = Router()

@router.message(Command("myaccounts"))
async def my_accounts(message: types.Message):
    """Show user's accounts with status"""
    
    user_id = message.from_user.id
    accounts = await get_user_accounts(user_id)
    
    if not accounts:
        await message.answer(
            "📋 <b>Babu accounts</b>\n\n"
            "Ba ka da wata lambar da ka tura tukuna.\n"
            "Ka iya tura lambar waya don farawa."
        )
        return
    
    response = "📋 <b>Lambar da ka tura:</b>\n\n"
    
    status_counts = {'pending': 0, 'unverified': 0, 'verified': 0, 'paid': 0}
    
    for phone, status in accounts:
        status_counts[status] += 1
        
        status_emoji = {
            'pending': '⏳',
            'unverified': '❌',
            'verified': '✅',
            'paid': '💰'
        }.get(status, '❓')
        
        status_text = {
            'pending': 'Ana jira OTP',
            'unverified': 'Ba a tabbatar ba',
            'verified': 'An tabbatar',
            'paid': 'An biya'
        }.get(status, status)
        
        response += f"{status_emoji} <code>{phone}</code> — <b>{status_text}</b>\n"
    
    response += f"\n📊 <b>Taƙaitawa:</b>\n"
    response += f"⏳ Ana jira: {status_counts['pending']}\n"
    response += f"❌ Ba a tabbatar ba: {status_counts['unverified']}\n"
    response += f"✅ An tabbatar: {status_counts['verified']}\n"
    response += f"💰 An biya: {status_counts['paid']}\n"
    
    if status_counts['unverified'] > 0:
        response += f"\n💡 <b>Shawarar:</b> Ka iya sake tura unverified accounts koyaushe."
    
    await message.answer(response)

@router.message(Command("help"))
async def help_command(message: types.Message):
    """Show help message"""
    
    help_text = (
        "🤖 <b>TAIMAKO - TELEGRAM ACCOUNT BOT</b>\n\n"
        
        "📋 <b>Commands:</b>\n"
        "• <code>/start</code> - Fara amfani da bot\n"
        "• <code>/myaccounts</code> - Duba accounts da ka tura\n"
        "• <code>/withdraw</code> - Nemi biyan kuɗi\n"
        "• <code>/cancel</code> - Soke aikin da ke gudana\n"
        "• <code>/help</code> - Nuna wannan taimako\n\n"
        
        "📱 <b>Yadda ake amfani:</b>\n"
        "1. Turo lambar waya (misali: +2348167757987)\n"
        "2. Turo OTP cikin minti 1\n"
        "3. Bot zai shiga account da saita tsaro\n"
        "4. Account zai zama 'verified'\n"
        "5. Ka iya nemi biya ta /withdraw\n\n"
        
        "⚠️ <b>Muhimmanci:</b>\n"
        "• Cire 2FA kafin tura account\n"
        "• Ka da minti 1 don tura OTP\n"
        "• Unverified accounts za ka iya sake tura su\n"
        "• Verified accounts za a hana su har mako 1\n\n"
        
        "⏰ <b>Lokutan aiki:</b>\n"
        "• Karɓar accounts: 8:00 AM - 10:00 PM WAT\n"
        "• Biyan kuɗi: 8:00 PM - 8:00 AM WAT\n\n"
        
        "💡 <b>Status nuna:</b>\n"
        "⏳ Pending - Ana jira OTP\n"
        "❌ Unverified - Ba a tabbatar ba\n"
        "✅ Verified - An tabbatar\n"
        "💰 Paid - An biya"
    )
    
    await message.answer(help_text)

@router.message(Command("status"))
async def status_command(message: types.Message):
    """Show bot status"""
    
    from utils.helpers import get_current_time
    
    current_time = get_current_time()
    receiving_open = is_account_receiving_open()
    
    status_text = (
        "🤖 <b>BOT STATUS</b>\n\n"
        f"⏰ <b>Lokaci yanzu:</b> {current_time.strftime('%H:%M:%S WAT')}\n"
        f"📅 <b>Ranar:</b> {current_time.strftime('%d/%m/%Y')}\n\n"
        f"📱 <b>Karɓar accounts:</b> {'✅ Buɗe' if receiving_open else '❌ Rufe'}\n"
        f"💰 <b>Biyan kuɗi:</b> {'✅ Buɗe' if not receiving_open else '❌ Rufe'}\n\n"
    )
    
    if receiving_open:
        status_text += "📋 <b>Ka iya tura lambar waya yanzu!</b>"
    else:
        status_text += "⏰ <b>Za a buɗe gobe karfe 8:00 na safe</b>"
    
    await message.answer(status_text)
