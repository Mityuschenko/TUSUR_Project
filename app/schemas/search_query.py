
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    content: str
    metadata: dict | None = Field(default=None)
