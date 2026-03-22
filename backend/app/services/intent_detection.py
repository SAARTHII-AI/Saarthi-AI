import re

def detect_intent(query: str) -> str:
    query = query.lower()

    price_keywords = ["mandi", "market price", "crop price", "bhav", "daam", "rate today",
                       "price today", "selling price", "mandi price", "mandi rate",
                       "aaj ka bhav", "aaj ka daam", "bazaar", "बाजार भाव", "मंडी"]
    helpline_keywords = ["helpline", "call", "phone", "number", "contact", "complaint",
                          "grievance", "shikayat", "helpdesk", "toll free"]
    eligibility_keywords = ["patrata", "eligibility", "koun", "who can", "eligible", "arugu", "yogya", "पात्रता", "தகுதி"]
    document_keywords = ["documents", "kagaz", "paper", "required", "dastavez", "दस्तावेज़", "ஆவணங்கள்"]
    benefits_keywords = ["benefits", "fayde", "kya milega", "labh", "what will i get", "लाभ", "நன்மைகள்"]
    scheme_keywords = ["yojana", "scheme", "plan", "yojna", "thittam", "योजना", "திட்டம்"]
    apply_keywords = ["apply", "register", "registration", "avedan", "aavedan", "how to apply",
                       "apply online", "sign up", "enroll", "आवेदन"]

    if any(k in query for k in price_keywords):
        return "price_query"

    if any(k in query for k in helpline_keywords):
        return "helpline_query"

    if any(k in query for k in document_keywords):
        return "document_requirements"

    if any(k in query for k in apply_keywords):
        return "application_process"

    if any(k in query for k in eligibility_keywords):
        return "eligibility_check"

    if any(k in query for k in benefits_keywords):
        return "benefits_query"

    if any(k in query for k in scheme_keywords):
        return "scheme_search"

    return "general_information"
