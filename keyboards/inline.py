from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="New Order", callback_data="new_order")
    builder.button(text="My Orders", callback_data="my_orders")
    builder.button(text="Contact", callback_data="contact")
    builder.adjust(1)
    return builder.as_markup()


def owner_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Statistics", callback_data="stats")
    builder.button(text="Pending Orders", callback_data="pending_orders")
    builder.button(text="All Orders", callback_data="all_orders")
    builder.button(text="Settings", callback_data="settings")
    builder.button(text="Back", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Edit Welcome", callback_data="edit_welcome")
    builder.button(text="Edit Success Message", callback_data="edit_success")
    builder.button(text="Edit Contact", callback_data="edit_contact")
    builder.button(text="Back", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def confirm_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Confirm", callback_data="confirm_yes")
    builder.button(text="Cancel", callback_data="confirm_no")
    builder.adjust(2)
    return builder.as_markup()
