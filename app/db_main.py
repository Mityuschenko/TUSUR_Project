
# @title Запуск ТОЛЬКО если нужно создать базы данных SQLite и PostgreSQL

# в данном случае имя файла базы данных SQLite - record_manager_cache.sql

import os
import asyncio # Импортируем модуль asyncio для работы с асинхронным кодом и управления циклом событий
import asyncpg  # Добавьте импорт asyncpg для прямой проверки СУБД
from dotenv import load_dotenv  # Импортируем загрузчик .env
from constants import RECORD_MANAGER # Импортируем путь к базе данных SQLite из модуля с константами нашего приложения
from langchain_classic.indexes import SQLRecordManager # Импортируем класс SQLRecordManager из LangChain для управления индексами документов
from dependencies import connect_and_create_db # Импортируем функцию для подключения к БД и создания таблиц. Она определена в файле dependencies.py

# Загружаем переменные из файла .env в окружение системы
load_dotenv()

# Извлекаем переменные (если их нет в .env, подставятся значения по умолчанию)
DB_USER = os.getenv("POSTGRES_USER", "Analyst")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB", "bpmn_models")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")

# Инициализируем менеджер записей, настраивая его параметры для работы с базой данных
record_manager = SQLRecordManager(
    # Указываем уникальный префикс (пространство имен) для изоляции записей этого проекта
    namespace="Stardew",
    # Передаем строку подключения к нашей локальной базе данных SQLite из константы
    db_url=RECORD_MANAGER,
    # Включаем асинхронный режим работы для бесконфликтного выполнения внутри асинхронного API
    async_mode=True
)

# Объявляем главную асинхронную функцию, которая будет выполнять инициализацию базы SQLite
async def main_SQLite_init():
    # Асинхронно создаем таблицы и схему данных в SQLite, если они еще не созданы
    await record_manager.acreate_schema()


async def create_database_if_not_exists():
    # Подключаемся к системной базе 'postgres' используя переменные окружения
    conn = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database='postgres',
        host=DB_HOST,
        port=int(DB_PORT)
    )

    # Проверяем, существует ли целевая база данных проекта
    db_exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", DB_NAME)

    if not db_exists:
        print(f"База данных {DB_NAME} не найдена. Создаю...")
        await conn.execute(f'CREATE DATABASE "{DB_NAME}" OWNER "{DB_USER}";') # Базы данных в Postgres нельзя создавать внутри транзакций, поэтому используем специальный синтаксис
        print(f"База данных {DB_NAME} успешно создана.")
    else:
        print(f"База данных {DB_NAME} уже существует.")

    await conn.close()

async def main_pg_init(): # Главная асинхронная функция для инициализации PostgreSQL
    print("Проверка наличия базы данных на сервере PostgreSQL...")
    try:
        await create_database_if_not_exists()
    except Exception as e:
        print(f"Ошибка при проверке/создании БД: {e}")

    print("Попытка подключения к PostgreSQL и создания таблиц...")
    await connect_and_create_db()
    print("Процесс initialization PostgreSQL завершен.")

# Проверяем, что скрипт запущен напрямую пользователем, а не импортирован как модуль
if __name__ == "__main__":
    asyncio.run(main_SQLite_init())
    asyncio.run(main_pg_init())
