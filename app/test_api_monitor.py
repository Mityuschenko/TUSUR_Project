
from fastapi import FastAPI
from routers.monitor_router import router as monitor_router
from dependencies import connect_and_create_db, disconnect_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполняется при запуске: подключаемся к БД и создаем таблицы
    await connect_and_create_db()
    yield
    # Выполняется при остановке: закрываем соединение
    await disconnect_db()

app = FastAPI(
    title="Тестирование сервиса мониторинга проекта",
    description="Тестирование эндпоинтов мониторинга для TUSUR RAG BPMN Generator",
    lifespan=lifespan
)

app.include_router(monitor_router, tags=["Monitoring"])

# Заметка для пользователя:
# Чтобы запустить этот тест в Colab, используйте uvicorn в отдельной ячейке:
# !uvicorn test_api_monitor:app --host 0.0.0.0 --port 8000 --reload
