def _status_label(status: str) -> str:
    labels = {
        "new": "новая",
        "approved": "подтверждена",
        "rejected": "отклонена",
    }
    return labels.get(status, status)


START_TEXT = (
    "Привет. Я бот маникюрного салона.\n"
    "Здесь можно быстро оставить заявку на запись."
)

HELP_TEXT = (
    "Команды:\n"
    "/start - главное меню\n"
    "/help - помощь\n"
    "/book - оставить заявку\n"
    "/pending - новые заявки (для админа)"
)

ASK_FULL_NAME = "Введите ваше имя:"
ASK_PHONE = "Введите номер телефона:"
ASK_SERVICE = "Какую услугу вы хотите?"
ASK_PREFERRED_TIME = "Укажите удобную дату и время:"
ASK_COMMENT = (
    "Добавите комментарий к заявке. "
    "Если он не нужен, нажмите 'Пропустить'."
)


def booking_created_text(request_id: int) -> str:
    return (
        f"Заявка создана. "
        f"Номер: <b>#{request_id}</b>. "
        "Администратор свяжется с вами."
    )


def booking_summary_text(data: dict[str, str]) -> str:
    comment = data.get("comment") or "-"
    return (
        "Проверьте заявку:\n"
        f"Имя: <b>{data['full_name']}</b>\n"
        f"Телефон: <b>{data['phone']}</b>\n"
        f"Услуга: <b>{data['service']}</b>\n"
        f"Удобное время: <b>{data['preferred_time']}</b>\n"
        f"Комментарий: <b>{comment}</b>"
    )


def admin_request_text(request_id: int, data: dict[str, str], user_id: int, username: str) -> str:
    username_value = f"@{username}" if username else "-"
    comment = data.get("comment") or "-"
    return (
        f"Новая заявка <b>#{request_id}</b>\n"
        f"Клиент: <b>{data['full_name']}</b>\n"
        f"Телефон: <b>{data['phone']}</b>\n"
        f"Услуга: <b>{data['service']}</b>\n"
        f"Время: <b>{data['preferred_time']}</b>\n"
        f"Комментарий: <b>{comment}</b>\n"
        f"ID пользователя: <code>{user_id}</code>\n"
        f"Имя пользователя: {username_value}"
    )


def pending_request_text(row: dict) -> str:
    comment = row.get("comment") or "-"
    username = row.get("username") or "-"
    return (
        f"Заявка <b>#{row['id']}</b> ({_status_label(row['status'])})\n"
        f"Имя: <b>{row['full_name']}</b>\n"
        f"Телефон: <b>{row['phone']}</b>\n"
        f"Услуга: <b>{row['service']}</b>\n"
        f"Время: <b>{row['preferred_time']}</b>\n"
        f"Комментарий: <b>{comment}</b>\n"
        f"ID пользователя: <code>{row['user_id']}</code>\n"
        f"Имя пользователя: {username}"
    )
