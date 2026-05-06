import os
import asyncio
import random
from aiogram.types import FSInputFile, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot_folder.keyboards import get_main_keyboard
from bot_folder.amdm_parser import AmDm

favorites = {}

amdm = AmDm()

RANDOM_SONGS = [
    "Кино пачка сигарет",
    "Кино группа крови",
    "Кино звезда по имени солнце",
    "Сплин выхода нет",
    "Сплин орбит без сахара",
    "Любэ комбат",
    "Любэ там за туманами",
    "ДДТ что такое осень",
    "ДДТ это все",
    "Монеточка нимфоманка",
    "Lizer пачка сигарет",
    "Король и шут лесник",
    "Король и шут кукла колдуна",
    "Ария беспечный ангел",
    "Би-2 полковнику никто не пишет",
    "Земфира искала",
    "Мумий Тролль утекай",
    "Ночные снайперы 31 весна",
    "Сектор Газа лирика",
    "Агата Кристи как на войне",
]

def get_image(image_name):
    path = f"images/buttons/{image_name}"
    if os.path.exists(path):
        return FSInputFile(path)
    return None

def get_song_gif():
    path = "gifs/guitar.gif"
    if os.path.exists(path):
        return FSInputFile(path)
    return None


async def handle_messages(message):
    text = message.text.lower().strip()

    if text == "как ставить аккорды?":
        img = get_image("chord.jpg")
        answer_text = (
            "смотри и вникай бро:\n\n"
            "напиши /chord и название аккорда\n"
            "например: /chord am - я покажу как зажимать!\n\n"
        )
        if img:
            await message.answer_photo(photo=img, caption=answer_text, reply_markup=get_main_keyboard())
        else:
            await message.answer(answer_text, reply_markup=get_main_keyboard())

    elif text == "о боте":
        about_text = "бот был создан данным лицом в качестве продукта для индивидуального проекта лайк если я крутая"
        photo_path1 = "photo/bot_photo.jpg"
        photo_path2 = "photo/bot_photo2.jpg"
        media_group = []
        if os.path.exists(photo_path1):
            media_group.append(InputMediaPhoto(media=FSInputFile(photo_path1), caption=about_text))
        if os.path.exists(photo_path2):
            media_group.append(InputMediaPhoto(media=FSInputFile(photo_path2)))
        if len(media_group) > 0:
            await message.answer_media_group(media=media_group)
        else:
            await message.answer(about_text)

    elif text == "сос":
        img = get_image("sos.jpg")
        answer_text = (
            "тут все легко \n\n"
            "пиши название песни-я тащу текст\n"
            "/chord am - показывает как зажимать аккорд\n"
            "/help - то же самое что эта кнопка\n\n"
            "Чем могу еще помочь?"
        )
        if img:
            await message.answer_photo(photo=img, caption=answer_text, reply_markup=get_main_keyboard())
        else:
            await message.answer(answer_text, reply_markup=get_main_keyboard())

    elif text == "избранное":
        user_id = message.from_user.id

        if user_id not in favorites or not favorites[user_id]:
            await message.answer(
                "У тебя пока нет избранных песен, бро!\n\n"
                "Когда найдёшь песню — нажми ❤️ В избранное",
                reply_markup=get_main_keyboard()
            )
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for song in favorites[user_id]:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"🎸 {song['artist']} - {song['title']}",
                    callback_data=f"fav_{song['artist']}_{song['title']}"
                )
            ])

        await message.answer("📋 **Твои любимые песни:**\n\nНажми на любую — я найду аккорды!",
                             reply_markup=keyboard,
                             parse_mode="Markdown")

    elif text == "случайная песня":
        dice_message = await message.answer_dice(emoji="🎲")
        await asyncio.sleep(2)
        random_song = random.choice(RANDOM_SONGS)
        await message.answer(f"Выпало: {dice_message.dice.value}\n\n случайная песня: {random_song}\n\n ищу аккорды...")

        try:
            results = await asyncio.to_thread(amdm.get_chords_list, random_song)
            if not results or len(results) == 0:
                await message.answer(f"я не нашел '{random_song}', попробуй другую!", reply_markup=get_main_keyboard())
                return
            song = results[0]
            artist = song['artist']
            title = song['title']
            song_url = song['url']
            chords = await asyncio.to_thread(amdm.get_chords_song, song_url)
            chords = chords.replace('<br/>', '\n').replace('<br>', '\n').replace('&nbsp;', ' ')
            response = f"""🎸 {artist} - {title} 🎸
━━━━━━━━━━━━━━━━━━━━━

{chords}

━━━━━━━━━━━━━━━━━━━━━
🎵 Совет: бой шестёрка ↓↓*↓ ↓↑
💡 Аккорды: /chord am - как зажимать

играй с кайфом!
"""
            if len(response) > 4000:
                response = response[:3950] + "\n\n... аккорды обрезаны"

            fav_button = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❤️", callback_data=f"save_{artist}_{title}")]
            ])

            song_gif = get_song_gif()
            if song_gif:
                short_caption = f"🎸 {artist} - {title} 🎸"
                await message.answer_animation(animation=song_gif, caption=short_caption)
                await message.answer(response, reply_markup=fav_button)
            else:
                await message.answer(response, reply_markup=fav_button)
        except Exception as e:
            await message.answer(f"Ошибка: {str(e)[:100]}", reply_markup=get_main_keyboard())

    elif text == "хелпер":
        img = get_image("helper.jpg")
        answer_text = (
            "это гитарный словарь для чайников\n\n"
            "бой - ритм который ты бьешь по струнам ладонью или медиатором\n"
            "перебор - когда щипаешь струны по одной,а не бьешь по всем\n"
            "баррэ - одним пальцем зажимаешь весь лад\n"
            "тональность - настроение песни\n"
            "каподастр - прищепка на гриф, которая меняет тональность\n\n"
            "понял че к чему?"
        )
        if img:
            await message.answer_photo(photo=img, caption=answer_text, reply_markup=get_main_keyboard())
        else:
            await message.answer(answer_text, reply_markup=get_main_keyboard())

    else:
        await message.answer(f"ищу '{text}' на AmDm ... подожди пару сек!")

        try:
            results = await asyncio.to_thread(amdm.get_chords_list, text)
            if not results or len(results) == 0:
                await message.answer(
                    f"я не нашел '{text}' на AmDm, сорянчик\n\n"
                    "попробуй:\n"
                    "• написать исполнителя и название полностью (Кино пачка сигарет)\n"
                    "• проверить название\n"
                    "• написать короче (Пачка сигарет)",
                    reply_markup=get_main_keyboard()
                )
                return
            song = results[0]
            artist = song['artist']
            title = song['title']
            song_url = song['url']
            chords = await asyncio.to_thread(amdm.get_chords_song, song_url)
            chords = chords.replace('<br/>', '\n').replace('<br>', '\n').replace('&nbsp;', ' ')
            response = f"""🎸 {artist} - {title} 🎸
━━━━━━━━━━━━━━━━━━━━━

{chords}

━━━━━━━━━━━━━━━━━━━━━
🎵 Совет: бой шестёрка ↓↓*↓ ↓↑
💡 Аккорды: /chord am - как зажимать

играй с кайфом!
"""
            if len(response) > 4000:
                response = response[:3950] + "\n\n... аккорды обрезаны"

            fav_button = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❤️", callback_data=f"save_{artist}_{title}")]
            ])

            song_gif = get_song_gif()
            if song_gif:
                short_caption = f"🎸 {artist} - {title} 🎸"
                await message.answer_animation(animation=song_gif, caption=short_caption)
                await message.answer(response, reply_markup=fav_button)
            else:
                await message.answer(response, reply_markup=fav_button)
        except Exception as e:
            await message.answer(
                f"ошибка: {str(e)[:100]}\n\n"
                "Возможно сайт AmDm временно недоступен. Попробуй чутка позже",
                reply_markup=get_main_keyboard()
            )


async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    if data.startswith("save_"):
        _, artist, title = data.split("_", 2)

        if user_id not in favorites:
            favorites[user_id] = []

        for song in favorites[user_id]:
            if song['artist'] == artist and song['title'] == title:
                await callback.answer("уже есть в избранном!", show_alert=True)
                return

        favorites[user_id].append({'artist': artist, 'title': title})
        await callback.answer("Добавлено в избранное!", show_alert=True)

    elif data.startswith("fav_"):
        _, artist, title = data.split("_", 2)
        await callback.message.answer(f"🔍 Ищу: {artist} - {title}")

        try:
            results = await asyncio.to_thread(amdm.get_chords_list, f"{artist} {title}")
            if not results:
                await callback.message.answer(f"не нашел {artist} - {title}", reply_markup=get_main_keyboard())
                return

            song = results[0]
            chords = await asyncio.to_thread(amdm.get_chords_song, song['url'])
            chords = chords.replace('<br/>', '\n').replace('<br>', '\n').replace('&nbsp;', ' ')
            response = f"""🎸 {song['artist']} - {song['title']} 🎸
━━━━━━━━━━━━━━━━━━━━━

{chords}

━━━━━━━━━━━━━━━━━━━━━
🎵 Совет: бой шестёрка ↓↓*↓ ↓↑
💡 Аккорды: /chord am - как зажимать

играй с кайфом!
"""
            if len(response) > 4000:
                response = response[:3950] + "\n\n... аккорды обрезаны"

            fav_button = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="В избранное", callback_data=f"save_{song['artist']}_{song['title']}")]
            ])

            song_gif = get_song_gif()
            if song_gif:
                short_caption = f"🎸 {song['artist']} - {song['title']} 🎸"
                await callback.message.answer_animation(animation=song_gif, caption=short_caption)
                await callback.message.answer(response, reply_markup=fav_button)
            else:
                await callback.message.answer(response, reply_markup=fav_button)

        except Exception as e:
            await callback.message.answer(f"Ошибка: {str(e)[:100]}", reply_markup=get_main_keyboard())

        await callback.answer()