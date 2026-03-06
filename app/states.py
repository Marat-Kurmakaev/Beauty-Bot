from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    full_name = State()
    phone = State()
    service = State()
    preferred_time = State()
    comment = State()
