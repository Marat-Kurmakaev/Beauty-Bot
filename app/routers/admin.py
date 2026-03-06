from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app import db
from app.config import settings
from app.keyboards import admin_decision_keyboard
from app.texts import pending_request_text


def _status_label(status: str) -> str:
    labels = {
        "approved": "\u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430",
        "rejected": "\u043e\u0442\u043a\u043b\u043e\u043d\u0435\u043d\u0430",
    }
    return labels.get(status, status)

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admins


@router.message(Command("pending"))
async def cmd_pending(message: Message) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("\u041a\u043e\u043c\u0430\u043d\u0434\u0430 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u0430 \u0442\u043e\u043b\u044c\u043a\u043e \u0430\u0434\u043c\u0438\u043d\u0443.")
        return

    rows = await db.get_pending_requests()
    if not rows:
        await message.answer("\u041d\u043e\u0432\u044b\u0445 \u0437\u0430\u044f\u0432\u043e\u043a \u043d\u0435\u0442.")
        return

    for row in rows:
        await message.answer(
            pending_request_text(dict(row)),
            reply_markup=admin_decision_keyboard(int(row["id"])),
        )


@router.callback_query(F.data.startswith("request:"))
async def process_request_decision(callback: CallbackQuery) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("\u041d\u0435\u0442 \u043f\u0440\u0430\u0432 \u0434\u043b\u044f \u044d\u0442\u043e\u0433\u043e \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f.", show_alert=True)
        return

    raw_data = callback.data or ""
    parts = raw_data.split(":")
    if len(parts) != 3 or not parts[1].isdigit():
        await callback.answer("\u041d\u0435\u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435 \u043a\u043d\u043e\u043f\u043a\u0438.", show_alert=True)
        return

    request_id = int(parts[1])
    action = parts[2]
    status_map = {"approve": "approved", "reject": "rejected"}
    status = status_map.get(action)

    if status is None:
        await callback.answer("\u041d\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043d\u043e\u0435 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435.", show_alert=True)
        return

    updated = await db.update_request_status(request_id, status)
    if not updated:
        await callback.answer("\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430.", show_alert=True)
        return

    row = await db.get_request(request_id)
    if row is not None:
        client_text = (
            f"\u0412\u0430\u0448\u0430 \u0437\u0430\u044f\u0432\u043a\u0430 #{request_id} "
            f"{'\u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430' if status == 'approved' else '\u043e\u0442\u043a\u043b\u043e\u043d\u0435\u043d\u0430'}."
        )
        try:
            await callback.bot.send_message(int(row["user_id"]), client_text)
        except Exception:
            pass

    if callback.message is not None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"\u0417\u0430\u044f\u0432\u043a\u0430 #{request_id} \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0430: <b>{_status_label(status)}</b>."
        )

    await callback.answer("\u0413\u043e\u0442\u043e\u0432\u043e.")
