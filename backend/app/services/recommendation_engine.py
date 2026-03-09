from typing import Dict, Any, List

def recommend_schemes(user_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Recommend schemes based on:
    state, occupation, income, age, category
    """
    recommendations = []
    
    age = user_data.get("age")
    income = user_data.get("income")
    occupation = user_data.get("occupation", "").lower() if user_data.get("occupation") else ""
    
    # Simple rule-based logic for MVP
    if "farmer" in occupation or "kisan" in occupation:
        recommendations.append({
            "name": "PM-KISAN",
            "description": "Financial support for farmers. ₹6000 per year."
        })
        
    if income is not None and income < 250000:
        recommendations.append({
            "name": "Ayushman Bharat",
            "description": "Free health insurance cover of up to ₹5 lakhs per family per year."
        })
        recommendations.append({
            "name": "PM Awas Yojana",
            "description": "Affordable housing scheme for lower income groups."
        })
        
    if "student" in occupation:
        recommendations.append({
            "name": "Digital India",
            "description": "Digital empowerment initiatives often providing skill training and scholarships."
        })
        
    if occupation in ["startup", "business", "entrepreneur"]:
        recommendations.append({
            "name": "Startup India",
            "description": "Benefits for registered startups including tax exemptions."
        })
        recommendations.append({
            "name": "Mudra Loan",
            "description": "Loans up to ₹10 Lakhs for non-corporate, non-farm small/micro enterprises."
        })
        
    if age and age < 35:
        recommendations.append({
            "name": "PM Kaushal Vikas Yojana",
            "description": "Skill certification scheme that aims to train Indian youth."
        })
        
    # Default recommendation if none match
    if not recommendations:
        recommendations.append({
            "name": "Ayushman Bharat",
            "description": "Free health insurance cover of up to ₹5 lakhs per family per year."
        })
        
    # Return top 3
    return recommendations[:3]
