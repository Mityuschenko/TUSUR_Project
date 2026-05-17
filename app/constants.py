
from pathlib import Path
import os
from dotenv import load_dotenv # Добавлено для явной загрузки .env

# Явно загружаем переменные окружения из файла .env
load_dotenv() # Добавлено для явной загрузки .env

# Папка, где лежит constants.py
CURRENT_DIR = Path(__file__).parent

# Формируем путь: на уровень выше → папка data → vector_store
CHROMA_PATH = CURRENT_DIR.parent / "data" / "vector_store"
# Создаём папку, если её не существует (включая родительские каталоги)
CHROMA_PATH.mkdir(parents=True, exist_ok=True)
# Преобразуем в строку — так как ожидает Chroma
CHROMA_PATH = str(CHROMA_PATH)

CHROMA_COLLECTION = "embeddings"
EMBEDDINGS_MODEL = "snowflake-arctic-embed2:latest"



# Формируем путь: на уровень выше → папка data → db_file
DB_PATH = CURRENT_DIR.parent / "data" / "db_file" / "record_manager_cache.sql"
# Создаём родительские папки, если их нет
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
# Форматируем строку для SQLAlchemy
RECORD_MANAGER = f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"

LLM_MODEL = "gemma3:4b"

# Теперь эти константы будут браться из .env, или использовать значения по умолчанию
POSTGRES_USER = os.getenv("POSTGRES_USER", "Analyst")
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '12345678')
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "bpmn_models")

POSTGRES_CONNECTION_ASYNC_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
POSTGRES_CONNECTION_SYNC_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
