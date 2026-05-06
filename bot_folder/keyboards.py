from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Случайная песня")],
            [KeyboardButton(text="Избранное")],
            [KeyboardButton(text="Сос")],
            [KeyboardButton(text="Хелпер")],
            [KeyboardButton(text="Как ставить аккорды?")],
            [KeyboardButton(text="О боте")]

        ],
        resize_keyboard=True
    )
    return keyboard