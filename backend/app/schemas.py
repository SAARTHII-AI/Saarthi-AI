from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "auto"
    location: Optional[str] = None
    age: Optional[int] = None
    income: Optional[int] = None
    occupation: Optional[str] = None
    category: Optional[str] = None


class SchemeRecommedation(BaseModel):
    name: str
    description: str


class DocumentLink(BaseModel):
    """Represents an official document link for a government scheme."""
    title: str
    url: str
    description: str
    source: str


class QueryResponse(BaseModel):
    intent: str
    answer: str
    recommended_schemes: List[SchemeRecommedation] = Field(default_factory=list)
    document_links: List[DocumentLink] = Field(default_factory=list)
    response_language: str = "en"
