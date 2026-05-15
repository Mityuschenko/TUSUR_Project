
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class XMLDocument(BaseModel):
    """Модель для хранения загруженных XML документов"""
    id: UUID = Field(default_factory=uuid4)
    parent_doc_id: str
    filename: str
    xml_content: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)

class GeneratedResult(BaseModel):
    """Модель для хранения результатов генерации LLM (XML или JSON)"""
    id: UUID = Field(default_factory=uuid4)
    parent_doc_id: str
    result_type: str # 'xml' или 'json'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
