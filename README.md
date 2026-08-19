# Telegram Business Bot

Telegram bot for small business: orders, notifications, analytics, partner program. Works from Russia via Cloudflare proxy.

## Features

**Free:**
- Order management (customers place orders through bot)
- Notification to owner about new orders
- Basic analytics (users, orders, pending/completed)
- Order status management (processing, completed, cancelled)
- Customer notifications on status change
- Language selection (Russian/English)
- Partner/referral program (earn from referrals)
- Configurable messages and products
- SQLite database (no server needed)
- Docker-ready
- Works from Russia (Cloudflare proxy)

**Pro (paid):**
- Payment integration (ЮMoney, Киви, card transfers)
- Multi-admin support (team management)
- Auto-responses (AI-powered customer support)
- CRM integration (1C, amoCRM, Bitrix24)
- Advanced analytics (charts, export)
- Custom branding (your logo, colors)
- Priority support

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
  "contact_info": "@your_contact",
  "partner_percent": 10
}
```
3. Install and run:
```bash
pip install -r requirements.txt
python bot.py
```

## Commands

- `/start` - Main menu (with referral support)
- `/admin` - Admin panel (owner only)

## Partner Program

Users can invite friends and earn a percentage from each purchase:
1. User clicks "Partner Program" in menu
2. Gets unique referral link: `t.me/BotName?refUSER_ID`
3. Shares link with friends
4. Earns configured percentage from each friend's purchase

Configure `partner_percent` in config.json (default: 10%).

## How It Works

Customers interact with the bot through inline buttons:
1. Click "New Order" to place an order
2. Select a product
3. Describe the order
4. Select quantity
5. Confirm

Owner receives notification with order details.
Owner can change order status (processing, completed, cancelled).
Customer receives notification on status change.

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

## Pro Features

Need payment processing, multi-admin, or CRM integration? 

**Get Pro version:** Contact @Sakvato on Telegram

**Pricing:**
- Pro license: $99 (one-time)
- Setup + customization: $199
- Monthly support: $49/month

## Setup Service

Don't want to set up yourself? I'll do it for you:

- Basic setup: $49
- Full customization: $149
- Priority support: $99/month

**Contact:** @Sakvato on Telegram

## License

MIT
