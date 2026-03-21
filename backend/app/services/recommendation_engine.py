from typing import Dict, Any, List
from app.services.scheme_loader import load_schemes

def recommend_schemes(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recommend schemes based on:
    state, occupation, income, age, category, scheme_type
    """
    age = user_data.get("age")
    income = user_data.get("income")
    occupation = user_data.get("occupation", "").lower() if user_data.get("occupation") else ""
    user_state = user_data.get("state")
    scheme_type = user_data.get("scheme_type")

    all_schemes = load_schemes(scheme_type=scheme_type, state=user_state)

    recommendations = []

    for scheme in all_schemes:
        score = 0
        target = scheme.get("target_group", "").lower()

        if "farmer" in occupation or "kisan" in occupation:
            if "farmer" in target or "kisan" in scheme.get("name", "").lower():
                score += 3

        if income is not None and income < 250000:
            if any(kw in target for kw in ["low-income", "bpl", "poor", "ews"]):
                score += 2
            if "insurance" in scheme.get("description", "").lower() or "health" in scheme.get("description", "").lower():
                score += 1

        if "student" in occupation:
            if "student" in target or "education" in scheme.get("description", "").lower() or "scholarship" in scheme.get("description", "").lower():
                score += 3

        if occupation in ["startup", "business", "entrepreneur"]:
            if any(kw in target for kw in ["entrepreneur", "business", "startup", "small business"]):
                score += 3

        if "vendor" in occupation:
            if "vendor" in target:
                score += 3

        if age and age < 35:
            if "youth" in target or "skill" in scheme.get("description", "").lower():
                score += 1

        if age and age >= 60:
            if "elderly" in target or "pension" in scheme.get("description", "").lower():
                score += 2

        if "women" in target or "girl" in target:
            category = user_data.get("category", "").lower() if user_data.get("category") else ""
            if "women" in category or "female" in category:
                score += 2

        if user_state and scheme.get("state") and scheme["state"].lower() == user_state.lower():
            score += 1

        if score > 0:
            recommendations.append((score, {
                "name": scheme["name"],
                "description": scheme.get("description", ""),
                "type": scheme.get("type"),
                "state": scheme.get("state"),
                "documents_links": scheme.get("documents_links")
            }))

    recommendations.sort(key=lambda x: x[0], reverse=True)

    if not recommendations:
        fallback = next((s for s in all_schemes if s["name"] == "Ayushman Bharat"), None)
        if not fallback and all_schemes:
            fallback = all_schemes[0]
        if fallback:
            return [{
                "name": fallback["name"],
                "description": fallback.get("description", ""),
                "type": fallback.get("type"),
                "state": fallback.get("state"),
                "documents_links": fallback.get("documents_links")
            }]
        return []

    return [r[1] for r in recommendations[:5]]
