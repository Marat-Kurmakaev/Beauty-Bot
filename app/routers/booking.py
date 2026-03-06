from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app import db
from app.config import settings
from app.keyboards import admin_decision_keyboard, main_menu_keyboard, skip_comment_keyboard
from app.states import BookingStates
from app.texts import (
    ASK_COMMENT,
    ASK_FULL_NAME,
    ASK_PHONE,
    ASK_PREFERRED_TIME,
    ASK_SERVICE,
    admin_request_text,
    booking_created_text,
    booking_summary_text,
)

router = Router()


@router.message(Command("book"))
@router.message(F.text == "\u0417\u0430\u043f\u0438\u0441\u0430\u0442\u044c\u0441\u044f")
async def start_booking(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BookingStates.full_name)
    await message.answer(ASK_FULL_NAME)


@router.message(BookingStates.full_name)
async def booking_full_name(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(ASK_FULL_NAME)
        return
    await state.update_data(full_name=message.text.strip())
    await state.set_state(BookingStates.phone)
    await message.answer(ASK_PHONE)


@router.message(BookingStates.phone)
async def booking_phone(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(ASK_PHONE)
        return
    await state.update_data(phone=message.text.strip())
    await state.set_state(BookingStates.service)
    await message.answer(ASK_SERVICE)


@router.message(BookingStates.service)
async def booking_service(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(ASK_SERVICE)
        return
    await state.update_data(service=message.text.strip())
    await state.set_state(BookingStates.preferred_time)
    await message.answer(ASK_PREFERRED_TIME)


@router.message(BookingStates.preferred_time)
async def booking_preferred_time(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(ASK_PREFERRED_TIME)
        return
    await state.update_data(preferred_time=message.text.strip())
    await state.set_state(BookingStates.comment)
    await message.answer(ASK_COMMENT, reply_markup=skip_comment_keyboard())


@router.message(BookingStates.comment)
async def booking_comment(message: Message, state: FSMContext) -> None:
    comment_text = (message.text or "").strip()
    comment = "" if comment_text == "\u041f\u0440\u043e\u043f\u0443\u0441\u0442\u0438\u0442\u044c" else comment_text
    await state.update_data(comment=comment)
    data = await state.get_data()

    if message.from_user is None:
        await state.clear()
        await message.answer(
            "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442\u044c \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f.",
            reply_markup=main_menu_keyboard(),
        )
        return

    request_id = await db.insert_request(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=data["full_name"],
        phone=data["phone"],
        service=data["service"],
        preferred_time=data["preferred_time"],
        comment=data.get("comment") or None,
    )

    await message.answer(booking_summary_text(data))
    await message.answer(booking_created_text(request_id), reply_markup=main_menu_keyboard())
    await state.clear()

    admin_text = admin_request_text(
        request_id=request_id,
        data=data,
        user_id=message.from_user.id,
        username=message.from_user.username or "",
    )
    keyboard = admin_decision_keyboard(request_id)

    for admin_id in settings.admins:
        try:
            await message.bot.send_message(admin_id, admin_text, reply_markup=keyboard)
        except Exception:
            continue
