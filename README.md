# Telegram Account Trading Bot

A professional Telegram bot for trading Telegram accounts with automated verification, 2FA setup, and payment processing.

## Features

### 🤖 Automated Account Management
- Phone number submission and OTP verification
- Automatic 2FA password setup (Bashir@111#)
- Account status tracking (pending, unverified, verified, paid)
- Session termination from seller's device

### ⏰ Time-Based Operations
- Account receiving: 8:00 AM - 10:00 PM WAT
- Payment processing: 8:00 PM - 8:00 AM WAT
- Automatic cleanup of expired submissions

### 🔐 Security Features
- Real OTP forwarding to buyers via DM
- Secure session management
- 2FA protection for all verified accounts
- Phone number blocking after verification (1 week cooldown)

### 👨‍💼 Admin Controls
- `/accept [user_id] [phone_number]` - Accept verified accounts
- `/stats` - View bot statistics
- `/user_accounts [user_id]` - Check user's accounts
- `/mark_paid [user_id] [count]` - Mark accounts as paid
- `/completed_today_payment` - Announce payment completion

### 👤 User Commands
- `/start` - Start using the bot
- `/myaccounts` - View your submitted accounts
- `/withdraw` - Request payment with bank details
- `/cancel` - Cancel current operation
- `/help` - Show help information
- `/status` - Check bot status

## Installation

### Prerequisites
- Python 3.11+
- Termux (for Android) or Linux environment
- Telegram Bot Token
- Telegram API credentials

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/telegram-account-bot.git
cd telegram-account-bot
```

2. **Install dependencies:**
```bash
pip install aiogram telethon aiosqlite apscheduler pytz python-dotenv
```

3. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_user_id
CHANNEL_ID=your_channel_id
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number
```

4. **Run the bot:**
```bash
python main.py
```

## Getting API Credentials

### Bot Token
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token

### Admin ID
1. Message @userinfobot on Telegram
2. Copy your user ID

### Channel ID
1. Add @userinfobot to your channel
2. Copy the channel ID

### API ID & API Hash
1. Visit https://my.telegram.org/apps
2. Create a new application
3. Copy API ID and API Hash

## Project Structure

```
telegram-account-bot/
├── main.py                 # Main application entry point
├── config.py              # Configuration and settings
├── database.py            # Database operations
├── .env.example           # Environment variables template
├── handlers/              # Message handlers
│   ├── start.py          # Start command handler
│   ├── phone_handler.py  # Phone number processing
│   ├── otp_handler.py    # OTP verification
│   ├── admin_commands.py # Admin commands
│   ├── user_commands.py  # User commands
│   └── withdraw_handler.py # Withdrawal processing
├── services/             # Business logic services
│   ├── telegram_client.py # Telegram client operations
│   ├── account_manager.py # Account management
│   ├── scheduler.py      # Scheduled tasks
│   └── otp_forwarder.py  # OTP forwarding service
└── utils/               # Utility functions
    ├── helpers.py       # Helper functions
    └── status_manager.py # Status management
```

## How It Works

### Account Submission Flow
1. Seller submits phone number via bot
2. Bot initiates OTP request to phone
3. Seller has 1 minute to provide OTP
4. If successful: Account becomes "verified"
5. If failed/timeout: Account becomes "unverified"

### Verification Process
1. Bot logs into account using OTP
2. Sets up 2FA password (Bashir@111#)
3. Terminates session from seller's device
4. Notifies admin of verified account
5. Maps account for OTP forwarding to buyer

### Payment Processing
1. Seller requests withdrawal via `/withdraw`
2. Provides bank details (account number, bank name, account name)
3. Admin receives notification with account details
4. Admin processes payment and marks as paid

### OTP Forwarding
1. When buyer tries to login to purchased account
2. Telegram sends OTP to account
3. Bot captures OTP and forwards to buyer's DM
4. Buyer can complete login process

## Database Schema

### Tables
- `users` - User registration data
- `pending_submissions` - Temporary OTP waiting period
- `unverified_accounts` - Failed verification attempts
- `verified_accounts` - Successfully verified accounts
- `withdrawal_requests` - Payment requests
- `admin_notifications` - Admin activity log

## Business Hours

- **Account Receiving:** 8:00 AM - 10:00 PM WAT
- **Payment Processing:** 8:00 PM - 8:00 AM WAT
- **Timezone:** West Africa Time (WAT)

## Security Features

- Phone number validation and formatting
- OTP timeout protection (1 minute limit)
- Automatic 2FA setup on all verified accounts
- Session termination from seller devices
- Secure buyer-account mapping for OTP forwarding
- Admin-only sensitive commands

## Error Handling

- Comprehensive error logging
- Graceful failure recovery
- User-friendly error messages in Hausa
- Automatic cleanup of expired data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Ensure compliance with Telegram's Terms of Service.

## Support

For support or questions, contact the repository maintainer.

---

**Note:** This bot handles real financial transactions and Telegram accounts. Use responsibly and ensure proper security measures are in place.
