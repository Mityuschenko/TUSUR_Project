
import uuid
import os
from dependencies import chroma, llm, database, xml_documents_table, generated_results_table
from prompts.bpmn_xml_rules import template as xml_template
from prompts.bpmn_table_rules import template as table_template
from schemas.search_query import SearchQuery
from schemas.db_models import GeneratedResult
from fastapi import APIRouter, Body, HTTPException, Query
from langchain_core.prompts import ChatPromptTemplate
import datetime

# Импортируем загрузчик для чтения файлов с диска
from routers.document_loader import _read_document_content
from fastapi import UploadFile
import io

router = APIRouter()

@router.post("/search/rag")
async def rag(search_query: SearchQuery = Body(), document_path: str = Query(None)):
    if not search_query.content:
        raise HTTPException(status_code=400, detail="Запрос пуст")

    # 1. Загрузка внешнего документа, если указан путь
    extra_doc_content = ""
    if document_path:
        if not os.path.exists(document_path):
            raise HTTPException(status_code=404, detail="Файл по указанному пути не найден")

        # Создаем временный объект UploadFile для использования существующей функции
        with open(document_path, "rb") as f:
            file_content = f.read()
            fake_file = UploadFile(filename=os.path.basename(document_path), file=io.BytesIO(file_content))
            extra_doc_content = await _read_document_content(fake_file)

    # 2. Поиск в Chroma
    docs = await chroma.asimilarity_search(search_query.content, k=3)
    context_text = "\n\n".join([d.page_content for d in docs])
    parent_id = docs[0].metadata.get("parent_doc_id") if docs else "unknown"

    # 3. Поиск XML в Postgres
    query = xml_documents_table.select().where(xml_documents_table.c.parent_doc_id == parent_id)
    db_xml = await database.fetch_one(query)
    if db_xml:
        context_text += f"\n\nПример эталонного XML:\n{db_xml['xml_content']}"

    # 4. Формируем комбинированный ввод
    # В input попадает и инструкция пользователя, и текст целевого документа
    full_input = search_query.content
    if extra_doc_content:
        full_input = f"ИНСТРУКЦИЯ: {search_query.content}\n\nТЕКСТ ДОКУМЕНТА ДЛЯ ОБРАБОТКИ:\n{extra_doc_content}"

    # 5. Выбор шаблона
    user_request = search_query.content.lower()
    is_xml_workflow = "xml" in user_request
    selected_template = xml_template if is_xml_workflow else table_template
    result_type = "xml" if is_xml_workflow else "json"

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", selected_template),
        ("human", "{input}"),
    ])

    chain = chat_prompt | llm
    response = await chain.ainvoke({"context": context_text, "input": full_input})

    # 6. Сохранение и ответ
    new_id = uuid.uuid4()
    insert_query = generated_results_table.insert().values(
        id=new_id,
        parent_doc_id=parent_id,
        result_type=result_type,
        content=response.content,
        created_at=datetime.datetime.utcnow()
    )
    await database.execute(insert_query)

    return {
        "result_link": f"/get/result/{new_id}",
        "type": result_type,
        "parent_doc_id": parent_id
    }

@router.get("/get/result/{result_id}")
async def get_result(result_id: uuid.UUID):
    query = generated_results_table.select().where(generated_results_table.c.id == result_id)
    result = await database.fetch_one(query)
    if not result:
        raise HTTPException(status_code=404, detail="Результат не найден")
    return {"content": result["content"], "type": result["result_type"]}
