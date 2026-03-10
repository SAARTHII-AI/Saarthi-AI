import os
import json
from app.services.scheme_loader import load_schemes
from app.config import settings

class RAGEngine:
    def __init__(self):
        # Local models removed for Vercel size limits (250MB)
        # In production, use Google Gemini or OpenAI API here.
        self.schemes = []
        
    def load_documents(self):
        print("Loading schemes for RAG Engine...")
        self.schemes = load_schemes()
        return self.schemes
        
    def create_embeddings(self, texts):
        # Mock embedding creation
        return []
        
    def build_vector_index(self):
        # Mock index building
        if not self.schemes:
            self.load_documents()
        print("Vector index build skipped (Vercel Compatibility Mode).")

    def search_similar(self, query: str, top_k: int = 3):
        """
        Lightweight keyword-based search as a replacement for FAISS.
        """
        if not self.schemes:
            self.load_documents()

        if not self.schemes:
            return []

        # Simple keyword matching as a fallback for FAISS
        query_words = set(query.lower().split())
        scored_schemes = []
        
        for scheme in self.schemes:
            text = (scheme['name'] + " " + scheme['description']).lower()
            score = sum(1 for word in query_words if word in text)
            if score > 0:
                scored_schemes.append((score, scheme))
        
        # Sort by score descending
        scored_schemes.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored_schemes[:top_k]]

    def generate_answer(self, context: str, question: str) -> str:
        if not context:
            return "मुझे आपके सवाल के लिए कोई प्रासंगिक योजना (scheme) नहीं मिली। I couldn't find a relevant scheme."
            
        answer = f"यहाँ आपके सवाल के आधार पर कुछ जानकारी है: \n\n{context}\n\nयह जानकारी सरकारी स्रोतों के आधार पर है।"
        return answer

rag_engine = RAGEngine()
