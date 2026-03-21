from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "auto"
    location: Optional[str] = None
    age: Optional[int] = None
    income: Optional[int] = None
    occupation: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None
    scheme_type: Optional[str] = None
    crop: Optional[str] = None
    land_size: Optional[str] = None

class SchemeRecommedation(BaseModel):
    name: str
    description: str
    type: Optional[str] = None
    state: Optional[str] = None
    documents_links: Optional[List[str]] = None

class DocLink(BaseModel):
    title: str
    url: str

class HelpCenter(BaseModel):
    name: str
    type: str
    phone: str
    address: str
    district: str
    maps_url: Optional[str] = None

class QueryResponse(BaseModel):
    intent: str
    answer: str
    recommended_schemes: List[SchemeRecommedation] = []
    response_language: str = "en"
    doc_links: List[DocLink] = []
    nearest_centers: List[HelpCenter] = []
