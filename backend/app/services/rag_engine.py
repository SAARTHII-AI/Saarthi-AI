import logging
from app.services.scheme_loader import load_schemes
from app.config import settings

logger = logging.getLogger(__name__)


def _build_azure_client():
    """Return an AzureOpenAI client if credentials are configured, else None."""
    if settings.offline_only:
        return None
    if not settings.azure_openai_api_key or not settings.azure_openai_endpoint or not settings.azure_openai_deployment:
        return None
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        return client
    except Exception as e:
        logger.warning(f"Could not initialise Azure OpenAI client: {e}")
        return None


class RAGEngine:
    def __init__(self):
        self.schemes = []
        self._azure_client = None

    def load_documents(self):
        print("Loading schemes for RAG Engine...")
        self.schemes = load_schemes()
        return self.schemes

    def create_embeddings(self, texts):
        return []

    def build_vector_index(self):
        if not self.schemes:
            self.load_documents()
        print("Vector index build skipped (keyword-search mode).")

    def search_similar(self, query: str, top_k: int = 3):
        """Lightweight keyword-based search."""
        if not self.schemes:
            self.load_documents()

        if not self.schemes:
            return []

        query_words = set(query.lower().split())
        scored_schemes = []

        for scheme in self.schemes:
            text = (scheme['name'] + " " + scheme['description']).lower()
            score = sum(1 for word in query_words if word in text)
            if score > 0:
                scored_schemes.append((score, scheme))

        scored_schemes.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored_schemes[:top_k]]

    def generate_answer(self, context: str, question: str) -> str:
        """
        Generate an answer using Azure OpenAI when available.
        Falls back to the template string on any failure or when offline.
        """
        if not context:
            return (
                "मुझे आपके सवाल के लिए कोई प्रासंगिक योजना (scheme) नहीं मिली। "
                "I couldn't find a relevant scheme for your question."
            )

        client = _build_azure_client()
        if client:
            try:
                system_prompt = (
                    "You are SaarthiAI, a helpful assistant that explains Indian government "
                    "schemes to citizens. Answer in clear, simple language. "
                    "Use the context provided. If the context is insufficient, say so honestly."
                )
                user_prompt = (
                    f"Context about relevant government schemes:\n{context}\n\n"
                    f"User question: {question}\n\n"
                    "Please provide a helpful, accurate answer based on the context above."
                )
                response = client.chat.completions.create(
                    model=settings.azure_openai_deployment,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_completion_tokens=512,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Azure OpenAI call failed, using fallback: {e}")

        return (
            f"यहाँ आपके सवाल के आधार पर कुछ जानकारी है:\n\n"
            f"{context}\n\n"
            f"यह जानकारी सरकारी स्रोतों के आधार पर है।"
        )


rag_engine = RAGEngine()
