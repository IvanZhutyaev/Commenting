# Telegram Story Viewer & Promo Bot

## 📌 Project Description

This project provides an automated Telegram bot that:
1. Views stories of group/channel members
2. Sends promotional comments/messages
3. Includes anti-spam protection and error handling

Two implementation versions are included with different approaches.

## ✨ Features

### Core Functionality:
- Automated story viewing for group/channel members
- Promo message delivery after story views
- Randomized delays between actions
- Comprehensive error handling (FloodWait, privacy restrictions)
- Blacklist system for problematic users

### Advanced Features:
- Progressive delay increases as daily limits approach
- Random user skips for natural behavior
- Periodic long pauses
- Detailed operation logging
- Success/failure statistics

## 🚀 Installation

### Requirements:
- Python 3.7+
- Required packages (see `requirements.txt` below)

### requirements.txt:
```
pyaes==1.6.1
pyasn1==0.6.1
rsa==4.9
Telethon==1.39.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Get your API ID and HASH from [my.telegram.org](https://my.telegram.org/)
2. Customize settings in the script:
   - `COMMENT_TEXT` - Your promotional message
   - `daily_limit` - Daily action limit (default: 150)
   - Delay timings in `safe_delay()`

## ⚠️ Important Notes

1. Telegram may temporarily restrict accounts for excessive activity
2. Recommended to use aged accounts (not newly created)
3. Avoid aggressive timing settings
4. Won't work with users who have strict privacy settings

## 📊 Statistics

Both scripts provide detailed stats:
- Successful story views
- Error counts
- Daily limit progress
- Runtime information

## 📜 License

MIT License - use at your own risk. No liability for account restrictions.
