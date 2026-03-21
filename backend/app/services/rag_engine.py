import logging
import hashlib
import time
from typing import Optional, Dict, Any
from app.services.scheme_loader import load_schemes
from app.config import settings

logger = logging.getLogger(__name__)

_answer_cache = {}
_ANSWER_CACHE_MAX = 200
_ANSWER_CACHE_TTL = 1800


def _build_azure_client():
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

    def search_similar(self, query: str, top_k: int = 5, user_state: Optional[str] = None, occupation: Optional[str] = None):
        if not self.schemes:
            self.load_documents()

        if not self.schemes:
            return []

        query_lower = query.lower()
        query_words = set(query_lower.split())

        occupation_lower = (occupation or "").lower()

        scored_schemes = []

        for scheme in self.schemes:
            name_lower = scheme['name'].lower()
            desc_lower = scheme.get('description', '').lower()
            target_lower = scheme.get('target_group', '').lower()
            elig_lower = scheme.get('eligibility', '').lower()
            state_lower = (scheme.get('state') or '').lower()

            searchable = f"{name_lower} {desc_lower} {target_lower} {elig_lower} {state_lower}"

            score = 0

            for word in query_words:
                if len(word) < 3:
                    continue
                if word in name_lower:
                    score += 3
                elif word in target_lower:
                    score += 2
                elif word in desc_lower or word in elig_lower:
                    score += 1

            if user_state and state_lower and user_state.lower() in state_lower:
                score += 2

            if scheme.get('type') == 'central':
                score += 0.5

            if occupation_lower:
                if occupation_lower in target_lower or occupation_lower in desc_lower:
                    score += 2

            if score > 0:
                scored_schemes.append((score, scheme))

        scored_schemes.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored_schemes[:top_k]]

    def _build_rich_context(self, schemes: list, web_snippets: list = None, farmer_profile: dict = None) -> str:
        parts = []

        if farmer_profile:
            profile_parts = []
            if farmer_profile.get("state"):
                profile_parts.append(f"State: {farmer_profile['state']}")
            if farmer_profile.get("crop"):
                profile_parts.append(f"Primary Crop: {farmer_profile['crop']}")
            if farmer_profile.get("land_size"):
                profile_parts.append(f"Land Size: {farmer_profile['land_size']} acres")
            if farmer_profile.get("income"):
                profile_parts.append(f"Annual Income: ₹{farmer_profile['income']}")
            if farmer_profile.get("occupation"):
                profile_parts.append(f"Occupation: {farmer_profile['occupation']}")
            if profile_parts:
                parts.append("=== FARMER PROFILE ===\n" + "\n".join(profile_parts))

        if schemes:
            scheme_texts = []
            for s in schemes:
                lines = [f"Scheme: {s['name']}"]
                if s.get('type'):
                    lines.append(f"  Type: {s['type'].title()} scheme")
                if s.get('state'):
                    lines.append(f"  State: {s['state']}")
                if s.get('description'):
                    lines.append(f"  Description: {s['description']}")
                if s.get('eligibility'):
                    lines.append(f"  Eligibility: {s['eligibility']}")
                if s.get('target_group'):
                    lines.append(f"  Target Group: {s['target_group']}")
                if s.get('documents_links'):
                    lines.append(f"  Official Links: {', '.join(s['documents_links'])}")
                scheme_texts.append("\n".join(lines))
            parts.append("=== GOVERNMENT SCHEMES ===\n" + "\n\n".join(scheme_texts))

        if web_snippets:
            parts.append("=== WEB SEARCH RESULTS ===\n" + "\n".join(f"- {s}" for s in web_snippets))

        return "\n\n".join(parts)

    def _cache_key(self, context: str, question: str, profile: dict = None) -> str:
        raw = f"{question}|{context[:500]}|{str(sorted((profile or {}).items()))}"
        return hashlib.md5(raw.encode()).hexdigest()

    def generate_answer(self, context: str, question: str, farmer_profile: dict = None) -> str:
        if not context:
            return (
                "मुझे आपके सवाल के लिए कोई प्रासंगिक योजना (scheme) नहीं मिली। "
                "I couldn't find a relevant scheme for your question."
            )

        cache_key = self._cache_key(context, question, farmer_profile)
        cached = _answer_cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < _ANSWER_CACHE_TTL:
            logger.info("Returning cached answer")
            return cached["answer"]

        client = _build_azure_client()
        if client:
            try:
                profile_instruction = ""
                if farmer_profile:
                    profile_instruction = (
                        "\n\nThe user is a farmer. Use their profile information from the context "
                        "to personalize your answer. Prioritize schemes that match their state, "
                        "crop type, land size, and income level. Mention specific eligibility "
                        "criteria that apply to them."
                    )

                system_prompt = (
                    "You are SaarthiAI, a friendly and knowledgeable assistant helping Indian "
                    "farmers and citizens discover government schemes they are eligible for. "
                    "Answer in clear, simple language that a rural farmer can understand. "
                    "Structure your response with: 1) Direct answer to their question, "
                    "2) Key eligibility points, 3) How to apply (if known), 4) Important documents needed. "
                    "Use the scheme data and web search results provided in the context. "
                    "If the context is insufficient, say so honestly. "
                    "Do NOT make up scheme details or eligibility criteria."
                    f"{profile_instruction}"
                )
                user_prompt = (
                    f"Context:\n{context}\n\n"
                    f"User question: {question}\n\n"
                    "Provide a helpful, accurate, and personalized answer."
                )
                response = client.chat.completions.create(
                    model=settings.azure_openai_deployment,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_completion_tokens=600,
                )
                answer = response.choices[0].message.content.strip()
                if len(_answer_cache) >= _ANSWER_CACHE_MAX:
                    oldest = min(_answer_cache, key=lambda k: _answer_cache[k]["ts"])
                    del _answer_cache[oldest]
                _answer_cache[cache_key] = {"answer": answer, "ts": time.time()}
                return answer
            except Exception as e:
                logger.warning(f"Azure OpenAI call failed, using fallback: {e}")

        return (
            f"यहाँ आपके सवाल के आधार पर कुछ जानकारी है:\n\n"
            f"{context}\n\n"
            f"यह जानकारी सरकारी स्रोतों के आधार पर है।"
        )


rag_engine = RAGEngine()
