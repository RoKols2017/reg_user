import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
import httpx

load_dotenv()  # этот вызов загрузит все переменные из .env в окружение

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DJANGO_API_URL = os.getenv('DJANGO_API_URL')

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Обработка команды /start c токеном
@dp.message(CommandStart(deep_link=True))
async def process_start_with_token(message: Message, command: CommandStart):
    token = command.args
    if not token:
        await message.answer("Пожалуйста, сканируйте QR-код на сайте для привязки.")
        return

    # Отправляем POST-запрос к Django REST API
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            DJANGO_API_URL,
            json={
                "token": token,
                "telegram_id": str(message.from_user.id),
                "telegram_username": message.from_user.username or "",
            },
            timeout=10
        )

    if resp.status_code == 200:
        await message.answer("✅ Ваш Telegram успешно привязан к аккаунту сайта!")
    elif resp.status_code == 400:
        await message.answer("❌ Ошибка: неверный или устаревший токен. Попробуйте сгенерировать новый QR на сайте.")
    else:
        await message.answer("🚫 Непредвиденная ошибка. Попробуйте позже.")

# На случай обычного /start
@dp.message(CommandStart())
async def process_start_no_token(message: Message):
    await message.answer("Привет! Для привязки аккаунта сканируйте QR-код на сайте.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
