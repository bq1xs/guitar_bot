import os
from aiogram import types
from aiogram.types import FSInputFile
from bot_folder.keyboards import get_main_keyboard

def get_image(image_name):
    path = f"images/buttons/{image_name}"
    if os.path.exists(path):
        return FSInputFile(path)
    return None


async def cmd_start(message: types.Message):
    img = get_image("start.jpg")
    text = "привет бро, я тут чтобы ты не мучался с поиском аккордов!"

    if img:
        await message.answer_photo(photo=img, caption=text, reply_markup=get_main_keyboard())
    else:
        await message.answer(text, reply_markup=get_main_keyboard())


async def cmd_help(message: types.Message):
    img = get_image("help.jpg")
    text = (
        "просто напиши название песни и готово"
    )

    if img:
        await message.answer_photo(photo=img, caption=text)
    else:
        await message.answer(text)


async def cmd_chord(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("напиши так: /chord am")
        return
    chord = parts[1].lower()
    path = f"chords_images/fingers/{chord}.jpg"
    if os.path.exists(path):
        photo = FSInputFile(path)
        await message.answer_photo(photo, caption=f"аккорд {chord.upper()}")
    else:
        await message.answer(f"Нет картинки для {chord.upper()}")