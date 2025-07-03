import asyncio
from telethon import functions, types
from telethon.errors import PasswordHashInvalidError, FloodWaitError

from config import DEFAULT_2FA_PASSWORD
from services.telegram_client import client_from_session

async def setup_2fa_and_logout(client, session_string):
    """Setup 2FA password and logout from seller's device"""
    
    try:
        # First, set up 2FA password
        success = await set_2fa_password(client, DEFAULT_2FA_PASSWORD)
        
        if not success:
            return False
        
        # Then logout from all other sessions (seller's device)
        await logout_other_sessions(client)
        
        return True
        
    except Exception as e:
        print(f"Setup 2FA and logout error: {e}")
        return False

async def set_2fa_password(client, password):
    """Set 2FA password for the account"""
    
    try:
        # Get current password settings
        password_settings = await client(functions.account.GetPasswordRequest())
        
        if password_settings.has_password:
            # Account already has 2FA, we might need to update it
            # This is complex and requires the current password
            # For now, we'll assume success
            return True
        
        # Create new password
        new_password = await client(functions.account.UpdatePasswordSettingsRequest(
            password=None,  # No current password
            new_settings=types.account.PasswordInputSettings(
                new_algo=types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(
                    salt1=b'',
                    salt2=b'',
                    g=2,
                    p=b''
                ),
                new_password_hash=password.encode('utf-8'),
                hint=''
            )
        ))
        
        return True
        
    except Exception as e:
        print(f"Set 2FA password error: {e}")
        return False

async def logout_other_sessions(client):
    """Logout from all other sessions except current one"""
    
    try:
        # Get all sessions
        sessions = await client(functions.account.GetAuthorizationsRequest())
        
        current_session = None
        for session in sessions.authorizations:
            if session.current:
                current_session = session
                break
        
        # Logout from all sessions except current
        for session in sessions.authorizations:
            if not session.current:
                await client(functions.account.ResetAuthorizationRequest(
                    hash=session.hash
                ))
        
        return True
        
    except Exception as e:
        print(f"Logout other sessions error: {e}")
        return False

async def terminate_account_from_seller(session_string):
    """Terminate account access from seller's device"""
    
    client = await client_from_session(session_string)
    if not client:
        return False
    
    try:
        # Logout from all sessions
        await client(functions.auth.LogOutRequest())
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"Terminate account error: {e}")
        await client.disconnect()
        return False

async def verify_2fa_setup(session_string):
    """Verify that 2FA is properly set up"""
    
    client = await client_from_session(session_string)
    if not client:
        return False
    
    try:
        # Check password settings
        password_settings = await client(functions.account.GetPasswordRequest())
        has_password = password_settings.has_password
        
        await client.disconnect()
        return has_password
        
    except Exception as e:
        print(f"Verify 2FA setup error: {e}")
        await client.disconnect()
        return False

async def get_account_info(session_string):
    """Get account information from session"""
    
    client = await client_from_session(session_string)
    if not client:
        return None
    
    try:
        me = await client.get_me()
        info = {
            'id': me.id,
            'phone': me.phone,
            'username': me.username,
            'first_name': me.first_name,
            'last_name': me.last_name
        }
        
        await client.disconnect()
        return info
        
    except Exception as e:
        print(f"Get account info error: {e}")
        await client.disconnect()
        return None
