import logging
import hashlib
import time
from typing import Optional, Dict, Any
from app.services.scheme_loader import load_schemes
from app.services.offline_answer_engine import generate_offline_answer
from app.config import settings

logger = logging.getLogger(__name__)

_answer_cache = {}
_ANSWER_CACHE_MAX = 200
_ANSWER_CACHE_TTL = 1800

LANG_NAMES = {
    "hi": "Hindi", "en": "English", "bn": "Bengali", "te": "Telugu",
    "mr": "Marathi", "ta": "Tamil", "gu": "Gujarati", "kn": "Kannada",
    "ml": "Malayalam", "pa": "Punjabi", "or": "Odia",
}


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


SYSTEM_PROMPT_TEMPLATE = """You are **SaarthiAI** — a warm, expert government-scheme advisor built for Indian farmers and citizens. Your goal is to give **complete, actionable, and personalized** answers that a rural farmer or first-generation beneficiary can immediately use.

## RESPONSE LANGUAGE
{lang_instruction}

## RESPONSE FORMAT (always follow this structure)
Use **bold headings**, numbered lists, and bullet points. Structure EVERY answer like this:

**[Scheme Name]** — one-line summary of what it does.

1) **आपके लिए क्या फायदा / Benefits for You**
   - List 3-5 concrete benefits with ₹ amounts, percentages, or specifics
   - Mention interest rate subsidies, insurance coverage, or cash transfers with exact figures
   - Highlight any special advantage for the user based on their profile

2) **मुख्य पात्रता / Eligibility**
   - List who qualifies (farmer type, land size, income ceiling, age, gender)
   - Directly tell the user whether they likely qualify based on their profile
   - Mention if sharecroppers, tenant farmers, or landless laborers are included

3) **आवेदन कैसे करें / How to Apply**
   - Step-by-step (visit bank/CSC/portal, fill form, submit documents)
   - Mention specific portals with URLs
   - Mention if PM-KISAN beneficiaries get automatic benefits

4) **जरूरी दस्तावेज़ / Required Documents**
   - Bulleted list of every document needed (Aadhaar, land papers, bank passbook, photos, PAN if needed)

5) **हेल्पलाइन / Helpline**
   - Phone numbers and toll-free numbers
   - Official website URLs

6) **Follow-up prompt**: End with "अगर आप बताएं कि आपका राज्य, जमीन कितनी है, और कौन सी फसल उगाते हैं, तो मैं और भी योजनाएं बता सकता हूँ।" (or equivalent in the response language)

## KEY RULES
- **NEVER** say "I don't have information" if the context contains scheme data — use it fully.
- **NEVER** give a short 2-3 line answer. Always give a comprehensive, detailed response.
- Include ₹ amounts, percentages, exact figures from the scheme data.
- If multiple schemes are relevant, cover the top 2-3 in detail.
- Personalize based on farmer profile (state, crop, land size, income).
- Use emojis sparingly: 💰 for money, ✅ for eligibility, 📄 for documents, 📞 for helpline, 🔗 for links.
- When web search results provide additional details, incorporate them naturally.
- For state-specific schemes, highlight that the scheme is specific to their state.
- Do NOT fabricate scheme details, eligibility criteria, ₹ amounts, or helpline numbers that are not in the context.
- If the context does not have specific details, say so honestly — do not invent information.
- Only include URLs and helpline numbers that appear in the provided context.
{profile_instruction}"""

PROFILE_INSTRUCTION = """
## USER PROFILE
The user is a farmer/citizen. Their profile details are in the context below. Use this to:
- Prioritize schemes matching their state, crop, land size, and income
- Tell them directly "आप इस योजना के लिए पात्र हैं" if they likely qualify
- Suggest additional schemes based on their profile
- Mention state-specific benefits if their state matches any scheme"""


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
            benefits_lower = scheme.get('benefits', '').lower()
            state_lower = (scheme.get('state') or '').lower()

            score = 0

            for word in query_words:
                if len(word) < 3:
                    continue
                if word in name_lower:
                    score += 3
                elif word in target_lower:
                    score += 2
                elif word in desc_lower or word in elig_lower or word in benefits_lower:
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
                if s.get('benefits'):
                    lines.append(f"  Benefits: {s['benefits']}")
                if s.get('target_group'):
                    lines.append(f"  Target Group: {s['target_group']}")
                if s.get('documents'):
                    lines.append(f"  Documents Required: {', '.join(s['documents'][:6])}")
                if s.get('helpline'):
                    lines.append(f"  Helpline: {s['helpline']}")
                if s.get('application_url') and s['application_url'].startswith('http'):
                    lines.append(f"  Apply: {s['application_url']}")
                if s.get('documents_links'):
                    lines.append(f"  Official Links: {', '.join(s['documents_links'][:3])}")
                scheme_texts.append("\n".join(lines))
            parts.append("=== GOVERNMENT SCHEMES ===\n" + "\n\n".join(scheme_texts))

        if web_snippets:
            parts.append("=== WEB SEARCH RESULTS ===\n" + "\n".join(f"- {s}" for s in web_snippets))

        return "\n\n".join(parts)

    def _cache_key(self, context: str, question: str, profile: dict = None) -> str:
        raw = f"{question}|{context[:500]}|{str(sorted((profile or {}).items()))}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _build_system_prompt(self, language: str = "en", farmer_profile: dict = None) -> str:
        lang_name = LANG_NAMES.get(language, "English")

        if language == "hi":
            lang_instruction = (
                "You MUST respond entirely in **Hindi (Devanagari script)**. "
                "Use simple Hindi that a rural farmer understands. "
                "You may use English for scheme names, URLs, and technical terms. "
                "Example: 'PM-KISAN' stays in English but explain in Hindi."
            )
        elif language == "en":
            lang_instruction = "Respond in clear, simple English."
        else:
            lang_instruction = (
                f"You MUST respond entirely in **{lang_name}** using the native script of that language. "
                f"Use simple {lang_name} that a common person understands. "
                "You may keep scheme names, URLs, and numbers in English/Latin script."
            )

        profile_instruction = PROFILE_INSTRUCTION if farmer_profile else ""

        return SYSTEM_PROMPT_TEMPLATE.format(
            lang_instruction=lang_instruction,
            profile_instruction=profile_instruction,
        )

    def generate_answer(self, context: str, question: str, farmer_profile: dict = None, language: str = "en", matched_schemes: list = None) -> str:
        if not context:
            return generate_offline_answer([], question, farmer_profile, language)

        cache_key = self._cache_key(context, question, farmer_profile)
        cached = _answer_cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < _ANSWER_CACHE_TTL:
            logger.info("Returning cached answer")
            return cached["answer"]

        client = _build_azure_client()
        if client:
            try:
                system_prompt = self._build_system_prompt(language, farmer_profile)

                user_prompt = (
                    f"Context:\n{context}\n\n"
                    f"User question: {question}\n\n"
                    "Give a comprehensive, detailed, and personalized answer using ALL the scheme data from the context. "
                    "Include specific ₹ amounts, eligibility criteria, application steps, required documents, and helpline numbers. "
                    "Do NOT give a short answer. Cover every relevant detail."
                )
                response = client.chat.completions.create(
                    model=settings.azure_openai_deployment,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_completion_tokens=1500,
                )
                answer = response.choices[0].message.content.strip()
                if len(_answer_cache) >= _ANSWER_CACHE_MAX:
                    oldest = min(_answer_cache, key=lambda k: _answer_cache[k]["ts"])
                    del _answer_cache[oldest]
                _answer_cache[cache_key] = {"answer": answer, "ts": time.time()}
                return answer
            except Exception as e:
                logger.warning(f"Azure OpenAI call failed, using offline engine: {e}")

        answer = generate_offline_answer(
            matched_schemes or [],
            question,
            farmer_profile,
            language,
        )

        if len(_answer_cache) >= _ANSWER_CACHE_MAX:
            oldest = min(_answer_cache, key=lambda k: _answer_cache[k]["ts"])
            del _answer_cache[oldest]
        _answer_cache[cache_key] = {"answer": answer, "ts": time.time()}
        return answer


rag_engine = RAGEngine()
