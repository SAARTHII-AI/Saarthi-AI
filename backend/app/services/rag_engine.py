import logging
import hashlib
import time
from typing import Optional, Dict, Any, List
from app.services.scheme_loader import load_schemes
from app.services.offline_answer_engine import generate_offline_answer
from app.config import settings

logger = logging.getLogger(__name__)

_answer_cache = {}
_ANSWER_CACHE_MAX = 500
_ANSWER_CACHE_TTL = 3600

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


SYSTEM_PROMPT_TEMPLATE = """You are **SaarthiAI** — a warm, patient government-scheme advisor who helps Indian farmers and citizens apply for schemes **step by step** through voice conversation. Think of yourself as a helpful village-level guide sitting next to the farmer.

## YOUR ROLE
- You guide farmers through the ENTIRE application process — from understanding the scheme to actually submitting their application.
- You speak in simple, everyday language a rural farmer can understand.
- You remember what was discussed earlier in the conversation and build on it.
- You proactively ask what step they need help with next.
- You never overwhelm with too much information at once — break it into digestible steps.

## RESPONSE LANGUAGE
{lang_instruction}

## CONVERSATION AWARENESS
- If this is the FIRST message about a scheme, give a warm overview with key benefits and ask if they want to apply.
- If they say YES or ask HOW TO APPLY, walk them through Step 1 first and ask if they are ready for the next step.
- If they ask about DOCUMENTS, list exactly what they need and explain where to get each one.
- If they ask about ELIGIBILITY, check their profile and tell them clearly if they qualify.
- If they are continuing a conversation, pick up from where you left off — do NOT repeat information already given.
- If they ask a follow-up like "what next?" or "aage kya karna hai?", give them the NEXT step.

## RESPONSE FORMAT
For a FIRST question about a scheme, structure your answer like this:

**[Scheme Name]** — one-line summary

1) **💰 Benefits** — 3-5 concrete benefits with ₹ amounts
2) **✅ Eligibility** — who qualifies (directly tell farmer if they qualify based on profile)
3) **📋 How to Apply** — step-by-step (number each step clearly)
4) **📄 Required Documents** — bulleted list of every document needed
5) **📞 Helpline** — phone numbers and official website URLs

End with a friendly follow-up like: "Kya aap iske liye apply karna chahte hain? Main aapko step-by-step bata sakta hoon." (in the response language)

For FOLLOW-UP messages in a conversation:
- Give ONLY the information they asked about
- Keep it concise and actionable
- Always end with "Agle step ke liye poochiye" or equivalent prompt in the response language

## KEY RULES
- **NEVER** say "I don't have information" if the context contains scheme data — use it fully.
- Include ₹ amounts, percentages, exact figures from the scheme data.
- If multiple schemes are relevant, mention top 2-3 but focus on the most relevant one.
- Personalize based on farmer profile (state, crop, land size, income).
- Use emojis sparingly: 💰 for money, ✅ for eligibility, 📄 for documents, 📞 for helpline, 🔗 for links.
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

MAX_HISTORY_TURNS = 6


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

    def _cache_key(self, context: str, question: str, profile: dict = None, history_summary: str = "") -> str:
        raw = f"{question}|{context[:500]}|{str(sorted((profile or {}).items()))}|{history_summary}"
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

    def _build_conversation_messages(self, system_prompt: str, context: str, question: str, conversation_history: list = None) -> list:
        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            recent = conversation_history[-MAX_HISTORY_TURNS * 2:]
            for msg in recent:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ("user", "assistant") and content:
                    if role == "assistant" and len(content) > 800:
                        content = content[:800] + "..."
                    messages.append({"role": role, "content": content})

        user_prompt = (
            f"Context:\n{context}\n\n"
            f"User question: {question}\n\n"
            "Give a comprehensive, personalized answer using the scheme data from the context. "
            "Include specific ₹ amounts, eligibility criteria, application steps, required documents, and helpline numbers. "
            "If this is a follow-up question in a conversation, build on what was already discussed — do not repeat."
        )
        messages.append({"role": "user", "content": user_prompt})

        return messages

    def generate_answer(self, context: str, question: str, farmer_profile: dict = None, language: str = "en", matched_schemes: list = None, conversation_history: list = None) -> str:
        if not context:
            return generate_offline_answer([], question, farmer_profile, language)

        history_summary = ""
        if conversation_history:
            history_summary = "|".join(m.get("content", "")[:50] for m in conversation_history[-4:])

        cache_key = self._cache_key(context, question, farmer_profile, history_summary)
        cached = _answer_cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < _ANSWER_CACHE_TTL:
            logger.info("Returning cached answer")
            return cached["answer"]

        client = _build_azure_client()
        if client:
            try:
                system_prompt = self._build_system_prompt(language, farmer_profile)
                messages = self._build_conversation_messages(
                    system_prompt, context, question, conversation_history
                )

                response = client.chat.completions.create(
                    model=settings.azure_openai_deployment,
                    messages=messages,
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
