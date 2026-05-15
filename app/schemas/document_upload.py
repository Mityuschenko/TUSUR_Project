
from pydantic import BaseModel, Field


class DocumentUpload(BaseModel):
    content: str
    metadata: dict | None = Field(default=None)
