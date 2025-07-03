import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import API_ID, API_HASH
from database import DB_NAME
import aiosqlite

# Global client for OTP forwarding
otp_client = None

async def setup_otp_forwarder():
    """Setup OTP forwarding service"""
    global otp_client
    
    # Create client with a dedicated session for OTP forwarding
    # In a real implementation, you would use a dedicated account
    otp_client = TelegramClient(
        StringSession(),
        API_ID,
        API_HASH
    )
    
    try:
        await otp_client.connect()
        
        # Add event handler for Telegram system messages
        otp_client.add_event_handler(
            handle_telegram_system_message,
            events.NewMessage(from_users=777000)  # Telegram system bot
        )
        
        print("OTP forwarder setup completed")
        
    except Exception as e:
        print(f"Error setting up OTP forwarder: {e}")

async def handle_telegram_system_message(event):
    """Handle messages from Telegram system bot (777000)"""
    
    try:
        message_text = event.message.message
        
        # Check if this is an OTP message
        if any(keyword in message_text.lower() for keyword in ['login', 'code', 'otp', 'verification']):
            # Get the phone number from the session
            phone_number = await get_phone_from_current_session(event.client)
            
            if phone_number:
                # Find the buyer for this phone number
                buyer_id = await get_buyer_for_phone(phone_number)
                
                if buyer_id:
                    # Forward OTP to buyer
                    await forward_otp_to_buyer(buyer_id, message_text)
                    
    except Exception as e:
        print(f"Error handling Telegram system message: {e}")

async def get_phone_from_current_session(client):
    """Get phone number from current session"""
    try:
        me = await client.get_me()
        return me.phone
    except Exception as e:
        print(f"Error getting phone from session: {e}")
        return None

async def get_buyer_for_phone(phone_number):
    """Get buyer ID for a phone number"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT buyer_id FROM verified_accounts
            WHERE phone_number = ? AND buyer_id IS NOT NULL
        ''', (phone_number,))
        result = await cursor.fetchone()
        return result[0] if result else None

async def forward_otp_to_buyer(buyer_id, otp_message):
    """Forward OTP message to buyer"""
    try:
        # Use aiogram Bot directly with token
        from aiogram import Bot
        from config import BOT_TOKEN
        
        bot = Bot(token=BOT_TOKEN)
        
        formatted_message = (
            "🔐 <b>OTP daga Telegram:</b>\n\n"
            f"<code>{otp_message}</code>\n\n"
            "📱 Wannan OTP ne don account da ka saya."
        )
        
        await bot.send_message(buyer_id, formatted_message, parse_mode='HTML')
        await bot.session.close()
        
    except Exception as e:
        print(f"Error forwarding OTP to buyer: {e}")

async def add_buyer_mapping(phone_number, buyer_id):
    """Add buyer mapping for a phone number"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE verified_accounts
            SET buyer_id = ?
            WHERE phone_number = ? AND status = 'verified'
        ''', (buyer_id, phone_number))
        await db.commit()

async def remove_buyer_mapping(phone_number):
    """Remove buyer mapping for a phone number"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE verified_accounts
            SET buyer_id = NULL
            WHERE phone_number = ?
        ''', (phone_number,))
        await db.commit()

async def start_otp_forwarding():
    """Start OTP forwarding client"""
    global otp_client
    
    if otp_client and not otp_client.is_connected():
        try:
            if not otp_client.is_connected():
                await otp_client.connect()
            print("OTP forwarding client started")
        except Exception as e:
            print(f"Error starting OTP forwarding client: {e}")

async def stop_otp_forwarding():
    """Stop OTP forwarding client"""
    global otp_client
    
    if otp_client and otp_client.is_connected():
        try:
            otp_client.disconnect()
            print("OTP forwarding client stopped")
        except Exception as e:
            print(f"Error stopping OTP forwarding client: {e}")
