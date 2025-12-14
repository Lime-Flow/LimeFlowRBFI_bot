import asyncio
import logging
import os # Работа с операционной системой
from dotenv import load_dotenv # Инструмент для .env
from aiogram import Bot, Dispatcher
from handlers import router

# Импортируем функцию создания таблицы
from database import create_table

# 1. Загружаем секреты из .env в память компьютера
load_dotenv()

# 2. Достаем токен (если его нет — выдаем ошибку)
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Создаем таблицу БД перед запуском бота
    await create_table()
    print("База данных подключена! 📁")
    
    # Используем токен, который достали
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("Бот запущен! Токен в безопасности. 🔒")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")

async def main():
    # Включаем логирование
    logging.basicConfig(level=logging.INFO)
    
    # Создаем объекты
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # !!! САМОЕ ВАЖНОЕ !!!
    # Подключаем наш роутер к диспетчеру
    dp.include_router(router)
    
    print("Бот запущен в новом режиме!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")