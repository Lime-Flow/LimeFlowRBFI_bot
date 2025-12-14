from aiogram import Router, F
from aiogram.types import (
    Message, 
    CallbackQuery, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.filters import Command
import aiohttp 
import os
from database import get_all_users # <-- Добавляем новую функцию

from database import add_user, get_users_count

# 1. Инициализируем роутер
router = Router()

# --- СОЗДАЕМ КЛАВИАТУРЫ ---

# Нижняя клавиатура (Reply)
kb_list = [
    [KeyboardButton(text="Привет"), KeyboardButton(text="Пока")],
    [KeyboardButton(text="Бросить кубик 🎲"), KeyboardButton(text="Курс BTC 💰")] 
]
main_keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)

# Инлайн клавиатура (Ссылки)
inline_kb_list = [
    [InlineKeyboardButton(text="Мой GitHub 💻", url="https://github.com")],
    [InlineKeyboardButton(text="Показать секрет 🔒", callback_data="secret_button")]
]
links_keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


# --- ХЭНДЛЕРЫ (ФУНКЦИИ) ---

@router.message(Command("start"))
async def cmd_start(message: Message):
    # 1. Сохраняем пользователя в БД
    await add_user(message.from_user.id, message.from_user.first_name)
    
    # 2. Узнаем, сколько нас теперь
    count = await get_users_count()
    
    # 3. Отправляем сообщение с результатом
    # (Старую строчку с "Привет! Я вернулся..." мы убрали, теперь будет эта)
    await message.answer(
        f"Привет! Я тебя запомнил. 📝\n"
        f"Ты {count}-й пользователь в моей базе!",
        reply_markup=main_keyboard
    )

@router.message(Command("links"))
async def show_links(message: Message):
    await message.answer("Вот полезные ссылки:", reply_markup=links_keyboard)

# Ловим секретную кнопку
@router.callback_query(F.data == "secret_button")
async def send_secret(callback: CallbackQuery):
    await callback.answer("Тс-с-с!", show_alert=True)
    await callback.message.answer("Ты нашел пасхалку в новом файле! 🥚")

# Ловим кнопку "Курс BTC" (или команду /btc)
@router.message(F.text == "Курс BTC 💰")
@router.message(Command("btc"))
async def send_crypto(message: Message):
    await message.answer("Узнаю курс... ⏳")
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            price = data['bitcoin']['usd']
            await message.answer(f"💰 Биткоин: {price} $")

# Ловим кубик
@router.message(F.text == "Бросить кубик 🎲")
async def send_dice(message: Message):
    await message.answer_dice(emoji="🎲")

# Обработка текста (должна быть в конце)
@router.message(F.text.lower() == "привет")
async def answer_hello(message: Message):
    await message.answer("И тебе привет!")

@router.message(Command("sendall"))
async def cmd_sendall(message: Message):
    # 1. Проверка на админа
    # Получаем ID админа из .env (превращаем в строку, так как из env приходит строка)
    admin_id = os.getenv("ADMIN_ID")
    
    # Сравниваем ID того, кто написал (str(message.from_user.id)), с Админом
    if str(message.from_user.id) != admin_id:
        await message.answer("❌ У тебя нет прав на эту команду.")
        return

    # 2. Парсим текст (отделяем команду /sendall от текста)
    # Пример: "/sendall Привет всем" -> parts = ["/sendall", "Привет", "всем"]
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Ошибка. Пиши так: /sendall Текст рассылки")
        return
        
    text_to_send = parts[1] # Это сам текст ("Привет всем")
    
    # 3. Достаем всех из базы
    users = await get_all_users()
    count = 0
    
    # 4. Рассылка
    for user_id in users:
        try:
            # Пытаемся отправить
            await message.bot.send_message(chat_id=user_id, text=text_to_send)
            count += 1
        except Exception:
            # Если пользователь заблокировал бота, будет ошибка. Мы её просто игнорируем.
            pass
            
    await message.answer(f"✅ Рассылка завершена! Сообщение получили: {count} человек.")

@router.message()
async def echo_handler(message: Message):
    await message.answer(f"Я не знаю что ответить на: {message.text}")