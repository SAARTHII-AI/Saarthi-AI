import os
import numpy as np
import json
import requests
import time
from api.services.scheme_loader import load_schemes
from api.config import settings

class RAGEngine:
    def __init__(self):
        self.model_id = "sentence-transformers/all-MiniLM-L6-v2"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        self.headers = {"Authorization": f"Bearer {settings.huggingface_api_token}"} if settings.huggingface_api_token else {}
        self.index = None
        self.schemes = []
        self.embedding_dimension = 384
        self.vector_store_path = settings.vector_store_path
        
    def load_documents(self):
        print("Loading schemes for RAG Engine...")
        self.schemes = load_schemes()
        return self.schemes
        
    def create_embeddings(self, texts):
        print(f"Creating embeddings for {len(texts)} texts via HuggingFace API...")
        
        # HuggingFace Inference API has a limit on input size, we might need to chunk if many texts
        # For this prototype, we'll assume the number of schemes is small enough for one request
        response = requests.post(self.api_url, headers=self.headers, json={"inputs": texts, "options": {"wait_for_model": True}})
        
        if response.status_code != 200:
            print(f"Error from HuggingFace API: {response.text}")
            # Fallback or error handling
            raise Exception(f"Failed to get embeddings: {response.text}")
            
        return np.array(response.json())
        
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
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        self.index = embeddings
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
        # Write to disk using numpy
        np.save(self.vector_store_path, self.index)
        print("Vector index built and saved using NumPy.")

    def search_similar(self, query: str, top_k: int = 3):
        if self.index is None:
            if os.path.exists(self.vector_store_path):
                self.index = np.load(self.vector_store_path)
            else:
                self.build_vector_index()
                
        if not self.schemes:
            self.load_documents()
            
        if self.index is None or not self.schemes:
            return []

        # Get query embedding
        query_embedding = self.create_embeddings([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Compute cosine similarities
        similarities = np.dot(self.index, query_embedding.T).flatten()
        
        # Get top-k indices
        indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i in indices:
            if i < len(self.schemes):
                results.append(self.schemes[i])
                
        return results

    def generate_answer(self, context: str, question: str) -> str:
        if not context:
            return "मुझे आपके सवाल के लिए कोई प्रासंगिक योजना (scheme) नहीं मिली। I couldn't find a relevant scheme."
            
        answer = f"यहाँ आपके सवाल के आधार पर कुछ जानकारी है: \n\n{context}\n\nयह जानकारी सरकारी स्रोतों के आधार पर है।"
        return answer

rag_engine = RAGEngine()
