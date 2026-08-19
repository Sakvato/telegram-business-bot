from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline import main_menu_keyboard, owner_menu_keyboard

router = Router()


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    config = callback.bot.get("config")

    if callback.from_user.id != config.get("owner_id"):
        await callback.answer("Access denied", show_alert=True)
        return

    db = callback.bot.get("db")
    stats = await db.get_stats()

    text = (
        f"<b>Statistics:</b>\n\n"
        f"Users: {stats['total_users']}\n"
        f"Total orders: {stats['total_orders']}\n"
        f"Pending: {stats['pending_orders']}\n"
        f"Completed: {stats['completed_orders']}"
    )

    await callback.message.edit_text(text, reply_markup=owner_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "pending_orders")
async def pending_orders(callback: CallbackQuery):
    config = callback.bot.get("config")

    if callback.from_user.id != config.get("owner_id"):
        await callback.answer("Access denied", show_alert=True)
        return

    db = callback.bot.get("db")
    orders = await db.get_all_orders(status="pending")

    if not orders:
        await callback.message.edit_text(
            "No pending orders.", reply_markup=owner_menu_keyboard()
        )
        await callback.answer()
        return

    text = "<b>Pending orders:</b>\n\n"
    for order in orders[:10]:
        order_id, user_id, product, desc, qty, status, created = order
        text += f"#{order_id} | {product} | @{user_id}\n"

    await callback.message.edit_text(text, reply_markup=owner_menu_keyboard())
    await callback.answer()
