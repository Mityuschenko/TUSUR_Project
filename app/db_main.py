
# @title Запуск ТОЛЬКО если нужно создать базы данных SQLite и PostgreSQL

# в данном случае имя файла базы данных SQLite - record_manager_cache.sql

# Импортируем модуль asyncio для работы с асинхронным кодом и управления циклом событий
import asyncio

# Импортируем путь к базе данных SQLite из модуля с константами нашего приложения
from constants import RECORD_MANAGER

# Импортируем класс SQLRecordManager из LangChain для управления индексами документов
from langchain_classic.indexes import SQLRecordManager

# Импортируем функцию для подключения к БД и создания таблиц. Она определена в файле dependencies.py
from dependencies import connect_and_create_db

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

# Главная асинхронная функция для инициализации PostgreSQL таблицы
async def main_pg_init():
    print("Попытка подключения к PostgreSQL и создания таблицы...")
    await connect_and_create_db()
    print("Процесс инициализации PostgreSQL завершен.")

# Проверяем, что скрипт запущен напрямую пользователем, а не импортирован как модуль
if __name__ == "__main__":
  asyncio.run(main_SQLite_init())
  asyncio.run(main_pg_init())
