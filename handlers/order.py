from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.inline import main_menu_keyboard, confirm_keyboard

router = Router()


class OrderForm(StatesGroup):
    product = State()
    description = State()
    quantity = State()
    confirm = State()


PRODUCTS = [
    "Product 1",
    "Product 2",
    "Product 3",
    "Service 1",
    "Service 2",
]


@router.callback_query(F.data == "new_order")
async def new_order(callback: CallbackQuery, state: FSMContext):
    text = "Select a product or service:"
    keyboard = []
    for i, product in enumerate(PRODUCTS):
        keyboard.append([{"text": product, "callback_data": f"product_{i}"}])

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for i, product in enumerate(PRODUCTS):
        builder.button(text=product, callback_data=f"product_{i}")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await state.set_state(OrderForm.product)
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    product = PRODUCTS[index]
    await state.update_data(product=product)

    await callback.message.edit_text(
        f"Product: {product}\n\nDescribe your order:"
    )
    await state.set_state(OrderForm.description)
    await callback.answer()


@router.message(OrderForm.description)
async def enter_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text=str(i), callback_data=f"qty_{i}")
    builder.adjust(5)

    await message.answer("Quantity:", reply_markup=builder.as_markup())
    await state.set_state(OrderForm.quantity)


@router.callback_query(F.data.startswith("qty_"))
async def select_quantity(callback: CallbackQuery, state: FSMContext):
    quantity = int(callback.data.split("_")[1])
    data = await state.get_data()

    text = (
        f"<b>Order Summary:</b>\n\n"
        f"Product: {data['product']}\n"
        f"Description: {data['description']}\n"
        f"Quantity: {quantity}\n\n"
        f"Confirm order?"
    )

    await callback.message.edit_text(text, reply_markup=confirm_keyboard())
    await state.update_data(quantity=quantity)
    await state.set_state(OrderForm.confirm)
    await callback.answer()


@router.callback_query(F.data == "confirm_yes", OrderForm.confirm)
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    db = callback.bot.get("db")
    config = callback.bot.get("config")
    data = await state.get_data()

    order_id = await db.add_order(
        user_id=callback.from_user.id,
        product=data["product"],
        description=data["description"],
        quantity=data["quantity"]
    )

    owner_id = config.get("owner_id")
    if owner_id:
        owner_text = (
            f"<b>New order #{order_id}</b>\n\n"
            f"Client: @{callback.from_user.username or callback.from_user.full_name}\n"
            f"Product: {data['product']}\n"
            f"Description: {data['description']}\n"
            f"Quantity: {data['quantity']}"
        )
        await callback.bot.send_message(owner_id, owner_text)

    success_msg = config.get("order_success_message", "Order confirmed!")
    await callback.message.edit_text(
        f"{success_msg}\n\nOrder #{order_id}"
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "confirm_no", OrderForm.confirm)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Order cancelled.", reply_markup=main_menu_keyboard()
    )
    await callback.answer()
