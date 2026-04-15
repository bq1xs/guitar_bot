import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from bot_folder.handlers import cmd_start, cmd_help, cmd_chord
from bot_folder.messages_handler import handle_messages
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_help, Command("help"))
dp.message.register(cmd_chord, Command("chord"))


dp.message.register(handle_messages)

async def main():
    print("бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())