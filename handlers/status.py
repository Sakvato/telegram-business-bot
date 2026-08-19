from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.inline import main_menu_keyboard

router = Router()

STATUS_MAP = {
    "pending": "Pending",
    "processing": "Processing",
    "completed": "Completed",
    "cancelled": "Cancelled",
}


@router.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    db = callback.bot.get("db")
    orders = await db.get_user_orders(callback.from_user.id)

    if not orders:
        await callback.message.edit_text(
            "You have no orders yet.",
            reply_markup=main_menu_keyboard()
        )
        await callback.answer()
        return

    text = "<b>Your orders:</b>\n\n"
    for order in orders[:10]:
        order_id, user_id, product, desc, qty, status, created = order
        status_text = STATUS_MAP.get(status, status)
        text += f"#{order_id} | {product} | {status_text}\n"

    await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("order_detail_"))
async def order_detail(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    db = callback.bot.get("db")
    order = await db.get_order(order_id)

    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    _, user_id, product, desc, qty, status, created = order
    status_text = STATUS_MAP.get(status, status)

    text = (
        f"<b>Order #{order_id}</b>\n\n"
        f"Product: {product}\n"
        f"Description: {desc}\n"
        f"Quantity: {qty}\n"
        f"Status: {status_text}\n"
        f"Date: {created}"
    )

    await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    await callback.answer()
