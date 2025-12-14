import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiohttp import web # Для сервера

# Твои файлы
from handlers import router
from database import create_table

# Загрузка настроек
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# --- ВЕБ-СЕРВЕР (ЧТОБЫ RENDER НЕ УБИВАЛ БОТА) ---
async def health_check(request):
    """Простая функция: если Render спросит, мы ответим 'OK'"""
    return web.Response(text="Bot is alive!", status=200)

async def start_server():
    """Запуск сервера на порту, который дал Render"""
    try:
        app = web.Application()
        app.router.add_get('/', health_check) # Главная страница
        app.router.add_get('/health', health_check) # Доп. страница для проверок
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Render ОБЯЗАТЕЛЬНО передает порт через переменную PORT
        port = int(os.environ.get("PORT", 8080))
        
        # Запускаем на 0.0.0.0 (доступно для всего интернета)
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        # Пишем в лог большими буквами, чтобы ты увидел
        print(f"✅ ВЕБ-СЕРВЕР ЗАПУЩЕН НА ПОРТУ: {port}")
    except Exception as e:
        print(f"❌ ОШИБКА ЗАПУСКА СЕРВЕРА: {e}")

# --- ГЛАВНАЯ ФУНКЦИЯ ---
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. База данных
    await create_table()
    
    # 2. 🔥 ЗАПУСКАЕМ СЕРВЕР В ФОНЕ (create_task) 🔥
    # Это главная фишка: сервер работает параллельно с ботом
    asyncio.create_task(start_server())
    
    # 3. Запускаем бота
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("🚀 Бот начал работу (Polling)...")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
