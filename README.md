# Telegram Business Bot

Telegram bot for small business: orders, notifications, analytics. Works from Russia via Cloudflare proxy.

## Features

- Order management (customers place orders through bot)
- Notification to owner about new orders
- Basic analytics (users, orders, pending/completed)
- Configurable messages and products
- SQLite database (no server needed)
- Docker-ready
- Works from Russia (Cloudflare proxy)

## Quick Start

1. Create a bot in [@BotFather](https://t.me/BotFather) and get token
2. Edit `config.json`:
```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "bot_username": "your_bot_username",
  "bot_name": "My Business Bot",
  "owner_id": 123456789,
  "welcome_message": "Welcome!",
  "order_success_message": "Order received!",
  "contact_info": "@your_contact"
}
```
3. Install and run:
```bash
pip install -r requirements.txt
python bot.py
```

## Commands

- `/start` - Main menu
- `/admin` - Admin panel (owner only)

## How It Works

Customers interact with the bot through inline buttons:
1. Click "New Order" to place an order
2. Select a product
3. Describe the order
4. Select quantity
5. Confirm

Owner receives notification with order details.

## Tech Stack

- Python 3.10+
- requests
- SQLite
- Cloudflare Worker proxy (for Russia)

## Docker

```bash
docker build -t my-bot .
docker run my-bot
```

## Support

If this bot helped you, consider buying me a coffee:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/YOUR_USERNAME)

## License

MIT
