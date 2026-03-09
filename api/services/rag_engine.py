import os
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from api.services.scheme_loader import load_schemes
from api.config import settings

class RAGEngine:
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.schemes = []
        self.embedding_dimension = 384
        self.vector_store_path = settings.vector_store_path
        
    def load_documents(self):
        print("Loading schemes for RAG Engine...")
        self.schemes = load_schemes()
        return self.schemes
        
    def create_embeddings(self, texts):
        print(f"Creating embeddings for {len(texts)} texts...")
        return self.encoder.encode(texts)
        
    def build_vector_index(self):
        if not self.schemes:
            self.load_documents()
            
        if not self.schemes:
            print("No schemes found to index.")
            return
            
        texts_to_embed = []
        for s in self.schemes:
            # Combine relevant text fields for embedding
            text_rep = f"{s['name']}. {s['description']}. Eligibility: {s['eligibility']}. Benefits: {s['benefits']}"
            texts_to_embed.append(text_rep)
            
        embeddings = self.create_embeddings(texts_to_embed)
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        faiss.normalize_L2(embeddings) # normalize for cosine similarity
        self.index.add(embeddings)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
        # Write to disk
        faiss.write_index(self.index, self.vector_store_path)
        print("Vector index built and saved.")

    def search_similar(self, query: str, top_k: int = 3):
        if self.index is None:
            if os.path.exists(self.vector_store_path):
                self.index = faiss.read_index(self.vector_store_path)
            else:
                self.build_vector_index()
                
        if not self.schemes:
            self.load_documents()

        if self.index is None or not self.schemes:
            return []

        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.schemes):
                results.append(self.schemes[i])
                
        return results

    def generate_answer(self, context: str, question: str) -> str:
        # In a real RAG application, you would pass the context and question
        # to an LLM like OpenAI, Cohere, Llama2, etc. to generate a natural language response.
        # Since this is a prototype, we'll return a simulated simplified response.
        
        if not context:
            return "मुझे आपके सवाल के लिए कोई प्रासंगिक योजना (scheme) नहीं मिली। I couldn't find a relevant scheme."
            
        answer = f"यहाँ आपके सवाल के आधार पर कुछ जानकारी है: \n\n{context}\n\nयह जानकारी सरकारी स्रोतों के आधार पर है।"
        return answer

rag_engine = RAGEngine()
