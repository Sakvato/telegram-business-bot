"""
Telegram Bot Template - Business Bot
Works from Russia via Cloudflare proxy
"""
import json
import time
import logging
import requests
from pathlib import Path
from database import Database

CONFIG_PATH = Path(__file__).parent / "config.json"
DB_PATH = Path(__file__).parent / "bot_data.db"
PROXY_URL = "https://frog-telegram-proxy.ilaturakov.workers.dev"


class BotAPI:
    """Telegram Bot API via Cloudflare proxy"""

    def __init__(self, bot_token, proxy_url=PROXY_URL):
        self.bot_token = bot_token
        self.proxy_url = proxy_url.rstrip("/")

    def _get(self, method, **params):
        all_params = {"token": self.bot_token, "method": method}
        all_params.update({k: v for k, v in params.items() if v is not None})
        for attempt in range(3):
            try:
                r = requests.get(self.proxy_url, params=all_params, timeout=15)
                return r.json()
            except Exception as e:
                if attempt < 2:
                    time.sleep(1)
                else:
                    return {"ok": False, "error": str(e)}

    def _post(self, method, params=None):
        payload = {
            "token": self.bot_token,
            "method": method,
            "params": params or {},
        }
        for attempt in range(3):
            try:
                r = requests.post(self.proxy_url, json=payload, timeout=15)
                return r.json()
            except Exception as e:
                if attempt < 2:
                    time.sleep(1)
                else:
                    return {"ok": False, "error": str(e)}

    def get_me(self):
        return self._get("getMe")

    def get_updates(self, offset=None, limit=100, timeout=0):
        return self._get("getUpdates", offset=offset, limit=limit, timeout=timeout)

    def send_message(self, chat_id, text, parse_mode="HTML", reply_markup=None):
        params = {"chat_id": chat_id, "text": text}
        if parse_mode:
            params["parse_mode"] = parse_mode
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        return self._post("sendMessage", params)

    def edit_message_text(self, chat_id, message_id, text, parse_mode="HTML", reply_markup=None):
        params = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if parse_mode:
            params["parse_mode"] = parse_mode
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        return self._post("editMessageText", params)

    def answer_callback_query(self, callback_query_id, text=None):
        params = {"callback_query_id": callback_query_id}
        if text:
            params["text"] = text
        return self._post("answerCallbackQuery", params)


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main_menu_kb():
    return {
        "inline_keyboard": [
            [{"text": "New Order", "callback_data": "new_order"}],
            [{"text": "My Orders", "callback_data": "my_orders"}],
            [{"text": "Contact", "callback_data": "contact"}],
        ]
    }


def confirm_kb():
    return {
        "inline_keyboard": [
            [
                {"text": "Confirm", "callback_data": "confirm_yes"},
                {"text": "Cancel", "callback_data": "confirm_no"},
            ]
        ]
    }


def back_kb():
    return {
        "inline_keyboard": [
            [{"text": "Back to Menu", "callback_data": "back_to_menu"}],
        ]
    }


def owner_menu_kb():
    return {
        "inline_keyboard": [
            [{"text": "Statistics", "callback_data": "stats"}],
            [{"text": "Pending Orders", "callback_data": "pending_orders"}],
            [{"text": "Settings", "callback_data": "settings"}],
            [{"text": "Back to Menu", "callback_data": "back_to_menu"}],
        ]
    }


PRODUCTS = ["Product 1", "Product 2", "Product 3", "Service 1", "Service 2"]
STATUS_MAP = {"pending": "Pending", "processing": "Processing", "completed": "Completed", "cancelled": "Cancelled"}

user_states = {}


def handle_message(bot, api, config, db, msg):
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "")
    chat_id = msg.get("chat", {}).get("id")

    if not user_id or not chat_id:
        return

    db.add_user_sync(user_id, msg["from"].get("username"), msg["from"].get("full_name"))

    state = user_states.get(user_id)

    if state and state.get("step") == "waiting_description":
        user_states[user_id] = {"step": "waiting_quantity", "product": state["product"], "description": text}
        kb = {"inline_keyboard": [[{"text": str(i), "callback_data": f"qty_{i}"} for i in range(1, 6)]]}
        api.send_message(chat_id, f"Product: {state['product']}\nDescription: {text}\n\nQuantity:", reply_markup=kb)
        return

    if text == "/start":
        api.send_message(chat_id, config.get("welcome_message", "Welcome!"), reply_markup=main_menu_kb())

    elif text == "/admin" and user_id == config.get("owner_id"):
        api.send_message(chat_id, "<b>Admin Panel:</b>", reply_markup=owner_menu_kb())


def handle_callback(bot, api, config, db, cb):
    user_id = cb.get("from", {}).get("id")
    chat_id = cb.get("message", {}).get("chat", {}).get("id")
    message_id = cb.get("message", {}).get("message_id")
    data = cb.get("data", "")

    if not user_id or not chat_id:
        return

    api.answer_callback_query(cb["id"])

    if data == "back_to_menu":
        user_states.pop(user_id, None)
        api.edit_message_text(chat_id, message_id, config.get("welcome_message", "Welcome!"), reply_markup=main_menu_kb())

    elif data == "new_order":
        kb = {"inline_keyboard": [[{"text": p, "callback_data": f"product_{i}"}] for i, p in enumerate(PRODUCTS)]}
        api.edit_message_text(chat_id, message_id, "Select a product:", reply_markup=kb)

    elif data.startswith("product_"):
        index = int(data.split("_")[1])
        product = PRODUCTS[index]
        user_states[user_id] = {"step": "waiting_description", "product": product}
        api.edit_message_text(chat_id, message_id, f"Product: {product}\n\nDescribe your order:")

    elif data.startswith("qty_"):
        quantity = int(data.split("_")[1])
        state = user_states.get(user_id, {})
        product = state.get("product", "Unknown")
        description = state.get("description", "No description")
        user_states[user_id] = {"step": "confirm", "product": product, "description": description, "quantity": quantity}
        text = f"<b>Order:</b>\nProduct: {product}\nDescription: {description}\nQuantity: {quantity}\n\nConfirm?"
        api.edit_message_text(chat_id, message_id, text, reply_markup=confirm_kb())

    elif data == "confirm_yes":
        state = user_states.pop(user_id, {})
        product = state.get("product", "Unknown")
        description = state.get("description", "")
        quantity = state.get("quantity", 1)
        order_id = db.add_order_sync(user_id, product, description, quantity)

        owner_id = config.get("owner_id")
        if owner_id:
            username = cb.get("from", {}).get("username", "")
            owner_text = f"<b>New order #{order_id}</b>\n\nClient: @{username}\nProduct: {product}\nDescription: {description}\nQty: {quantity}"
            api.send_message(owner_id, owner_text)

        api.edit_message_text(chat_id, message_id, f"Order #{order_id} confirmed!\n\n{config.get('order_success_message', 'Thank you!')}", reply_markup=main_menu_kb())

    elif data == "confirm_no":
        user_states.pop(user_id, None)
        api.edit_message_text(chat_id, message_id, "Order cancelled.", reply_markup=main_menu_kb())

    elif data == "my_orders":
        orders = db.get_user_orders_sync(user_id)
        if not orders:
            api.edit_message_text(chat_id, message_id, "No orders yet.", reply_markup=back_kb())
        else:
            text = "<b>Your orders:</b>\n\n"
            for o in orders[:10]:
                oid, uid, prod, desc, qty, status, created = o
                text += f"#{oid} | {prod} | {STATUS_MAP.get(status, status)}\n"
            api.edit_message_text(chat_id, message_id, text, reply_markup=back_kb())

    elif data == "contact":
        api.edit_message_text(chat_id, message_id, f"Contact: {config.get('contact_info', '@support')}", reply_markup=back_kb())

    elif data == "stats":
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], "Access denied", show_alert=True)
            return
        stats = db.get_stats_sync()
        text = f"<b>Statistics:</b>\n\nUsers: {stats['total_users']}\nOrders: {stats['total_orders']}\nPending: {stats['pending_orders']}\nCompleted: {stats['completed_orders']}"
        api.edit_message_text(chat_id, message_id, text, reply_markup=owner_menu_kb())

    elif data == "pending_orders":
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], "Access denied", show_alert=True)
            return
        orders = db.get_all_orders_sync("pending")
        if not orders:
            api.edit_message_text(chat_id, message_id, "No pending orders.", reply_markup=owner_menu_kb())
        else:
            text = "<b>Pending orders:</b>\n\n"
            for o in orders[:10]:
                oid, uid, prod, desc, qty, status, created = o
                user = db.get_user_sync(uid)
                uname = user[1] if user and user[1] else f"ID:{uid}"
                text += f"#{oid} | {prod} | @{uname}\n"
            api.edit_message_text(chat_id, message_id, text, reply_markup=owner_menu_kb())

    elif data == "settings":
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], "Access denied", show_alert=True)
            return
        api.edit_message_text(chat_id, message_id, "<b>Bot Settings:</b>\n\nWelcome message and more.", reply_markup=back_kb())


def main():
    config = load_config()
    api = BotAPI(config["bot_token"])
    db = Database(str(DB_PATH))
    db.init_sync()

    me = api.get_me()
    if not me.get("ok"):
        print(f"ERROR: {me}")
        return

    bot_username = me["result"]["username"]
    print(f"Bot started: @{bot_username}")

    offset = 0
    while True:
        try:
            updates = api.get_updates(offset=offset, limit=100, timeout=30)
            if not updates.get("ok"):
                print(f"Update error: {updates}")
                time.sleep(5)
                continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                if "message" in update and "text" in update["message"]:
                    handle_message(None, api, config, db, update["message"])

                elif "callback_query" in update:
                    handle_callback(None, api, config, db, update["callback_query"])

        except KeyboardInterrupt:
            print("\nBot stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
