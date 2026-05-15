
from fastapi import FastAPI
from routers.rag import router as rag_router
from dependencies import database, connect_and_create_db, disconnect_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполняется при запуске: подключаемся к БД и создаем таблицы
    await connect_and_create_db()
    yield
    # Выполняется при остановке: закрываем соединение
    await disconnect_db()

# Создаем приложение с жизненным циклом (lifespan)
app = FastAPI(
    title="TUSUR RAG Service Test",
    description="Тестирование RAG с поддержкой генерации BPMN XML и извлечения сущностей",
    lifespan=lifespan
)

# Подключаем роутер с нашей бизнес-логикой
app.include_router(rag_router, tags=["RAG"])

# Заметка для пользователя:
# Чтобы запустить этот тест в Colab, используйте uvicorn в отдельной ячейке:
# !uvicorn test_api_rag:app --host 0.0.0.0 --port 8000
