
from uuid import UUID
import datetime

from chroma_async import AsyncChroma
from databases import Database
from sqlalchemy.dialects import postgresql
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    DateTime,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from constants import (
    CHROMA_COLLECTION,
    CHROMA_PATH,
    EMBEDDINGS_MODEL,
    LLM_MODEL,
    RECORD_MANAGER,
    POSTGRES_CONNECTION_ASYNC_URL,
    POSTGRES_CONNECTION_SYNC_URL,

)
from schemas.db_models import XMLDocument

from langchain_classic.indexes import SQLRecordManager
from langchain_ollama import ChatOllama, OllamaEmbeddings

# Инициализация эмбеддингов
embedding_model = OllamaEmbeddings(model=EMBEDDINGS_MODEL)

# Подключение к Chroma
chroma = AsyncChroma(
    collection_name=CHROMA_COLLECTION,
    persist_directory=CHROMA_PATH,
    embedding_function=embedding_model,
)

# Инициализация менеджера записей для отслеживания состояния документов
record_manager = SQLRecordManager(
    namespace="Stardew", db_url=RECORD_MANAGER, async_mode=True
)

# Инициализация LLM
llm = ChatOllama(model=LLM_MODEL)

# Инициализация PostgreSQL базы данных
database = Database(POSTGRES_CONNECTION_ASYNC_URL)  # Создаёт объект базы данных с использованием асинхронной библиотеки (например, databases), передавая строку подключения к PostgreSQL
metadata = MetaData()  # Инициализирует объект MetaData — контейнер для описания структуры таблиц и схемы БД в SQLAlchemy


# Определение таблицы для XML документов
xml_documents_table = Table(  # Создаёт описание таблицы в памяти (не в БД) с помощью класса Table из SQLAlchemy
    "xml_documents",  # Имя таблицы в базе данных
    metadata,  # Ссылка на объект MetaData, к которому привязывается таблица
    Column("id", PG_UUID(as_uuid=True), primary_key=True, default=UUID),  # Колонка id: UUID как первичный ключ; as_uuid=True сохраняет тип UUID Python; default=UUID задаёт генерацию UUID по умолчанию
    Column("parent_doc_id", String, index=True, nullable=False),  # Колонка parent_doc_id: строковый тип, с индексом для быстрого поиска, обязательное поле (не может быть NULL)
    Column("filename", String, nullable=False),  # Колонка filename: строковый тип, обязательное поле
    Column("xml_content", Text, nullable=False),  # Колонка xml_content: тип Text для хранения больших текстовых данных (XML), обязательное поле
    Column("upload_timestamp", DateTime, default=datetime.datetime.utcnow),  # Колонка upload_timestamp: тип DateTime для даты и времени загрузки; default=datetime.datetime.utcnow автоматически устанавливает текущее время UTC при создании записи
)

# Определение таблицы для результатов генерации LLM
generated_results_table = Table(
    "generated_results",
    metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True, default=UUID),
    Column("parent_doc_id", String, index=True),
    Column("result_type", String),
    Column("content", Text),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)

async def connect_and_create_db():
    """Подключается к базе данных и создаёт таблицу XML документов, если её нет."""
    await database.connect()  # Асинхронно подключается к БД через объект database (использует асинхронный драйвер, например asyncpg)
    # URL для create_engine должен быть синхронным. Заменяем '+asyncpg' на синхронный драйвер, например '+psycopg2'
    engine = create_engine(POSTGRES_CONNECTION_SYNC_URL)  # Создаёт движок SQLAlchemy для синхронного взаимодействия с БД (нужен для операций с метаданными)
    metadata.create_all(engine)  # Выполняет SQL‑запросы для создания всех таблиц, описанных в metadata, в БД через движок engine; если таблица уже есть — ничего не делает
    print("Таблица PostgreSQL 'xml_documents' и 'generated_results' созданы или уже существуют.")  # Выводит сообщение о результате операции

async def disconnect_db():
    """Отключается от базы данных."""
    await database.disconnect()  # Асинхронно разрывает соединение с БД через объект database
