from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.inline import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    db = message.bot.get("db")
    config = message.bot.get("config")

    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    welcome = config.get("welcome_message", "Welcome!")
    await message.answer(welcome, reply_markup=main_menu_keyboard())
