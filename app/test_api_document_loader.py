
from fastapi import FastAPI, UploadFile, File # Добавляем UploadFile, File
from routers.document_loader import router  # Импорт роутера из файла

app = FastAPI(title="Загрузка документов для RAG")

# Подключаем роутер
app.include_router(router)

# Пример использования нового эндпоинта (требует клиента для загрузки файлов, например Postman/Insomnia/curl)
# from httpx import AsyncClient
# async def test_upload_file_and_xml():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         with open("example.txt", "rb") as doc_file, open("example.xml", "rb") as xml_file:
#             response = await ac.post(
#                 "/load/file_and_xml",
#                 files={"document_file": ("example.txt", doc_file, "text/plain"),
#                        "xml_file": ("example.xml", xml_file, "application/xml")}
#             )
#             assert response.status_code == 200
#             print(response.json())
