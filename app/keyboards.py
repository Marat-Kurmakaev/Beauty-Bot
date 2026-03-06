from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="\u0417\u0430\u043f\u0438\u0441\u0430\u0442\u044c\u0441\u044f")],
            [KeyboardButton(text="\u0426\u0435\u043d\u044b")],
            [KeyboardButton(text="\u0410\u0434\u0440\u0435\u0441")],
        ],
        resize_keyboard=True,
    )


def skip_comment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="\u041f\u0440\u043e\u043f\u0443\u0441\u0442\u0438\u0442\u044c")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def admin_decision_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c",
                    callback_data=f"request:{request_id}:approve",
                ),
                InlineKeyboardButton(
                    text="\u041e\u0442\u043a\u043b\u043e\u043d\u0438\u0442\u044c",
                    callback_data=f"request:{request_id}:reject",
                ),
            ]
        ]
    )
