import asyncio
import os
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.sessions import StringSession

from config import API_ID, API_HASH

# Global client instance for OTP forwarding
forwarding_client = None

async def create_client():
    """Create a new Telegram client"""
    return TelegramClient(
        StringSession(),
        API_ID,
        API_HASH
    )

async def login_with_otp(phone_number, otp):
    """Login to Telegram using phone number and OTP"""
    client = await create_client()
    
    try:
        await client.connect()
        
        # Send code request
        await client.send_code_request(phone_number)
        
        # Sign in with OTP
        user = await client.sign_in(phone_number, otp)
        
        if user:
            # Get session string
            session_string = client.session.save()
            return client, session_string
        else:
            return None, None
            
    except PhoneCodeInvalidError:
        await client.disconnect()
        return None, None
    except SessionPasswordNeededError:
        await client.disconnect()
        return None, None  # 2FA is enabled
    except Exception as e:
        print(f"Login error: {e}")
        await client.disconnect()
        return None, None

async def client_from_session(session_string):
    """Create client from session string"""
    client = TelegramClient(
        StringSession(session_string),
        API_ID,
        API_HASH
    )
    
    try:
        await client.connect()
        return client
    except Exception as e:
        print(f"Session client error: {e}")
        return None

async def setup_otp_forwarding_client():
    """Setup the main client for OTP forwarding"""
    global forwarding_client
    
    # This would use the main bot's session or a dedicated session
    # For now, we'll create a basic client structure
    forwarding_client = await create_client()
    
    # In a real implementation, you'd login with the bot's main account
    # or use a dedicated forwarding account
    
    return forwarding_client

async def forward_otp_to_buyer(phone_number, otp_message):
    """Forward OTP message to buyer"""
    # This would be implemented to forward OTP messages
    # to the buyer's DM when they try to login
    pass

async def get_phone_from_session(session_string):
    """Get phone number from session"""
    client = await client_from_session(session_string)
    if client:
        try:
            me = await client.get_me()
            phone = me.phone
            await client.disconnect()
            return phone
        except Exception as e:
            print(f"Get phone error: {e}")
            await client.disconnect()
            return None
    return None

async def send_otp_to_phone(phone_number):
    """Send OTP to phone number (initiate login process)"""
    client = await create_client()
    
    try:
        await client.connect()
        result = await client.send_code_request(phone_number)
        await client.disconnect()
        return True
    except Exception as e:
        print(f"Send OTP error: {e}")
        await client.disconnect()
        return False
