import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# Telegram Client Configuration
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

# Database Configuration
DB_NAME = "telegram_accounts.db"

# Business Configuration
PAYMENT_START_TIME = 20  # 8:00 PM WAT
PAYMENT_END_TIME = 8     # 8:00 AM WAT
ACCOUNT_RECEIVING_START = 8  # 8:00 AM WAT
ACCOUNT_RECEIVING_END = 22   # 10:00 PM WAT

# Security Configuration
DEFAULT_2FA_PASSWORD = "Bashir@111#"
OTP_TIMEOUT_MINUTES = 1

# Status Constants
STATUS_PENDING = "pending"
STATUS_UNVERIFIED = "unverified"
STATUS_VERIFIED = "verified"
STATUS_PAID = "paid"

# Time Constants
TIMEZONE = "Africa/Lagos"  # WAT timezone
RESUBMISSION_COOLDOWN_DAYS = 7  # 1 week for verified accounts
