
from fastapi import FastAPI
from routers import document_loader, rag, monitor_router
from dependencies import connect_and_create_db, disconnect_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполняется при запуске приложения: подключаемся к БД и создаем таблицы
    print("Запуск приложения: Подключение к БД и проверка таблиц...")
    await connect_and_create_db()
    print("Приложение запущено.")
    yield
    # Выполняется при остановке приложения: закрываем соединение с БД
    print("Остановка приложения: Отключение от БД...")
    await disconnect_db()
    print("Приложение остановлено.")

app = FastAPI(
    title="TUSUR RAG BPMN Generator Service",
    description="API для генерации BPMN XML и извлечения сущностей с использованием RAG на основе документов и Ollama",
    version="1.0.0",
    lifespan=lifespan
)

# Включаем роутеры
app.include_router(document_loader.router, prefix="/document", tags=["Document Loading"])
app.include_router(rag.router, prefix="/rag", tags=["RAG Logic"])
app.include_router(monitor_router.router, prefix="/system", tags=["System Monitoring"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Запущен сервис генератора BPMN RAG! Документацию по API можно найти по адресу: http://localhost:8000/docs."}
