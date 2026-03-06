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
@router.message(F.text == "\u041f\u043e\u043c\u043e\u0449\u044c")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(F.text == "\u0426\u0435\u043d\u044b")
async def show_prices(message: Message) -> None:
    await message.answer("\u041f\u0440\u0430\u0439\u0441: ...", reply_markup=main_menu_keyboard())


@router.message(F.text == "\u0410\u0434\u0440\u0435\u0441")
async def show_address(message: Message) -> None:
    await message.answer("\u0410\u0434\u0440\u0435\u0441: ...", reply_markup=main_menu_keyboard())
