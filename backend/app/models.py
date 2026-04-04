from sqlalchemy import Column, Integer, String, Text, JSON
from .database import Base

class Scheme(Base):
    __tablename__ = "schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    type = Column(String)
    state = Column(String, index=True)
    target_group = Column(String, index=True)
    eligibility = Column(Text)
    benefits = Column(Text)
    application_url = Column(String)
    helpline = Column(String)
    documents = Column(JSON)
    documents_links = Column(JSON)
    
    _name_lower = Column(String, index=True)
    _desc_lower = Column(Text)
    _target_lower = Column(String)
    _elig_lower = Column(Text)
    _benefits_lower = Column(Text)
    _state_lower = Column(String)
