from aiogram.dispatcher.filters.state import StatesGroup, State


class Admin(StatesGroup):
    make_newsletter = State()
    support_dialog = State()
