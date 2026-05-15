
from fastapi import APIRouter, HTTPException
from dependencies import chroma, database, record_manager, llm, embedding_model, xml_documents_table, generated_results_table

router = APIRouter()

@router.get("/monitor/chroma")
async def check_chroma_status():
    """Проверяет статус ChromaDB."""
    try:
        # Попытка получить информацию о коллекции для проверки доступности
        collection_info = await chroma.aget()
        count = len(collection_info['ids']) # Считаем количество элементов в коллекции
        return {"status": "ok", "message": "ChromaDB доступна", "collection_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChromaDB недоступна: {str(e)}")

@router.get("/monitor/postgresql")
async def check_postgresql_status():
    """Проверяет статус PostgreSQL и наличие таблиц."""
    try:
        await database.connect()
        await database.fetch_one("SELECT 1") # Простая проверка соединения

        # Проверка наличия и количества записей в xml_documents_table
        xml_count_query = xml_documents_table.count()
        xml_count = await database.fetch_val(xml_count_query)

        # Проверка наличия и количества записей в generated_results_table
        generated_count_query = generated_results_table.count()
        generated_count = await database.fetch_val(generated_count_query)

        await database.disconnect()
        return {
            "status": "ok",
            "message": "PostgreSQL доступна",
            "xml_documents_count": xml_count,
            "generated_results_count": generated_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PostgreSQL недоступна: {str(e)}")

@router.get("/monitor/sqlite_record_manager")
async def check_sqlite_record_manager_status():
    """Проверяет статус SQLite Record Manager."""
    try:
        # Проверяем, что схема существует и можем выполнить простой запрос
        # aget_keys вернет пустой список, если таблица пуста, но не вызовет ошибку
        keys = await record_manager.aget_keys(list_keys=["non_existent_key"], namespace="Stardew")

        # Можно также попытаться получить общее количество записей
        # Для этого нужно напрямую обратиться к базе данных SQLite
        import sqlite3
        from constants import RECORD_MANAGER
        db_path = RECORD_MANAGER.replace("sqlite+aiosqlite:///", "")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM upsertion_record WHERE namespace = 'Stardew'")
        record_count = cursor.fetchone()[0]
        conn.close()

        return {"status": "ok", "message": "SQLite Record Manager доступен", "record_count": record_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQLite Record Manager недоступен: {str(e)}")

@router.get("/monitor/ollama_llm")
async def check_ollama_llm_status():
    """Проверяет доступность Ollama LLM (gemma3:4b) ."""
    try:
        response = await llm.ainvoke("Привет, как дела?")
        if response.content: # Проверяем, что ответ не пустой
            return {"status": "ok", "message": "Ollama LLM (gemma3:4b) доступна", "test_response": response.content[:50] + "..."}
        else:
            raise HTTPException(status_code=500, detail="Ollama LLM вернула пустой ответ.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama LLM (gemma3:4b) недоступна: {str(e)}")

@router.get("/monitor/ollama_embeddings")
async def check_ollama_embeddings_status():
    """Проверяет доступность Ollama Embeddings (snowflake-arctic-embed2:latest)."""
    try:
        # Попытка сгенерировать эмбеддинг для тестовой строки
        embedding = await embedding_model.aembed_query("это тестовая строка")
        if isinstance(embedding, list) and len(embedding) > 0: # Проверяем, что получен список чисел
            return {"status": "ok", "message": "Ollama Embeddings (snowflake-arctic-embed2:latest) доступна", "embedding_length": len(embedding)}
        else:
            raise HTTPException(status_code=500, detail="Ollama Embeddings вернула некорректный результат.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama Embeddings (snowflake-arctic-embed2:latest) недоступна: {str(e)}")
