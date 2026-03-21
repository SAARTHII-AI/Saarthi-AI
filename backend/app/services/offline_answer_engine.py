from typing import List, Dict, Any, Optional

LANG_LABELS = {
    "hi": {
        "intro": "आपके सवाल के आधार पर यहाँ सरकारी योजनाओं की **विस्तृत जानकारी** है:",
        "benefits_heading": "आपके लिए क्या फायदा",
        "eligibility_heading": "मुख्य पात्रता (Eligibility)",
        "how_to_apply": "आवेदन कैसे करें",
        "documents_heading": "जरूरी दस्तावेज़",
        "helpline_heading": "हेल्पलाइन",
        "apply_heading": "आवेदन लिंक",
        "state_note": "📍 {state} के लिए विशेष योजनाएं ऊपर चिन्हित हैं।",
        "footer": "अगर आप बताएं कि आपका **राज्य**, **कितनी जमीन** है, और **कौन सी फसल** उगाते हैं — तो मैं आपको और भी योजनाएं बता सकता हूँ।\n\nअधिक जानकारी के लिए नजदीकी **CSC केंद्र** या **ग्राम पंचायत** से संपर्क करें।",
        "central": "केंद्र सरकार",
        "state_label": "राज्य",
        "no_match": "मुझे आपके सवाल से संबंधित कोई विशेष योजना नहीं मिली।\n\nकृपया अपना सवाल थोड़ा विस्तार से पूछें, या नजदीकी CSC केंद्र से संपर्क करें।",
        "common_schemes": "कुछ **सामान्य योजनाएं** जो आपके काम आ सकती हैं:",
        "apply_steps": "अपने **नजदीकी बैंक** या **CSC केंद्र** में जाकर आवेदन करें।",
    },
    "en": {
        "intro": "Based on your question, here is **detailed information** about relevant government schemes:",
        "benefits_heading": "Benefits for You",
        "eligibility_heading": "Eligibility",
        "how_to_apply": "How to Apply",
        "documents_heading": "Required Documents",
        "helpline_heading": "Helpline",
        "apply_heading": "Apply Link",
        "state_note": "📍 Schemes specific to {state} are marked above.",
        "footer": "If you share your **state**, **land size**, and **crop type**, I can recommend even more schemes for you.\n\nFor more information, visit your nearest **CSC center** or **Gram Panchayat** office.",
        "central": "Central Government",
        "state_label": "State",
        "no_match": "I couldn't find a specific scheme matching your question.\n\nPlease try asking in more detail, or visit your nearest CSC center for help.",
        "common_schemes": "Some **common schemes** that may help you:",
        "apply_steps": "Visit your **nearest bank** or **CSC center** to apply.",
    },
    "bn": {
        "intro": "আপনার প্রশ্নের ভিত্তিতে এখানে সরকারি প্রকল্পের **বিস্তারিত তথ্য**:",
        "benefits_heading": "আপনার জন্য সুবিধা",
        "eligibility_heading": "যোগ্যতা",
        "how_to_apply": "আবেদন কীভাবে করবেন",
        "documents_heading": "প্রয়োজনীয় নথিপত্র",
        "helpline_heading": "হেল্পলাইন",
        "apply_heading": "আবেদন লিংক",
        "state_note": "📍 {state}-এর জন্য বিশেষ প্রকল্প উপরে চিহ্নিত।",
        "footer": "আপনার **রাজ্য**, **জমির পরিমাণ** এবং **ফসল** জানালে আরও প্রকল্প সুপারিশ করতে পারব।\n\nআরও তথ্যের জন্য নিকটতম **CSC কেন্দ্র** বা **গ্রাম পঞ্চায়েত** এ যোগাযোগ করুন।",
        "central": "কেন্দ্র সরকার",
        "state_label": "রাজ্য",
        "no_match": "আপনার প্রশ্নের সাথে সম্পর্কিত কোনো নির্দিষ্ট প্রকল্প পাওয়া যায়নি।",
        "common_schemes": "কিছু **সাধারণ প্রকল্প** যা আপনার কাজে আসতে পারে:",
        "apply_steps": "আপনার **নিকটতম ব্যাংক** বা **CSC কেন্দ্রে** গিয়ে আবেদন করুন।",
    },
    "te": {
        "intro": "మీ ప్రశ్న ఆధారంగా ఇక్కడ ప్రభుత్వ పథకాల **వివరమైన సమాచారం**:",
        "benefits_heading": "మీ కోసం ప్రయోజనాలు",
        "eligibility_heading": "అర్హత",
        "how_to_apply": "దరఖాస్తు ఎలా చేయాలి",
        "documents_heading": "అవసరమైన పత్రాలు",
        "helpline_heading": "హెల్ప్‌లైన్",
        "apply_heading": "దరఖాస్తు లింక్",
        "state_note": "📍 {state} కోసం ప్రత్యేక పథకాలు పైన గుర్తించబడ్డాయి.",
        "footer": "మీ **రాష్ట్రం**, **భూమి విస్తీర్ణం** మరియు **పంట** తెలిపితే మరిన్ని పథకాలు సూచిస్తాను.\n\nమరిన్ని వివరాల కోసం సమీపంలోని **CSC కేంద్రం** లేదా **గ్రామ పంచాయతీ**ని సంప్రదించండి.",
        "central": "కేంద్ర ప్రభుత్వం",
        "state_label": "రాష్ట్రం",
        "no_match": "మీ ప్రశ్నకు సంబంధించిన నిర్దిష్ట పథకం కనుగొనబడలేదు.",
        "common_schemes": "మీకు ఉపయోగపడే కొన్ని **సాధారణ పథకాలు**:",
        "apply_steps": "మీ **సమీపంలోని బ్యాంకు** లేదా **CSC కేంద్రంలో** దరఖాస్తు చేయండి.",
    },
    "mr": {
        "intro": "तुमच्या प्रश्नावर आधारित सरकारी योजनांची **तपशीलवार माहिती**:",
        "benefits_heading": "तुमच्यासाठी काय फायदा",
        "eligibility_heading": "पात्रता",
        "how_to_apply": "अर्ज कसा करायचा",
        "documents_heading": "आवश्यक कागदपत्रे",
        "helpline_heading": "हेल्पलाइन",
        "apply_heading": "अर्ज लिंक",
        "state_note": "📍 {state} साठी विशेष योजना वर चिन्हांकित आहेत.",
        "footer": "तुमचे **राज्य**, **जमिनीचे क्षेत्र** आणि **पीक** सांगा, मग मी आणखी योजना सुचवू शकतो.\n\nअधिक माहितीसाठी जवळच्या **CSC केंद्र** किंवा **ग्रामपंचायत** कार्यालयाशी संपर्क करा.",
        "central": "केंद्र सरकार",
        "state_label": "राज्य",
        "no_match": "तुमच्या प्रश्नाशी संबंधित विशिष्ट योजना सापडली नाही.",
        "common_schemes": "तुमच्या कामाच्या काही **सामान्य योजना**:",
        "apply_steps": "तुमच्या **जवळच्या बँक** किंवा **CSC केंद्रात** जाऊन अर्ज करा.",
    },
    "ta": {
        "intro": "உங்கள் கேள்வியின் அடிப்படையில் அரசு திட்டங்களின் **விரிவான தகவல்**:",
        "benefits_heading": "உங்களுக்கான நன்மைகள்",
        "eligibility_heading": "தகுதி",
        "how_to_apply": "விண்ணப்பிப்பது எப்படி",
        "documents_heading": "தேவையான ஆவணங்கள்",
        "helpline_heading": "ஹெல்ப்லைன்",
        "apply_heading": "விண்ணப்ப இணைப்பு",
        "state_note": "📍 {state} க்கான சிறப்பு திட்டங்கள் மேலே குறிக்கப்பட்டுள்ளன.",
        "footer": "உங்கள் **மாநிலம்**, **நிலப் பரப்பு** மற்றும் **பயிர்** தெரிவிக்கவும், நான் மேலும் திட்டங்களை பரிந்துரைக்க முடியும்.\n\nமேலும் விவரங்களுக்கு அருகிலுள்ள **CSC மையம்** அல்லது **கிராம பஞ்சாயத்**தை தொடர்பு கொள்ளுங்கள்.",
        "central": "மத்திய அரசு",
        "state_label": "மாநிலம்",
        "no_match": "உங்கள் கேள்விக்கு பொருத்தமான திட்டம் கிடைக்கவில்லை.",
        "common_schemes": "உங்களுக்கு உதவக்கூடிய சில **பொதுவான திட்டங்கள்**:",
        "apply_steps": "உங்கள் **அருகிலுள்ள வங்கி** அல்லது **CSC மையத்தில்** விண்ணப்பிக்கவும்.",
    },
    "gu": {
        "intro": "તમારા પ્રશ્ન આધારે સરકારી યોજનાઓની **વિગતવાર માહિતી**:",
        "benefits_heading": "તમારા માટે ફાયદા",
        "eligibility_heading": "પાત્રતા",
        "how_to_apply": "અરજી કેવી રીતે કરવી",
        "documents_heading": "જરૂરી દસ્તાવેજો",
        "helpline_heading": "હેલ્પલાઇન",
        "apply_heading": "અરજી લિંક",
        "state_note": "📍 {state} માટે વિશેષ યોજનાઓ ઉપર ચિહ્નિત છે.",
        "footer": "તમારું **રાજ્ય**, **જમીનનું ક્ષેત્રફળ** અને **પાક** જણાવો, હું વધુ યોજનાઓ સૂચવી શકું.\n\nવધુ માહિતી માટે નજીકના **CSC કેન્દ્ર** અથવા **ગ્રામ પંચાયત** નો સંપર્ક કરો.",
        "central": "કેન્દ્ર સરકાર",
        "state_label": "રાજ્ય",
        "no_match": "તમારા પ્રશ્ન સાથે સંબંધિત ચોક્કસ યોજના મળી નથી.",
        "common_schemes": "તમારા કામની કેટલીક **સામાન્ય યોજનાઓ**:",
        "apply_steps": "તમારી **નજીકની બેંક** અથવા **CSC કેન્દ્રમાં** જઈને અરજી કરો.",
    },
    "kn": {
        "intro": "ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಆಧಾರದ ಮೇಲೆ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ **ವಿವರವಾದ ಮಾಹಿತಿ**:",
        "benefits_heading": "ನಿಮಗಾಗಿ ಪ್ರಯೋಜನಗಳು",
        "eligibility_heading": "ಅರ್ಹತೆ",
        "how_to_apply": "ಅರ್ಜಿ ಹೇಗೆ ಸಲ್ಲಿಸುವುದು",
        "documents_heading": "ಅಗತ್ಯ ದಾಖಲೆಗಳು",
        "helpline_heading": "ಹೆಲ್ಪ್‌ಲೈನ್",
        "apply_heading": "ಅರ್ಜಿ ಲಿಂಕ್",
        "state_note": "📍 {state} ಗಾಗಿ ವಿಶೇಷ ಯೋಜನೆಗಳು ಮೇಲೆ ಗುರುತಿಸಲಾಗಿದೆ.",
        "footer": "ನಿಮ್ಮ **ರಾಜ್ಯ**, **ಭೂಮಿಯ ವಿಸ್ತೀರ್ಣ** ಮತ್ತು **ಬೆಳೆ** ತಿಳಿಸಿ, ನಾನು ಹೆಚ್ಚಿನ ಯೋಜನೆಗಳನ್ನು ಸೂಚಿಸಬಹುದು.\n\nಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ಹತ್ತಿರದ **CSC ಕೇಂದ್ರ** ಅಥವಾ **ಗ್ರಾಮ ಪಂಚಾಯತ್** ಸಂಪರ್ಕಿಸಿ.",
        "central": "ಕೇಂದ್ರ ಸರ್ಕಾರ",
        "state_label": "ರಾಜ್ಯ",
        "no_match": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ನಿರ್ದಿಷ್ಟ ಯೋಜನೆ ಕಂಡುಬಂದಿಲ್ಲ.",
        "common_schemes": "ನಿಮಗೆ ಸಹಾಯಕವಾಗಬಹುದಾದ ಕೆಲವು **ಸಾಮಾನ್ಯ ಯೋಜನೆಗಳು**:",
        "apply_steps": "ನಿಮ್ಮ **ಹತ್ತಿರದ ಬ್ಯಾಂಕ್** ಅಥವಾ **CSC ಕೇಂದ್ರದಲ್ಲಿ** ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.",
    },
    "ml": {
        "intro": "നിങ്ങളുടെ ചോദ്യത്തിന്റെ അടിസ്ഥാനത്തിൽ സർക്കാർ പദ്ധതികളുടെ **വിശദമായ വിവരങ്ങൾ**:",
        "benefits_heading": "നിങ്ങൾക്കുള്ള ആനുകൂല്യങ്ങൾ",
        "eligibility_heading": "യോഗ്യത",
        "how_to_apply": "അപേക്ഷിക്കേണ്ടത് എങ്ങനെ",
        "documents_heading": "ആവശ്യമായ രേഖകൾ",
        "helpline_heading": "ഹെൽപ്‌ലൈൻ",
        "apply_heading": "അപേക്ഷ ലിങ്ക്",
        "state_note": "📍 {state} ന്റെ പ്രത്യേക പദ്ധതികൾ മുകളിൽ അടയാളപ്പെടുത്തിയിട്ടുണ്ട്.",
        "footer": "നിങ്ങളുടെ **സംസ്ഥാനം**, **ഭൂമിയുടെ വിസ്തൃതി**, **വിള** എന്നിവ അറിയിച്ചാൽ കൂടുതൽ പദ്ധതികൾ നിർദ്ദേശിക്കാം.\n\nകൂടുതൽ വിവരങ്ങൾക്ക് അടുത്തുള്ള **CSC കേന്ദ്രം** അല്ലെങ്കിൽ **ഗ്രാമ പഞ്ചായത്ത്** സന്ദർശിക്കുക.",
        "central": "കേന്ദ്ര സർക്കാർ",
        "state_label": "സംസ്ഥാനം",
        "no_match": "നിങ്ങളുടെ ചോദ്യവുമായി ബന്ധപ്പെട്ട നിർദ്ദിഷ്ട പദ്ധതി കണ്ടെത്താനായില്ല.",
        "common_schemes": "നിങ്ങൾക്ക് സഹായകമായ ചില **സാധാരണ പദ്ധതികൾ**:",
        "apply_steps": "നിങ്ങളുടെ **അടുത്തുള്ള ബാങ്കിൽ** അല്ലെങ്കിൽ **CSC കേന്ദ്രത്തിൽ** അപേക്ഷിക്കുക.",
    },
    "pa": {
        "intro": "ਤੁਹਾਡੇ ਸਵਾਲ ਦੇ ਆਧਾਰ 'ਤੇ ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ ਦੀ **ਵਿਸਤ੍ਰਿਤ ਜਾਣਕਾਰੀ**:",
        "benefits_heading": "ਤੁਹਾਡੇ ਲਈ ਲਾਭ",
        "eligibility_heading": "ਯੋਗਤਾ",
        "how_to_apply": "ਅਰਜ਼ੀ ਕਿਵੇਂ ਦੇਣੀ ਹੈ",
        "documents_heading": "ਲੋੜੀਂਦੇ ਦਸਤਾਵੇਜ਼",
        "helpline_heading": "ਹੈਲਪਲਾਈਨ",
        "apply_heading": "ਅਰਜ਼ੀ ਲਿੰਕ",
        "state_note": "📍 {state} ਲਈ ਵਿਸ਼ੇਸ਼ ਯੋਜਨਾਵਾਂ ਉੱਪਰ ਨਿਸ਼ਾਨ ਲਗਾਈਆਂ ਗਈਆਂ ਹਨ।",
        "footer": "ਤੁਹਾਡਾ **ਰਾਜ**, **ਜ਼ਮੀਨ ਕਿੰਨੀ ਹੈ** ਅਤੇ **ਕਿਹੜੀ ਫ਼ਸਲ** ਉਗਾਉਂਦੇ ਹੋ ਦੱਸੋ, ਤਾਂ ਮੈਂ ਹੋਰ ਯੋਜਨਾਵਾਂ ਦੱਸ ਸਕਦਾ ਹਾਂ।\n\nਹੋਰ ਜਾਣਕਾਰੀ ਲਈ ਨੇੜਲੇ **CSC ਕੇਂਦਰ** ਜਾਂ **ਗ੍ਰਾਮ ਪੰਚਾਇਤ** ਨਾਲ ਸੰਪਰਕ ਕਰੋ।",
        "central": "ਕੇਂਦਰ ਸਰਕਾਰ",
        "state_label": "ਰਾਜ",
        "no_match": "ਤੁਹਾਡੇ ਸਵਾਲ ਨਾਲ ਸੰਬੰਧਿਤ ਕੋਈ ਵਿਸ਼ੇਸ਼ ਯੋਜਨਾ ਨਹੀਂ ਮਿਲੀ।",
        "common_schemes": "ਤੁਹਾਡੇ ਕੰਮ ਦੀਆਂ ਕੁਝ **ਆਮ ਯੋਜਨਾਵਾਂ**:",
        "apply_steps": "ਤੁਹਾਡੀ **ਨੇੜਲੀ ਬੈਂਕ** ਜਾਂ **CSC ਕੇਂਦਰ** ਵਿੱਚ ਜਾ ਕੇ ਅਰਜ਼ੀ ਦਿਓ।",
    },
    "or": {
        "intro": "ଆପଣଙ୍କ ପ୍ରଶ୍ନ ଆଧାରରେ ସରକାରୀ ଯୋଜନାର **ବିସ୍ତୃତ ତଥ୍ୟ**:",
        "benefits_heading": "ଆପଣଙ୍କ ପାଇଁ ଲାଭ",
        "eligibility_heading": "ଯୋଗ୍ୟତା",
        "how_to_apply": "ଆବେଦନ କିପରି କରିବେ",
        "documents_heading": "ଆବଶ୍ୟକ ନଥିପତ୍ର",
        "helpline_heading": "ହେଲ୍ପଲାଇନ୍",
        "apply_heading": "ଆବେଦନ ଲିଙ୍କ",
        "state_note": "📍 {state} ପାଇଁ ବିଶେଷ ଯୋଜନା ଉପରେ ଚିହ୍ନିତ।",
        "footer": "ଆପଣଙ୍କ **ରାଜ୍ୟ**, **ଜମି ପରିମାଣ** ଓ **ଫସଲ** ଜଣାନ୍ତୁ, ମୁଁ ଆହୁରି ଯୋଜନା ସୁପାରିସ କରିପାରିବି।\n\nଅଧିକ ତଥ୍ୟ ପାଇଁ ନିକଟସ୍ଥ **CSC କେନ୍ଦ୍ର** ବା **ଗ୍ରାମ ପଞ୍ଚାୟତ** ସହ ଯୋଗାଯୋଗ କରନ୍ତୁ।",
        "central": "କେନ୍ଦ୍ର ସରକାର",
        "state_label": "ରାଜ୍ୟ",
        "no_match": "ଆପଣଙ୍କ ପ୍ରଶ୍ନ ସହ ସମ୍ପର୍କିତ କୌଣସି ନିର୍ଦ୍ଦିଷ୍ଟ ଯୋଜନା ମିଳିଲା ନାହିଁ।",
        "common_schemes": "ଆପଣଙ୍କ କାମର କିଛି **ସାଧାରଣ ଯୋଜନା**:",
        "apply_steps": "ଆପଣଙ୍କ **ନିକଟସ୍ଥ ବ୍ୟାଙ୍କ** ବା **CSC କେନ୍ଦ୍ରରେ** ଆବେଦନ କରନ୍ତୁ।",
    },
}


def _get_labels(language: str) -> dict:
    return LANG_LABELS.get(language, LANG_LABELS["en"])


def generate_offline_answer(
    schemes: List[Dict[str, Any]],
    question: str,
    farmer_profile: Optional[Dict[str, Any]] = None,
    language: str = "en",
) -> str:
    if not schemes:
        return _no_scheme_found(language)

    labels = _get_labels(language)
    top = schemes[:3]
    parts = []

    parts.append(f"{labels['intro']}\n")

    for i, s in enumerate(top, 1):
        parts.append(_format_scheme(s, i, language, labels, farmer_profile))

    if farmer_profile and farmer_profile.get("state"):
        state = farmer_profile["state"]
        state_schemes = [s for s in top if s.get("state") and s["state"].lower() == state.lower()]
        if state_schemes:
            parts.append(f"\n{labels['state_note'].format(state=state)}")

    parts.append(f"\n{labels['footer']}")

    return "\n".join(parts)


def _format_scheme(s: Dict[str, Any], idx: int, lang: str, labels: dict, profile: Optional[Dict] = None) -> str:
    lines = []
    name = s.get("name", "Unknown Scheme")
    scheme_type = s.get("type", "")
    state = s.get("state", "")
    badge = ""
    if scheme_type == "central":
        badge = f" [{labels['central']}]"
    elif scheme_type == "state" and state:
        badge = f" [{state}]"

    lines.append(f"\n{'─' * 30}")
    lines.append(f"**{name}**{badge}")
    if s.get("description"):
        desc = s["description"]
        if len(desc) > 250:
            desc = desc[:247] + "..."
        lines.append(f"{desc}\n")

    if s.get("benefits"):
        lines.append(f"1) **💰 {labels['benefits_heading']}**")
        benefits = s["benefits"]
        benefit_items = [b.strip() for b in benefits.replace(";", ",").split(",") if b.strip()]
        if len(benefit_items) > 1:
            for b in benefit_items[:5]:
                lines.append(f"   - {b}")
        else:
            lines.append(f"   - {benefits}")

    if s.get("eligibility"):
        lines.append(f"\n2) **✅ {labels['eligibility_heading']}**")
        elig = s["eligibility"]
        elig_items = [e.strip() for e in elig.replace(";", ".").split(".") if e.strip() and len(e.strip()) > 5]
        if len(elig_items) > 1:
            for e in elig_items[:5]:
                lines.append(f"   - {e}")
        else:
            lines.append(f"   - {elig}")

        if profile:
            if profile.get("occupation") and "farmer" in profile.get("occupation", "").lower():
                if lang == "hi":
                    lines.append(f"   - आप किसान हैं, इसलिए यह योजना आपके लिए लागू हो सकती है।")
                elif lang != "en":
                    pass
                else:
                    lines.append(f"   - As a farmer, you may be eligible for this scheme.")

    lines.append(f"\n3) **📋 {labels['how_to_apply']}**")
    lines.append(f"   - {labels['apply_steps']}")
    app_url = s.get("application_url") or ""
    if app_url and app_url.startswith("http"):
        lines.append(f"   - 🔗 {labels['apply_heading']}: {app_url}")

    docs = s.get("documents") or []
    if docs:
        lines.append(f"\n4) **📄 {labels['documents_heading']}**")
        for d in docs[:6]:
            lines.append(f"   - {d}")
        if len(docs) > 6:
            lines.append(f"   - (+{len(docs) - 6} more)")

    if s.get("helpline"):
        lines.append(f"\n5) **📞 {labels['helpline_heading']}:** {s['helpline']}")

    official_links = s.get("documents_links") or []
    if official_links:
        lines.append(f"   🔗 {', '.join(official_links[:3])}")

    return "\n".join(lines)


def _no_scheme_found(lang: str) -> str:
    labels = _get_labels(lang)
    return (
        f"{labels['no_match']}\n\n"
        f"{labels['common_schemes']}\n"
        "• **PM-KISAN** (₹6,000/year) - pmkisan.gov.in\n"
        "• **Ayushman Bharat** (₹5 lakh health cover) - pmjay.gov.in\n"
        "• **PM Awas Yojana** (Housing) - pmayg.nic.in\n"
        "• **PMFBY** (Crop Insurance) - pmfby.gov.in\n"
        "• **Kisan Credit Card** (Farm loans at 4%) - pmkisan.gov.in\n\n"
        f"{labels['footer']}"
    )
