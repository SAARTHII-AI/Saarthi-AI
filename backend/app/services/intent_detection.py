def detect_intent(query: str) -> str:
    query = query.lower()
    
    # rule-based keyword detection
    eligibility_keywords = ["patrata", "eligibility", "koun", "who can", "eligible", "arugu", "yogya", "पात्रता", "तகுதி"]
    document_keywords = ["documents", "kagaz", "paper", "required", "dastavez", "दस्तावेज़", "ஆவணங்கள்"]
    benefits_keywords = ["benefits", "fayde", "kya milega", "labh", "what will i get", "लाभ", "நன்மைகள்"]
    scheme_keywords = ["yojana", "scheme", "plan", "yojna", "thittam", "योजना", "திட்டம்"]
    
    if any(k in query for k in document_keywords):
        return "document_requirements"
    
    if any(k in query for k in eligibility_keywords):
        return "eligibility_check"
        
    if any(k in query for k in benefits_keywords):
        return "benefits_query"
        
    if any(k in query for k in scheme_keywords):
        return "scheme_search"
        
    return "general_information"
