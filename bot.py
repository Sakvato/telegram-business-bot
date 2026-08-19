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

MESSAGES = {
    "ru": {
        "welcome": "Добро пожаловать!\n\nЯ помогу вам управлять бизнесом.\nИспользуйте меню ниже:",
        "lang_selected": "Язык изменён на русский",
        "new_order": "Новый заказ",
        "my_orders": "Мои заказы",
        "contact": "Контакт",
        "back_to_menu": "Назад в меню",
        "back_to_admin": "Назад в админку",
        "select_product": "Выберите товар:",
        "describe_order": "Опишите ваш заказ:",
        "quantity": "Количество:",
        "confirm": "Подтвердить",
        "cancel": "Отмена",
        "order_summary": "<b>Заказ:</b>\nТовар: {product}\nОписание: {desc}\nКоличество: {qty}\n\nПодтвердить?",
        "order_confirmed": "Заказ #{order_id} подтверждён!\n\n{success}",
        "order_cancelled": "Заказ отменён.",
        "no_orders": "Заказов пока нет.",
        "your_orders": "<b>Ваши заказы:</b>\n\n",
        "contact_info": "Контакт: {info}",
        "admin_panel": "<b>Панель администратора:</b>",
        "statistics": "Статистика",
        "all_orders": "Все заказы",
        "pending_orders": "Ожидающие заказы",
        "settings": "Настройки",
        "access_denied": "Доступ запрещён",
        "no_pending": "Нет ожидающих заказов.",
        "no_orders_list": "Нет заказов.",
        "pending_list": "<b>Ожидающие заказы:</b>\n\nНажмите на заказ для действий.",
        "all_orders_list": "<b>Все заказы:</b>\n\nНажмите на заказ для действий.",
        "settings_text": "<b>Настройки бота:</b>\n\nПриветственное сообщение и другое.",
        "stats_text": "<b>Статистика:</b>\n\nПользователи: {users}\nЗаказы: {orders}\nОжидают: {pending}\nВыполнены: {completed}",
        "lang_button": "Язык",
        "select_language": "Выберите язык:",
        "order_detail": "<b>Заказ #{order_id}</b>\n\nКлиент: @{username}\nТовар: {product}\nОписание: {desc}\nКоличество: {qty}\nСтатус: {status}\nСоздан: {created}",
        "status_processing": "В обработке",
        "status_completed": "Выполнен",
        "status_cancelled": "Отменён",
        "status_changed": "Статус заказа #{order_id} изменён на: {status}",
        "notify_status": "Статус вашего заказа #{order_id} изменён на: {status}",
    },
    "en": {
        "welcome": "Welcome!\n\nI help you manage your business.\nUse the menu below:",
        "lang_selected": "Language changed to English",
        "new_order": "New Order",
        "my_orders": "My Orders",
        "contact": "Contact",
        "back_to_menu": "Back to Menu",
        "back_to_admin": "Back to Admin",
        "select_product": "Select a product:",
        "describe_order": "Describe your order:",
        "quantity": "Quantity:",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "order_summary": "<b>Order:</b>\nProduct: {product}\nDescription: {desc}\nQuantity: {qty}\n\nConfirm?",
        "order_confirmed": "Order #{order_id} confirmed!\n\n{success}",
        "order_cancelled": "Order cancelled.",
        "no_orders": "No orders yet.",
        "your_orders": "<b>Your orders:</b>\n\n",
        "contact_info": "Contact: {info}",
        "admin_panel": "<b>Admin Panel:</b>",
        "statistics": "Statistics",
        "all_orders": "All Orders",
        "pending_orders": "Pending Orders",
        "settings": "Settings",
        "access_denied": "Access denied",
        "no_pending": "No pending orders.",
        "no_orders_list": "No orders.",
        "pending_list": "<b>Pending orders:</b>\n\nClick an order for actions.",
        "all_orders_list": "<b>All orders:</b>\n\nClick an order for actions.",
        "settings_text": "<b>Bot Settings:</b>\n\nWelcome message and more.",
        "stats_text": "<b>Statistics:</b>\n\nUsers: {users}\nOrders: {orders}\nPending: {pending}\nCompleted: {completed}",
        "lang_button": "Language",
        "select_language": "Select language:",
        "order_detail": "<b>Order #{order_id}</b>\n\nClient: @{username}\nProduct: {product}\nDescription: {desc}\nQuantity: {qty}\nStatus: {status}\nCreated: {created}",
        "status_processing": "Processing",
        "status_completed": "Completed",
        "status_cancelled": "Cancelled",
        "status_changed": "Order #{order_id} status changed to: {status}",
        "notify_status": "Your order #{order_id} status changed to: {status}",
    }
}

PRODUCTS_RU = ["Товар 1", "Товар 2", "Товар 3", "Услуга 1", "Услуга 2"]
PRODUCTS_EN = ["Product 1", "Product 2", "Product 3", "Service 1", "Service 2"]
STATUS_MAP_RU = {"pending": "Ожидает", "processing": "В обработке", "completed": "Выполнен", "cancelled": "Отменён"}
STATUS_MAP_EN = {"pending": "Pending", "processing": "Processing", "completed": "Completed", "cancelled": "Cancelled"}


class BotAPI:
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

    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        params = {"callback_query_id": callback_query_id, "show_alert": show_alert}
        if text:
            params["text"] = text
        return self._post("answerCallbackQuery", params)


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_lang(user_id, user_langs):
    return user_langs.get(user_id, "ru")


def get_products(lang):
    return PRODUCTS_RU if lang == "ru" else PRODUCTS_EN


def get_status_map(lang):
    return STATUS_MAP_RU if lang == "ru" else STATUS_MAP_EN


def status_name(status, lang):
    return get_status_map(lang).get(status, status)


def msg(lang, key, **kwargs):
    text = MESSAGES[lang].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def lang_select_kb():
    return {
        "inline_keyboard": [
            [
                {"text": "Русский", "callback_data": "lang_ru"},
                {"text": "English", "callback_data": "lang_en"},
            ]
        ]
    }


def main_menu_kb(lang):
    return {
        "inline_keyboard": [
            [{"text": msg(lang, "new_order"), "callback_data": "new_order"}],
            [{"text": msg(lang, "my_orders"), "callback_data": "my_orders"}],
            [{"text": msg(lang, "contact"), "callback_data": "contact"}],
            [{"text": msg(lang, "lang_button"), "callback_data": "change_lang"}],
        ]
    }


def confirm_kb(lang):
    return {
        "inline_keyboard": [
            [
                {"text": msg(lang, "confirm"), "callback_data": "confirm_yes"},
                {"text": msg(lang, "cancel"), "callback_data": "confirm_no"},
            ]
        ]
    }


def back_kb(lang):
    return {
        "inline_keyboard": [
            [{"text": msg(lang, "back_to_menu"), "callback_data": "back_to_menu"}],
        ]
    }


def order_action_kb(order_id, lang):
    return {
        "inline_keyboard": [
            [
                {"text": msg(lang, "status_processing"), "callback_data": f"setstatus_{order_id}_processing"},
                {"text": msg(lang, "status_completed"), "callback_data": f"setstatus_{order_id}_completed"},
            ],
            [
                {"text": msg(lang, "status_cancelled"), "callback_data": f"setstatus_{order_id}_cancelled"},
            ],
            [
                {"text": msg(lang, "back_to_admin"), "callback_data": "back_to_admin"},
            ],
        ]
    }


def owner_menu_kb(lang):
    return {
        "inline_keyboard": [
            [{"text": msg(lang, "statistics"), "callback_data": "stats"}],
            [{"text": msg(lang, "pending_orders"), "callback_data": "pending_orders"}],
            [{"text": msg(lang, "all_orders"), "callback_data": "all_orders"}],
            [{"text": msg(lang, "settings"), "callback_data": "settings"}],
            [{"text": msg(lang, "back_to_menu"), "callback_data": "back_to_menu"}],
        ]
    }


user_states = {}
user_langs = {}


def handle_message(bot, api, config, db, message):
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not user_id or not chat_id:
        return

    db.add_user_sync(user_id, message["from"].get("username"), message["from"].get("full_name"))

    state = user_states.get(user_id)
    lang = get_lang(user_id, user_langs)

    if state and state.get("step") == "waiting_description":
        user_states[user_id] = {"step": "waiting_quantity", "product": state["product"], "description": text}
        kb = {"inline_keyboard": [[{"text": str(i), "callback_data": f"qty_{i}"} for i in range(1, 6)]]}
        api.send_message(chat_id, msg(lang, "quantity"), reply_markup=kb)
        return

    if text == "/start":
        api.send_message(chat_id, msg(lang, "welcome"), reply_markup=main_menu_kb(lang))

    elif text == "/admin" and user_id == config.get("owner_id"):
        api.send_message(chat_id, msg(lang, "admin_panel"), reply_markup=owner_menu_kb(lang))


def handle_callback(bot, api, config, db, cb):
    user_id = cb.get("from", {}).get("id")
    chat_id = cb.get("message", {}).get("chat", {}).get("id")
    message_id = cb.get("message", {}).get("message_id")
    data = cb.get("data", "")

    if not user_id or not chat_id:
        return

    api.answer_callback_query(cb["id"])

    lang = get_lang(user_id, user_langs)
    products = get_products(lang)

    if data == "lang_ru":
        user_langs[user_id] = "ru"
        api.edit_message_text(chat_id, message_id, msg("ru", "lang_selected"), reply_markup=main_menu_kb("ru"))
        return

    elif data == "lang_en":
        user_langs[user_id] = "en"
        api.edit_message_text(chat_id, message_id, msg("en", "lang_selected"), reply_markup=main_menu_kb("en"))
        return

    elif data == "change_lang":
        api.edit_message_text(chat_id, message_id, msg(lang, "select_language"), reply_markup=lang_select_kb())
        return

    if data == "back_to_menu":
        user_states.pop(user_id, None)
        api.edit_message_text(chat_id, message_id, msg(lang, "welcome"), reply_markup=main_menu_kb(lang))

    elif data == "back_to_admin":
        if user_id == config.get("owner_id"):
            api.edit_message_text(chat_id, message_id, msg(lang, "admin_panel"), reply_markup=owner_menu_kb(lang))
        else:
            api.edit_message_text(chat_id, message_id, msg(lang, "welcome"), reply_markup=main_menu_kb(lang))
        return

    elif data == "new_order":
        kb = {"inline_keyboard": [[{"text": p, "callback_data": f"product_{i}"}] for i, p in enumerate(products)]}
        api.edit_message_text(chat_id, message_id, msg(lang, "select_product"), reply_markup=kb)

    elif data.startswith("product_"):
        index = int(data.split("_")[1])
        product = products[index]
        user_states[user_id] = {"step": "waiting_description", "product": product}
        api.edit_message_text(chat_id, message_id, f"{product}\n\n{msg(lang, 'describe_order')}")

    elif data.startswith("qty_"):
        quantity = int(data.split("_")[1])
        state = user_states.get(user_id, {})
        product = state.get("product", "?")
        description = state.get("description", "")
        user_states[user_id] = {"step": "confirm", "product": product, "description": description, "quantity": quantity}
        text_msg = msg(lang, "order_summary", product=product, desc=description, qty=quantity)
        api.edit_message_text(chat_id, message_id, text_msg, reply_markup=confirm_kb(lang))

    elif data == "confirm_yes":
        state = user_states.pop(user_id, {})
        product = state.get("product", "?")
        description = state.get("description", "")
        quantity = state.get("quantity", 1)
        order_id = db.add_order_sync(user_id, product, description, quantity)

        owner_id = config.get("owner_id")
        if owner_id:
            username = cb.get("from", {}).get("username", "")
            owner_text = f"<b>New order #{order_id}</b>\n\nClient: @{username}\nProduct: {product}\nDescription: {description}\nQty: {quantity}"
            api.send_message(owner_id, owner_text)

        success_msg = config.get("order_success_message", "Thank you!")
        api.edit_message_text(chat_id, message_id, msg(lang, "order_confirmed", order_id=order_id, success=success_msg), reply_markup=main_menu_kb(lang))

    elif data == "confirm_no":
        user_states.pop(user_id, None)
        api.edit_message_text(chat_id, message_id, msg(lang, "order_cancelled"), reply_markup=main_menu_kb(lang))

    elif data == "my_orders":
        orders = db.get_user_orders_sync(user_id)
        if not orders:
            api.edit_message_text(chat_id, message_id, msg(lang, "no_orders"), reply_markup=back_kb(lang))
        else:
            status_map = get_status_map(lang)
            text_msg = msg(lang, "your_orders")
            for o in orders[:10]:
                oid, uid, prod, desc, qty, status, created = o
                text_msg += f"#{oid} | {prod} | {status_map.get(status, status)}\n"
            api.edit_message_text(chat_id, message_id, text_msg, reply_markup=back_kb(lang))

    elif data == "contact":
        info = config.get("contact_info", "@support")
        api.edit_message_text(chat_id, message_id, msg(lang, "contact_info", info=info), reply_markup=back_kb(lang))

    elif data == "stats":
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], msg(lang, "access_denied"), show_alert=True)
            return
        stats = db.get_stats_sync()
        text_msg = msg(lang, "stats_text", users=stats['total_users'], orders=stats['total_orders'], pending=stats['pending_orders'], completed=stats['completed_orders'])
        api.edit_message_text(chat_id, message_id, text_msg, reply_markup=owner_menu_kb(lang))

    elif data == "pending_orders":
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], msg(lang, "access_denied"), show_alert=True)
            return
        orders = db.get_all_orders_sync("pending")
        if not orders:
            api.edit_message_text(chat_id, message_id, msg(lang, "no_pending"), reply_markup=owner_menu_kb(lang))
        else:
            kb_buttons = []
            for o in orders[:10]:
                oid, uid, prod, desc, qty, status, created = o
                user = db.get_user_sync(uid)
                uname = user[1] if user and user[1] else f"ID:{uid}"
                kb_buttons.append([{"text": f"#{oid} | {prod} | @{uname}", "callback_data": f"vieworder_{oid}"}])
            kb_buttons.append([{"text": msg(lang, "back_to_admin"), "callback_data": "back_to_admin"}])
            api.edit_message_text(chat_id, message_id, msg(lang, "pending_list"), reply_markup={"inline_keyboard": kb_buttons})

    elif data == "all_orders":
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], msg(lang, "access_denied"), show_alert=True)
            return
        orders = db.get_all_orders_sync()
        if not orders:
            api.edit_message_text(chat_id, message_id, msg(lang, "no_orders_list"), reply_markup=owner_menu_kb(lang))
        else:
            status_map = get_status_map(lang)
            kb_buttons = []
            for o in orders[:10]:
                oid, uid, prod, desc, qty, status, created = o
                user = db.get_user_sync(uid)
                uname = user[1] if user and user[1] else f"ID:{uid}"
                kb_buttons.append([{"text": f"#{oid} | {prod} | {status_map.get(status, status)} | @{uname}", "callback_data": f"vieworder_{oid}"}])
            kb_buttons.append([{"text": msg(lang, "back_to_admin"), "callback_data": "back_to_admin"}])
            api.edit_message_text(chat_id, message_id, msg(lang, "all_orders_list"), reply_markup={"inline_keyboard": kb_buttons})

    elif data.startswith("vieworder_"):
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], msg(lang, "access_denied"), show_alert=True)
            return
        order_id = int(data.split("_")[1])
        order = db.get_order_sync(order_id)
        if not order:
            api.answer_callback_query(cb["id"], "Order not found", show_alert=True)
            return
        oid, uid, prod, desc, qty, status, created = order
        user = db.get_user_sync(uid)
        uname = user[1] if user and user[1] else f"ID:{uid}"
        text_msg = msg(lang, "order_detail", order_id=oid, username=uname, product=prod, desc=desc, qty=qty, status=status_name(status, lang), created=created)
        api.edit_message_text(chat_id, message_id, text_msg, reply_markup=order_action_kb(order_id, lang))

    elif data.startswith("setstatus_"):
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], msg(lang, "access_denied"), show_alert=True)
            return
        parts = data.split("_")
        order_id = int(parts[1])
        new_status = parts[2]
        order = db.get_order_sync(order_id)
        if not order:
            api.answer_callback_query(cb["id"], "Order not found", show_alert=True)
            return
        db.update_order_status_sync(order_id, new_status)
        api.answer_callback_query(cb["id"], msg(lang, "status_changed", order_id=order_id, status=status_name(new_status, lang)), show_alert=True)
        client_id = order[1]
        try:
            api.send_message(client_id, msg(lang, "notify_status", order_id=order_id, status=status_name(new_status, lang)))
        except Exception:
            pass
        order = db.get_order_sync(order_id)
        oid, uid, prod, desc, qty, status, created = order
        user = db.get_user_sync(uid)
        uname = user[1] if user and user[1] else f"ID:{uid}"
        text_msg = msg(lang, "order_detail", order_id=oid, username=uname, product=prod, desc=desc, qty=qty, status=status_name(status, lang), created=created)
        api.edit_message_text(chat_id, message_id, text_msg, reply_markup=order_action_kb(order_id, lang))

    elif data == "settings":
        if user_id != config.get("owner_id"):
            api.answer_callback_query(cb["id"], msg(lang, "access_denied"), show_alert=True)
            return
        api.edit_message_text(chat_id, message_id, msg(lang, "settings_text"), reply_markup=back_kb(lang))


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
