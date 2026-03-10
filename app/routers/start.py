from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards import main_menu_keyboard
from app.texts import HELP_TEXT, START_TEXT

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(START_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
@router.message(F.text == "Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(F.text == "Цены")
async def show_prices(message: Message) -> None:
    await message.answer("Прайс: ...", reply_markup=main_menu_keyboard())


@router.message(F.text == "Адрес")
async def show_address(message: Message) -> None:
    await message.answer("Адрес: улица Пушкина, дом Колотушкина", reply_markup=main_menu_keyboard())
