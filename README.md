
# RAG BPMN Generator

## Обзор проекта

Проект **RAG BPMN Generator** представляет собой FastAPI приложение, предназначенное для генерации BPMN 2.0 XML и извлечения сущностей из текстовых описаний бизнес-процессов с использованием технологии Retrieval-Augmented Generation (RAG). Приложение интегрируется с различными базами данных и моделями больших языковых моделей (LLM) через Ollama.

### Основные компоненты и функции:

*   **Архитектура**: FastAPI приложение с модульной структурой (`routers/`, `schemas/`, `prompts/`).
*   **Базы данных**:
    *   **ChromaDB**: Используется для векторного поиска по документам, обеспечивая контекст для LLM.
    *   **PostgreSQL**: Хранит эталонные XML-документы и результаты генерации (сгенерированный BPMN XML или JSON сущности).
    *   **SQLite**: Применяется для управления индексацией документов через `SQLRecordManager`, предотвращая дублирование.
*   **RAG Логика (`rag.py`)**:
    *   Поддерживает генерацию BPMN XML и извлечение сущностей (в формате JSON). 
    *   Может обрабатывать текстовые описания процессов, включая те, что поступают из локальных файлов (`document_path`).
    *   Автоматически собирает релевантный контекст из ChromaDB и связанные эталонные XML из PostgreSQL для формирования запроса к LLM.
*   **API Эндпоинты**: Приложение предоставляет следующие группы эндпоинтов:
    *   **Document Loading (`/document/`)**: Для загрузки и индексации документов в ChromaDB и сохранения связанных XML в PostgreSQL.
    *   **RAG Logic (`/rag/`)**: Основная логика для выполнения RAG запросов и получения сгенерированных BPMN XML или JSON сущностей.
    *   **System Monitoring (`/system/`)**: Эндпоинты для проверки состояния всех ключевых компонентов системы (ChromaDB, PostgreSQL, SQLite Record Manager, Ollama LLM и Ollama Embeddings).
*   **Промпты**: Используются специализированные шаблоны промптов (`bpmn_xml_rules.py`, `bpmn_table_rules.py`) для точного управления выводом LLM (генерация XML или извлечение структурированных данных).

## Развертывание с Docker и Docker Compose

Для упрощения развертывания и управления зависимостями все компоненты приложения контейнеризированы с использованием Docker и Docker Compose.

### 🛠 Инструкция по развертыванию

Чтобы развернуть и запустить приложение, выполните следующие шаги:

#### 1. Установите Docker и Docker Compose
Убедитесь, что у вас установлены Docker и Docker Compose на вашей машине. Если нет, следуйте инструкциям на [официальном сайте Docker](https://docs.docker.com/get-docker/).

#### 2. Разместите файлы в проекте
Убедитесь, что следующие файлы находятся в корневой директории вашего проекта `TUSUR_Project`:

```
TUSUR_Project/
├── app/
│   ├── ... (ваши Python файлы: main.py, routers/, schemas/, prompts/, constants.py, dependencies.py, db_main.py, chroma_async.py)
├── data/
│   ├── ... (папки vector_store/, reference_documents/, db_file/)
├── requirements.txt
├── Dockerfile
├── .env
└── docker-compose.yml
```

#### 3. Запустите Docker Compose
Перейдите в корневую директорию проекта (`TUSUR_Project`) в терминале и выполните следующую команду:

```bash
docker-compose up --build -d
```

*   `up`: Запускает контейнеры, определенные в `docker-compose.yml`.
*   `--build`: Пересобирает Docker-образ для сервиса `api` (ваше FastAPI приложение) на основе `Dockerfile`. Это гарантирует, что все последние изменения в коде и зависимостях будут включены.
*   `-d`: Запускает контейнеры в фоновом режиме (detached mode), чтобы они продолжали работать после закрытия терминала.

#### 4. Загрузите модели Ollama
После успешного запуска `docker-compose` сервис Ollama будет работать, но модели LLM (`gemma3:4b`) и эмбеддингов (`snowflake-arctic-embed2:latest`) необходимо загрузить. Для этого выполните команды в терминале:

```bash
docker exec -it ollama ollama run gemma3:4b
docker exec -it ollama ollama run snowflake-arctic-embed2:latest
```

Эти команды запускают процесс загрузки моделей внутри Ollama-контейнера. Дождитесь завершения загрузки для обеих моделей. Если модели уже скачаны, эти команды просто их запустят.

#### 5. Проверьте статус сервисов
Вы можете проверить статус запущенных контейнеров, чтобы убедиться, что все сервисы работают корректно:

```bash
docker-compose ps
```

Все сервисы (`db`, `ollama`, `api`) должны иметь статус `Up`.

#### 6. Доступ к приложению
После того, как все сервисы запущены, вы можете получить доступ к приложению:

*   **FastAPI Swagger UI**: Откройте `http://localhost:8000/docs` в вашем браузере. Здесь вы найдете полную интерактивную документацию по всем доступным эндпоинтам вашего API.
*   **Ollama UI**: Если вы используете какой-либо пользовательский интерфейс для Ollama, он будет доступен на `http://localhost:11434`.

#### 7. Остановка и удаление контейнеров
Чтобы остановить и удалить все контейнеры, сети и тома, созданные Docker Compose, выполните:

```bash
docker-compose down -v
```

*   `down`: Останавливает и удаляет контейнеры, определенные в `docker-compose.yml`.
*   `-v`: Удаляет тома данных, включая `postgres_data` и `ollama_data`. **Используйте с осторожностью**, так как это приведет к потере всех данных PostgreSQL, сохраненных моделей Ollama и данных ChromaDB/SQLite. Если вы хотите сохранить данные, опустите флаг `-v`.

Этот процесс завершает контейнеризацию и развертывание вашего приложения. Теперь вы можете использовать его в любой среде, где установлен Docker!

<!--
[AI_CONTEXT_BLOCK]
Project: TUSUR RAG BPMN Generator
State: Dockerization complete (requirements.txt, Dockerfile, .env, docker-compose.yml created). Instructions for Docker deployment provided and included in README.md. Development phase is complete.
Instructions: The user has updated the README.md. The next steps involve using and evaluating the deployed application in a Dockerized environment, or proceeding with deployment to a cloud environment. I should be ready to assist with testing the Docker setup, or to continue with further development if the user requests it (e.g., adding more features, refining existing ones, or exploring cloud deployment options).
-->
