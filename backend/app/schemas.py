from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "hi"
    location: Optional[str] = None
    age: Optional[int] = None
    income: Optional[int] = None
    occupation: Optional[str] = None
    category: Optional[str] = None

class SchemeRecommedation(BaseModel):
    name: str
    description: str

class QueryResponse(BaseModel):
    intent: str
    answer: str
    recommended_schemes: List[SchemeRecommedation] = []
