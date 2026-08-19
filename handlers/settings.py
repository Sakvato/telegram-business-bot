from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.inline import main_menu_keyboard, settings_keyboard

router = Router()


class SettingsForm(StatesGroup):
    welcome_message = State()
    order_success = State()
    contact_info = State()


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    config = callback.bot.get("config")

    if callback.from_user.id != config.get("owner_id"):
        await callback.answer("Access denied", show_alert=True)
        return

    await callback.message.edit_text(
        "<b>Bot Settings:</b>", reply_markup=settings_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "edit_welcome")
async def edit_welcome(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Enter new welcome message:")
    await state.set_state(SettingsForm.welcome_message)
    await callback.answer()


@router.message(SettingsForm.welcome_message)
async def save_welcome(message: Message, state: FSMContext, **kwargs):
    config = message.bot.get("config")
    config["welcome_message"] = message.text

    import json
    from pathlib import Path
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    await message.answer("Welcome message updated!", reply_markup=main_menu_keyboard())
    await state.clear()


@router.callback_query(F.data == "edit_success")
async def edit_success(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Enter new order success message:")
    await state.set_state(SettingsForm.order_success)
    await callback.answer()


@router.message(SettingsForm.order_success)
async def save_success(message: Message, state: FSMContext):
    config = message.bot.get("config")
    config["order_success_message"] = message.text

    import json
    from pathlib import Path
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    await message.answer("Success message updated!", reply_markup=main_menu_keyboard())
    await state.clear()
