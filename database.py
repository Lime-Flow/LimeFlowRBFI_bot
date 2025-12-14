import aiosqlite

# Имя файла базы данных
DB_NAME = 'bot.db'

async def create_table():
    # Создаем соединение с базой
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу users, если её нет
        # В ней будет 2 колонки: user_id (число) и username (текст)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT
            )
        ''')
        # Сохраняем изменения
        await db.commit()

async def add_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        # Пытаемся добавить пользователя
        # INSERT OR IGNORE означает: "Если такой ID уже есть, ничего не делай"
        await db.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
        await db.commit()

async def get_users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        # Считаем количество строк в таблице
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            result = await cursor.fetchone()
            return result[0]
    
async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        # Берем столбец user_id у всех пользователей
        async with db.execute('SELECT user_id FROM users') as cursor:
            # fetchall возвращает список кортежей: [(123,), (456,), ...]
            users = await cursor.fetchall()
            # Превращаем в чистый список чисел: [123, 456, ...]
            return [row[0] for row in users]