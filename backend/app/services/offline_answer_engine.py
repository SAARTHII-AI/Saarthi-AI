from typing import List, Dict, Any, Optional


def generate_offline_answer(
    schemes: List[Dict[str, Any]],
    question: str,
    farmer_profile: Optional[Dict[str, Any]] = None,
    language: str = "en",
) -> str:
    if not schemes:
        return _no_scheme_found(language)

    top = schemes[:3]
    parts = []

    if language == "hi":
        parts.append("आपके सवाल के आधार पर यहाँ कुछ सरकारी योजनाओं की जानकारी है:\n")
    else:
        parts.append("Based on your question, here are some relevant government schemes:\n")

    for i, s in enumerate(top, 1):
        parts.append(_format_scheme(s, i, language))

    if farmer_profile and farmer_profile.get("state"):
        state = farmer_profile["state"]
        state_schemes = [s for s in top if s.get("state") and s["state"].lower() == state.lower()]
        if state_schemes:
            if language == "hi":
                parts.append(f"\n📍 {state} के लिए विशेष योजनाएं ऊपर चिन्हित हैं।")
            else:
                parts.append(f"\n📍 Schemes specific to {state} are marked above.")

    if language == "hi":
        parts.append("\nअधिक जानकारी के लिए नजदीकी CSC केंद्र या ग्राम पंचायत से संपर्क करें।")
    else:
        parts.append("\nFor more information, visit your nearest CSC center or Gram Panchayat office.")

    return "\n".join(parts)


def _format_scheme(s: Dict[str, Any], idx: int, lang: str) -> str:
    lines = []
    name = s.get("name", "Unknown Scheme")
    scheme_type = s.get("type", "")
    state = s.get("state", "")
    badge = ""
    if scheme_type == "central":
        badge = " [Central/केंद्र]"
    elif scheme_type == "state" and state:
        badge = f" [{state}]"

    lines.append(f"\n{'─' * 30}")
    lines.append(f"📋 {idx}. {name}{badge}")

    if s.get("description"):
        desc = s["description"]
        if len(desc) > 200:
            desc = desc[:197] + "..."
        lines.append(f"   {desc}")

    if s.get("benefits"):
        if lang == "hi":
            lines.append(f"   💰 लाभ: {s['benefits']}")
        else:
            lines.append(f"   💰 Benefits: {s['benefits']}")

    if s.get("eligibility"):
        if lang == "hi":
            lines.append(f"   ✅ पात्रता: {s['eligibility']}")
        else:
            lines.append(f"   ✅ Eligibility: {s['eligibility']}")

    docs = s.get("documents") or []
    if docs:
        doc_str = ", ".join(docs[:5])
        if len(docs) > 5:
            doc_str += f" (+{len(docs) - 5} more)"
        if lang == "hi":
            lines.append(f"   📄 दस्तावेज़: {doc_str}")
        else:
            lines.append(f"   📄 Documents: {doc_str}")

    if s.get("helpline"):
        if lang == "hi":
            lines.append(f"   📞 हेल्पलाइन: {s['helpline']}")
        else:
            lines.append(f"   📞 Helpline: {s['helpline']}")

    app_url = s.get("application_url") or ""
    if app_url and app_url.startswith("http"):
        if lang == "hi":
            lines.append(f"   🔗 आवेदन: {app_url}")
        else:
            lines.append(f"   🔗 Apply: {app_url}")

    return "\n".join(lines)


def _no_scheme_found(lang: str) -> str:
    if lang == "hi":
        return (
            "मुझे आपके सवाल से संबंधित कोई विशेष योजना नहीं मिली। "
            "कृपया अपना सवाल थोड़ा विस्तार से पूछें, "
            "या नजदीकी CSC केंद्र से संपर्क करें।\n\n"
            "कुछ सामान्य योजनाएं जो आपके काम आ सकती हैं:\n"
            "• PM-KISAN (₹6,000/वर्ष) - pmkisan.gov.in\n"
            "• Ayushman Bharat (₹5 लाख स्वास्थ्य बीमा) - pmjay.gov.in\n"
            "• PM Awas Yojana (आवास) - pmayg.nic.in"
        )
    return (
        "I couldn't find a specific scheme matching your question. "
        "Please try asking in more detail, "
        "or visit your nearest CSC center for help.\n\n"
        "Some common schemes that may help you:\n"
        "• PM-KISAN (₹6,000/year) - pmkisan.gov.in\n"
        "• Ayushman Bharat (₹5 lakh health cover) - pmjay.gov.in\n"
        "• PM Awas Yojana (Housing) - pmayg.nic.in"
    )
