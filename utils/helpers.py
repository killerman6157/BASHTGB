import re
import pytz
from datetime import datetime
from config import (
    TIMEZONE, 
    ACCOUNT_RECEIVING_START, 
    ACCOUNT_RECEIVING_END,
    PAYMENT_START_TIME,
    PAYMENT_END_TIME,
    ADMIN_ID
)

def get_current_time():
    """Get current time in WAT timezone"""
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)

def is_account_receiving_open():
    """Check if account receiving is currently open (8AM-10PM WAT)"""
    current_time = get_current_time()
    current_hour = current_time.hour
    
    return ACCOUNT_RECEIVING_START <= current_hour < ACCOUNT_RECEIVING_END

def is_payment_time_open():
    """Check if payment time is open (8PM-8AM WAT)"""
    current_time = get_current_time()
    current_hour = current_time.hour
    
    # Payment time is from 8PM to 8AM (crosses midnight)
    return current_hour >= PAYMENT_START_TIME or current_hour < PAYMENT_END_TIME

def validate_phone_number(phone_number):
    """Validate phone number format"""
    # Remove spaces and hyphens
    phone = re.sub(r'[\s\-]', '', phone_number)
    
    # Check if it starts with + and has 10-15 digits
    pattern = r'^\+?[1-9]\d{9,14}$'
    
    return bool(re.match(pattern, phone))

def format_phone_number(phone_number):
    """Format phone number consistently"""
    # Remove spaces and hyphens
    phone = re.sub(r'[\s\-]', '', phone_number)
    
    # Add + if not present
    if not phone.startswith('+'):
        phone = '+' + phone
    
    return phone

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_ID

def get_country_from_phone(phone_number):
    """Get country from phone number (basic implementation)"""
    # Basic country detection based on phone prefixes
    phone = phone_number.replace('+', '')
    
    if phone.startswith('234'):
        return 'Nigeria'
    elif phone.startswith('1'):
        return 'USA/Canada'
    elif phone.startswith('44'):
        return 'UK'
    elif phone.startswith('33'):
        return 'France'
    elif phone.startswith('49'):
        return 'Germany'
    else:
        return 'Unknown'

def format_time_remaining(minutes):
    """Format time remaining in a readable format"""
    if minutes < 1:
        return "Karasa minti 1"
    elif minutes == 1:
        return "Minti 1"
    else:
        return f"Mintuna {minutes}"

def get_status_emoji(status):
    """Get emoji for account status"""
    status_emojis = {
        'pending': '⏳',
        'unverified': '❌',
        'verified': '✅',
        'paid': '💰'
    }
    return status_emojis.get(status, '❓')

def get_status_text_hausa(status):
    """Get Hausa text for account status"""
    status_texts = {
        'pending': 'Ana jira OTP',
        'unverified': 'Ba a tabbatar ba',
        'verified': 'An tabbatar',
        'paid': 'An biya'
    }
    return status_texts.get(status, status)

def format_account_list(accounts):
    """Format list of accounts for display"""
    if not accounts:
        return "Babu accounts"
    
    formatted = []
    for phone, status in accounts:
        emoji = get_status_emoji(status)
        text = get_status_text_hausa(status)
        formatted.append(f"{emoji} <code>{phone}</code> — <b>{text}</b>")
    
    return '\n'.join(formatted)

def is_valid_otp(otp):
    """Check if OTP format is valid"""
    # OTP should be 5-6 digits
    return bool(re.match(r'^\d{5,6}$', otp))

def get_next_receiving_time():
    """Get next time account receiving will be open"""
    current_time = get_current_time()
    
    if is_account_receiving_open():
        # Currently open, next close time
        next_time = current_time.replace(
            hour=ACCOUNT_RECEIVING_END,
            minute=0,
            second=0,
            microsecond=0
        )
        return next_time, 'close'
    else:
        # Currently closed, next open time
        if current_time.hour < ACCOUNT_RECEIVING_START:
            # Same day
            next_time = current_time.replace(
                hour=ACCOUNT_RECEIVING_START,
                minute=0,
                second=0,
                microsecond=0
            )
        else:
            # Next day
            next_time = current_time.replace(
                hour=ACCOUNT_RECEIVING_START,
                minute=0,
                second=0,
                microsecond=0
            )
            next_time = next_time.replace(day=next_time.day + 1)
        
        return next_time, 'open'

def calculate_timeout_remaining(timeout_at):
    """Calculate remaining time until timeout"""
    if isinstance(timeout_at, str):
        timeout_at = datetime.fromisoformat(timeout_at)
    
    current_time = datetime.now()
    
    if current_time >= timeout_at:
        return 0
    
    remaining = timeout_at - current_time
    return remaining.total_seconds()

def format_bank_details(details):
    """Format bank details for display"""
    # Basic formatting - you can enhance this
    return details.strip()

def is_valid_bank_details(details):
    """Validate bank details format"""
    # Basic validation - should have at least account number and name
    parts = details.split()
    return len(parts) >= 3 and any(part.isdigit() for part in parts)
