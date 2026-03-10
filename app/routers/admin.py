from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app import db
from app.config import settings
from app.keyboards import admin_decision_keyboard
from app.texts import pending_request_text


def _status_label(status: str) -> str:
    labels = {
        "approved": "подтверждена",
        "rejected": "отклонена",
    }
    return labels.get(status, status)


router = Router()


DB_DISABLED_TEXT = (
    "База данных отключена. "
    "Админ-функции заявок недоступны."
)


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admins


@router.message(Command("pending"))
async def cmd_pending(message: Message) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только админу.")
        return

    if not settings.database_enabled:
        await message.answer(DB_DISABLED_TEXT)
        return

    rows = await db.get_pending_requests()
    if not rows:
        await message.answer("Новых заявок нет.")
        return

    for row in rows:
        await message.answer(
            pending_request_text(dict(row)),
            reply_markup=admin_decision_keyboard(int(row["id"])),
        )


@router.callback_query(F.data.startswith("request:"))
async def process_request_decision(callback: CallbackQuery) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет прав для этого действия.", show_alert=True)
        return

    if not settings.database_enabled:
        await callback.answer(DB_DISABLED_TEXT, show_alert=True)
        return

    raw_data = callback.data or ""
    parts = raw_data.split(":")
    if len(parts) != 3 or not parts[1].isdigit():
        await callback.answer("Некорректные данные кнопки.", show_alert=True)
        return

    request_id = int(parts[1])
    action = parts[2]
    status_map = {"approve": "approved", "reject": "rejected"}
    status = status_map.get(action)

    if status is None:
        await callback.answer("Неизвестное действие.", show_alert=True)
        return

    updated = await db.update_request_status(request_id, status)
    if not updated:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    row = await db.get_request(request_id)
    if row is not None:
        client_text = (
            f"Ваша заявка #{request_id} "
            f"{'подтверждена' if status == 'approved' else 'отклонена'}."
        )
        try:
            await callback.bot.send_message(int(row["user_id"]), client_text)
        except Exception:
            pass

    if callback.message is not None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"Заявка #{request_id} обновлена: <b>{_status_label(status)}</b>."
        )

    await callback.answer("Готово.")
