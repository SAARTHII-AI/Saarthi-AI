const API_URL = "";

let conversationHistory = [];
const MAX_CONVERSATION_HISTORY = 12;

const I18N = {
    hi: {
        thinking:       "सोच रहा है...",
        listening:      "सुन रहा हूँ...",
        understood:     "समझ लिया!",
        offline:        "आप ऑफलाइन हैं। सहेजा गया उत्तर दिखा रहा है।",
        noCache:        "आप ऑफलाइन हैं। स्थानीय डेटा से उत्तर दे रहा हूँ।",
        serverError:    "सर्वर से संपर्क नहीं हो पा रहा है।",
        savedAnswer:    "सहेजा गया उत्तर",
        onlinePill:     "ऑनलाइन",
        offlinePill:    "ऑफलाइन",
        micUnsupported: "इस ब्राउज़र में वॉइस इनपुट समर्थित नहीं है। कृपया टाइप करें।",
        hearError:      "माफ़ करें, मैं सुन नहीं पाया।",
        schemesHeading: "अनुशंसित योजनाएं:",
        stopSpeaking:   "बोलना बंद करें",
        offlineAnswer:  "ऑफलाइन उत्तर",
        usefulLinks:    "उपयोगी लिंक",
        nearbyCenters:  "नजदीकी केंद्र",
        openMaps:       "नक्शे में देखें",
        officialLink:   "आधिकारिक लिंक",
        typeMessage:    "संदेश टाइप करें...",
        allSchemes:     "सभी योजनाएं",
        central:        "केंद्र",
        offlineFeatures: "ऑफलाइन में उपलब्ध: सहेजे गए उत्तर • योजना जानकारी • हेल्पलाइन नंबर",
        syncing:        "इंटरनेट वापस आया! डेटा अपडेट हो रहा है...",
        syncDone:       "डेटा अपडेट हो गया!",
    },
    en: {
        thinking:       "Thinking...",
        listening:      "Listening...",
        understood:     "Understood!",
        offline:        "You are offline. Showing saved answer.",
        noCache:        "You are offline. Answering from local data.",
        serverError:    "Unable to contact the server.",
        savedAnswer:    "Saved answer",
        onlinePill:     "Online",
        offlinePill:    "Offline",
        micUnsupported: "Voice input not supported on this browser. Please type.",
        hearError:      "Sorry, I couldn't hear you.",
        schemesHeading: "Recommended Schemes:",
        stopSpeaking:   "Stop Speaking",
        offlineAnswer:  "Offline answer",
        usefulLinks:    "Useful Links",
        nearbyCenters:  "Nearby Centers",
        openMaps:       "Open in Maps",
        officialLink:   "Official Link",
        typeMessage:    "Type a message...",
        allSchemes:     "All Schemes",
        central:        "Central",
        offlineFeatures: "Available offline: Saved answers • Scheme info • Helpline numbers",
        syncing:        "Back online! Syncing data...",
        syncDone:       "Data synced!",
    },
    bn: {
        thinking:       "ভাবছি...",
        listening:      "শুনছি...",
        understood:     "বুঝেছি!",
        offline:        "আপনি অফলাইনে আছেন। সংরক্ষিত উত্তর দেখাচ্ছি।",
        noCache:        "আপনি অফলাইনে আছেন। স্থানীয় তথ্য থেকে উত্তর দিচ্ছি।",
        serverError:    "সার্ভারে যোগাযোগ করা যাচ্ছে না।",
        savedAnswer:    "সংরক্ষিত উত্তর",
        onlinePill:     "অনলাইন",
        offlinePill:    "অফলাইন",
        micUnsupported: "এই ব্রাউজারে ভয়েস ইনপুট সমর্থিত নয়। অনুগ্রহ করে টাইপ করুন।",
        hearError:      "দুঃখিত, আমি শুনতে পাইনি।",
        schemesHeading: "প্রস্তাবিত প্রকল্পসমূহ:",
        stopSpeaking:   "কথা বলা বন্ধ করুন",
        offlineAnswer:  "অফলাইন উত্তর",
        usefulLinks:    "দরকারি লিংক",
        nearbyCenters:  "নিকটবর্তী কেন্দ্র",
        openMaps:       "মানচিত্রে দেখুন",
        officialLink:   "অফিসিয়াল লিংক",
        typeMessage:    "একটি বার্তা টাইপ করুন...",
        allSchemes:     "সকল প্রকল্প",
        central:        "কেন্দ্রীয়",
        offlineFeatures: "অফলাইনে পাওয়া যায়: সংরক্ষিত উত্তর • প্রকল্পের তথ্য • হেল্পলাইন নম্বর",
        syncing:        "অনলাইনে ফিরে এসেছেন! ডেটা আপডেট হচ্ছে...",
        syncDone:       "ডেটা আপডেট হয়েছে!",
    },
    te: {
        thinking:       "ఆలోచిస్తున్నాను...",
        listening:      "వింటున్నాను...",
        understood:     "అర్థమైంది!",
        offline:        "మీరు ఆఫ్‌లైన్‌లో ఉన్నారు. సేవ్ చేసిన సమాధానం చూపిస్తున్నాను.",
        noCache:        "మీరు ఆఫ్‌లైన్‌లో ఉన్నారు. స్థానిక డేటా నుండి సమాధానం ఇస్తున్నాను.",
        serverError:    "సర్వర్‌ను సంప్రదించడం సాధ్యం కాలేదు.",
        savedAnswer:    "సేవ్ చేసిన సమాధానం",
        onlinePill:     "ఆన్‌లైన్",
        offlinePill:    "ఆఫ్‌లైన్",
        micUnsupported: "ఈ బ్రౌజర్‌లో వాయిస్ ఇన్‌పుట్ మద్దతు లేదు. దయచేసి టైప్ చేయండి.",
        hearError:      "క్షమించండి, నేను వినలేకపోయాను.",
        schemesHeading: "సిఫార్సు చేసిన పథకాలు:",
        stopSpeaking:   "మాట్లాడటం ఆపండి",
        offlineAnswer:  "ఆఫ్‌లైన్ సమాధానం",
        usefulLinks:    "ఉపయోగకరమైన లింకులు",
        nearbyCenters:  "సమీపంలోని కేంద్రాలు",
        openMaps:       "మ్యాప్‌లో చూడండి",
        officialLink:   "అధికారిక లింక్",
        typeMessage:    "సందేశం టైప్ చేయండి...",
        allSchemes:     "అన్ని పథకాలు",
        central:        "కేంద్ర",
        offlineFeatures: "ఆఫ్‌లైన్‌లో అందుబాటులో: సేవ్ చేసిన సమాధానాలు • పథకాల సమాచారం • హెల్ప్‌లైన్ నంబర్లు",
        syncing:        "ఆన్‌లైన్‌కు తిరిగి వచ్చారు! డేటా అప్‌డేట్ అవుతోంది...",
        syncDone:       "డేటా అప్‌డేట్ అయింది!",
    },
    mr: {
        thinking:       "विचार करत आहे...",
        listening:      "ऐकत आहे...",
        understood:     "समजले!",
        offline:        "तुम्ही ऑफलाइन आहात. जतन केलेले उत्तर दाखवत आहे.",
        noCache:        "तुम्ही ऑफलाइन आहात. स्थानिक डेटावरून उत्तर देत आहे.",
        serverError:    "सर्व्हरशी संपर्क होऊ शकला नाही.",
        savedAnswer:    "जतन केलेले उत्तर",
        onlinePill:     "ऑनलाइन",
        offlinePill:    "ऑफलाइन",
        micUnsupported: "या ब्राउझरमध्ये व्हॉइस इनपुट समर्थित नाही. कृपया टाइप करा.",
        hearError:      "माफ करा, मला ऐकू आले नाही.",
        schemesHeading: "शिफारस केलेल्या योजना:",
        stopSpeaking:   "बोलणे थांबवा",
        offlineAnswer:  "ऑफलाइन उत्तर",
        usefulLinks:    "उपयुक्त दुवे",
        nearbyCenters:  "जवळचे केंद्र",
        openMaps:       "नकाशावर पहा",
        officialLink:   "अधिकृत दुवा",
        typeMessage:    "संदेश टाइप करा...",
        allSchemes:     "सर्व योजना",
        central:        "केंद्र",
        offlineFeatures: "ऑफलाइनमध्ये उपलब्ध: जतन केलेली उत्तरे • योजनांची माहिती • हेल्पलाइन क्रमांक",
        syncing:        "ऑनलाइन परत आलात! डेटा अपडेट होत आहे...",
        syncDone:       "डेटा अपडेट झाला!",
    },
    ta: {
        thinking:       "யோசிக்கிறேன்...",
        listening:      "கேட்கிறேன்...",
        understood:     "புரிந்தது!",
        offline:        "நீங்கள் ஆஃப்லைனில் உள்ளீர்கள். சேமிக்கப்பட்ட பதிலைக் காட்டுகிறேன்.",
        noCache:        "நீங்கள் ஆஃப்லைனில் உள்ளீர்கள். உள்ளூர் தரவிலிருந்து பதிலளிக்கிறேன்.",
        serverError:    "சர்வரை தொடர்பு கொள்ள இயலவில்லை.",
        savedAnswer:    "சேமிக்கப்பட்ட பதில்",
        onlinePill:     "ஆன்லைன்",
        offlinePill:    "ஆஃப்லைன்",
        micUnsupported: "இந்த உலாவியில் குரல் உள்ளீடு ஆதரிக்கப்படவில்லை. தயவுசெய்து தட்டச்சு செய்யுங்கள்.",
        hearError:      "மன்னிக்கவும், என்னால் கேட்க இயலவில்லை.",
        schemesHeading: "பரிந்துரைக்கப்பட்ட திட்டங்கள்:",
        stopSpeaking:   "பேசுவதை நிறுத்துங்கள்",
        offlineAnswer:  "ஆஃப்லைன் பதில்",
        usefulLinks:    "பயனுள்ள இணைப்புகள்",
        nearbyCenters:  "அருகிலுள்ள மையங்கள்",
        openMaps:       "வரைபடத்தில் பாருங்கள்",
        officialLink:   "அதிகாரப்பூர்வ இணைப்பு",
        typeMessage:    "செய்தியை தட்டச்சு செய்யுங்கள்...",
        allSchemes:     "அனைத்து திட்டங்கள்",
        central:        "மத்திய",
        offlineFeatures: "ஆஃப்லைனில் கிடைக்கும்: சேமிக்கப்பட்ட பதில்கள் • திட்டத் தகவல்கள் • ஹெல்ப்லைன் எண்கள்",
        syncing:        "ஆன்லைனில் திரும்பிவிட்டீர்கள்! தரவு புதுப்பிக்கப்படுகிறது...",
        syncDone:       "தரவு புதுப்பிக்கப்பட்டது!",
    },
    gu: {
        thinking:       "વિચારી રહ્યો છું...",
        listening:      "સાંભળી રહ્યો છું...",
        understood:     "સમજી ગયો!",
        offline:        "તમે ઑફલાઇન છો. સાચવેલો જવાબ બતાવી રહ્યો છું.",
        noCache:        "તમે ઑફલાઇન છો. સ્થાનિક ડેટામાંથી જવાબ આપી રહ્યો છું.",
        serverError:    "સર્વર સાથે સંપર્ક કરી શકાયો નહીં.",
        savedAnswer:    "સાચવેલો જવાબ",
        onlinePill:     "ઑનલાઇન",
        offlinePill:    "ઑફલાઇન",
        micUnsupported: "આ બ્રાઉઝરમાં અવાજ ઇનપુટ સમર્થિત નથી. કૃપા કરીને ટાઇપ કરો.",
        hearError:      "માફ કરશો, હું સાંભળી શક્યો નહીં.",
        schemesHeading: "ભલામણ કરેલી યોજનાઓ:",
        stopSpeaking:   "બોલવાનું બંધ કરો",
        offlineAnswer:  "ઑફલાઇન જવાબ",
        usefulLinks:    "ઉપયોગી લિંક્સ",
        nearbyCenters:  "નજીકના કેન્દ્રો",
        openMaps:       "નકશામાં જુઓ",
        officialLink:   "અધિકૃત લિંક",
        typeMessage:    "સંદેશ ટાઇપ કરો...",
        allSchemes:     "બધી યોજનાઓ",
        central:        "કેન્દ્ર",
        offlineFeatures: "ઑફલાઇનમાં ઉપલબ્ધ: સાચવેલા જવાબો • યોજનાની માહિતી • હેલ્પલાઇન નંબર",
        syncing:        "ઑનલાઇન પાછા આવ્યા! ડેટા અપડેટ થઈ રહ્યો છે...",
        syncDone:       "ડેટા અપડેટ થઈ ગયો!",
    },
    kn: {
        thinking:       "ಯೋಚಿಸುತ್ತಿದ್ದೇನೆ...",
        listening:      "ಕೇಳುತ್ತಿದ್ದೇನೆ...",
        understood:     "ಅರ್ಥವಾಯಿತು!",
        offline:        "ನೀವು ಆಫ್‌ಲೈನ್‌ನಲ್ಲಿದ್ದೀರಿ. ಉಳಿಸಿದ ಉತ್ತರವನ್ನು ತೋರಿಸುತ್ತಿದ್ದೇನೆ.",
        noCache:        "ನೀವು ಆಫ್‌ಲೈನ್‌ನಲ್ಲಿದ್ದೀರಿ. ಸ್ಥಳೀಯ ಡೇಟಾದಿಂದ ಉತ್ತರಿಸುತ್ತಿದ್ದೇನೆ.",
        serverError:    "ಸರ್ವರ್ ಅನ್ನು ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
        savedAnswer:    "ಉಳಿಸಿದ ಉತ್ತರ",
        onlinePill:     "ಆನ್‌ಲೈನ್",
        offlinePill:    "ಆಫ್‌ಲೈನ್",
        micUnsupported: "ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಬೆಂಬಲಿತವಲ್ಲ. ದಯವಿಟ್ಟು ಟೈಪ್ ಮಾಡಿ.",
        hearError:      "ಕ್ಷಮಿಸಿ, ನನಗೆ ಕೇಳಲಾಗಲಿಲ್ಲ.",
        schemesHeading: "ಶಿಫಾರಸು ಮಾಡಿದ ಯೋಜನೆಗಳು:",
        stopSpeaking:   "ಮಾತನಾಡುವುದನ್ನು ನಿಲ್ಲಿಸಿ",
        offlineAnswer:  "ಆಫ್‌ಲೈನ್ ಉತ್ತರ",
        usefulLinks:    "ಉಪಯುಕ್ತ ಲಿಂಕ್‌ಗಳು",
        nearbyCenters:  "ಹತ್ತಿರದ ಕೇಂದ್ರಗಳು",
        openMaps:       "ನಕ್ಷೆಯಲ್ಲಿ ನೋಡಿ",
        officialLink:   "ಅಧಿಕೃತ ಲಿಂಕ್",
        typeMessage:    "ಸಂದೇಶ ಟೈಪ್ ಮಾಡಿ...",
        allSchemes:     "ಎಲ್ಲಾ ಯೋಜನೆಗಳು",
        central:        "ಕೇಂದ್ರ",
        offlineFeatures: "ಆಫ್‌ಲೈನ್‌ನಲ್ಲಿ ಲಭ್ಯ: ಉಳಿಸಿದ ಉತ್ತರಗಳು • ಯೋಜನೆಯ ಮಾಹಿತಿ • ಹೆಲ್ಪ್‌ಲೈನ್ ಸಂಖ್ಯೆಗಳು",
        syncing:        "ಆನ್‌ಲೈನ್‌ಗೆ ಮರಳಿದ್ದೀರಿ! ಡೇಟಾ ಅಪ್‌ಡೇಟ್ ಆಗುತ್ತಿದೆ...",
        syncDone:       "ಡೇಟಾ ಅಪ್‌ಡೇಟ್ ಆಯಿತು!",
    },
    ml: {
        thinking:       "ആലോചിക്കുന്നു...",
        listening:      "കേൾക്കുന്നു...",
        understood:     "മനസ്സിലായി!",
        offline:        "നിങ്ങൾ ഓഫ്‌ലൈനിലാണ്. സേവ് ചെയ്ത ഉത്തരം കാണിക്കുന്നു.",
        noCache:        "നിങ്ങൾ ഓഫ്‌ലൈനിലാണ്. ലോക്കൽ ഡാറ്റയിൽ നിന്ന് ഉത്തരം നൽകുന്നു.",
        serverError:    "സെർവറുമായി ബന്ധപ്പെടാൻ കഴിയുന്നില്ല.",
        savedAnswer:    "സേവ് ചെയ്ത ഉത്തരം",
        onlinePill:     "ഓൺലൈൻ",
        offlinePill:    "ഓഫ്‌ലൈൻ",
        micUnsupported: "ഈ ബ്രൗസറിൽ വോയ്‌സ് ഇൻപുട്ട് പിന്തുണയ്ക്കുന്നില്ല. ദയവായി ടൈപ്പ് ചെയ്യുക.",
        hearError:      "ക്ഷമിക്കണം, എനിക്ക് കേൾക്കാൻ കഴിഞ്ഞില്ല.",
        schemesHeading: "ശുപാർശ ചെയ്ത പദ്ധതികൾ:",
        stopSpeaking:   "സംസാരിക്കുന്നത് നിർത്തുക",
        offlineAnswer:  "ഓഫ്‌ലൈൻ ഉത്തരം",
        usefulLinks:    "ഉപയോഗപ്രദമായ ലിങ്കുകൾ",
        nearbyCenters:  "സമീപത്തുള്ള കേന്ദ്രങ്ങൾ",
        openMaps:       "മാപ്പിൽ കാണുക",
        officialLink:   "ഔദ്യോഗിക ലിങ്ക്",
        typeMessage:    "ഒരു സന്ദേശം ടൈപ്പ് ചെയ്യുക...",
        allSchemes:     "എല്ലാ പദ്ധതികളും",
        central:        "കേന്ദ്ര",
        offlineFeatures: "ഓഫ്‌ലൈനിൽ ലഭ്യം: സേവ് ചെയ്ത ഉത്തരങ്ങൾ • പദ്ധതി വിവരങ്ങൾ • ഹെൽപ്‌ലൈൻ നമ്പറുകൾ",
        syncing:        "ഓൺലൈനിൽ തിരിച്ചെത്തി! ഡാറ്റ അപ്‌ഡേറ്റ് ചെയ്യുന്നു...",
        syncDone:       "ഡാറ്റ അപ്‌ഡേറ്റ് ചെയ്തു!",
    },
    pa: {
        thinking:       "ਸੋਚ ਰਿਹਾ ਹਾਂ...",
        listening:      "ਸੁਣ ਰਿਹਾ ਹਾਂ...",
        understood:     "ਸਮਝ ਲਿਆ!",
        offline:        "ਤੁਸੀਂ ਔਫਲਾਈਨ ਹੋ। ਸੰਭਾਲਿਆ ਹੋਇਆ ਜਵਾਬ ਦਿਖਾ ਰਿਹਾ ਹਾਂ।",
        noCache:        "ਤੁਸੀਂ ਔਫਲਾਈਨ ਹੋ। ਸਥਾਨਕ ਡੇਟਾ ਤੋਂ ਜਵਾਬ ਦੇ ਰਿਹਾ ਹਾਂ।",
        serverError:    "ਸਰਵਰ ਨਾਲ ਸੰਪਰਕ ਨਹੀਂ ਹੋ ਸਕਿਆ।",
        savedAnswer:    "ਸੰਭਾਲਿਆ ਹੋਇਆ ਜਵਾਬ",
        onlinePill:     "ਔਨਲਾਈਨ",
        offlinePill:    "ਔਫਲਾਈਨ",
        micUnsupported: "ਇਸ ਬ੍ਰਾਊਜ਼ਰ ਵਿੱਚ ਅਵਾਜ਼ ਇਨਪੁੱਟ ਸਮਰਥਿਤ ਨਹੀਂ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਟਾਈਪ ਕਰੋ।",
        hearError:      "ਮਾਫ਼ ਕਰਨਾ, ਮੈਂ ਸੁਣ ਨਹੀਂ ਸਕਿਆ।",
        schemesHeading: "ਸਿਫ਼ਾਰਸ਼ ਕੀਤੀਆਂ ਯੋਜਨਾਵਾਂ:",
        stopSpeaking:   "ਬੋਲਣਾ ਬੰਦ ਕਰੋ",
        offlineAnswer:  "ਔਫਲਾਈਨ ਜਵਾਬ",
        usefulLinks:    "ਲਾਭਦਾਇਕ ਲਿੰਕ",
        nearbyCenters:  "ਨੇੜਲੇ ਕੇਂਦਰ",
        openMaps:       "ਨਕਸ਼ੇ ਵਿੱਚ ਦੇਖੋ",
        officialLink:   "ਅਧਿਕਾਰਤ ਲਿੰਕ",
        typeMessage:    "ਸੁਨੇਹਾ ਟਾਈਪ ਕਰੋ...",
        allSchemes:     "ਸਾਰੀਆਂ ਯੋਜਨਾਵਾਂ",
        central:        "ਕੇਂਦਰ",
        offlineFeatures: "ਔਫਲਾਈਨ ਵਿੱਚ ਉਪਲਬਧ: ਸੰਭਾਲੇ ਹੋਏ ਜਵਾਬ • ਯੋਜਨਾ ਜਾਣਕਾਰੀ • ਹੈਲਪਲਾਈਨ ਨੰਬਰ",
        syncing:        "ਔਨਲਾਈਨ ਵਾਪਸ ਆ ਗਏ! ਡੇਟਾ ਅੱਪਡੇਟ ਹੋ ਰਿਹਾ ਹੈ...",
        syncDone:       "ਡੇਟਾ ਅੱਪਡੇਟ ਹੋ ਗਿਆ!",
    },
    or: {
        thinking:       "ଚିନ୍ତା କରୁଛି...",
        listening:      "ଶୁଣୁଛି...",
        understood:     "ବୁଝିଗଲି!",
        offline:        "ଆପଣ ଅଫଲାଇନ୍ ଅଛନ୍ତି। ସଞ୍ଚିତ ଉତ୍ତର ଦେଖାଉଛି।",
        noCache:        "ଆପଣ ଅଫଲାଇନ୍ ଅଛନ୍ତି। ସ୍ଥାନୀୟ ତଥ୍ୟରୁ ଉତ୍ତର ଦେଉଛି।",
        serverError:    "ସର୍ଭର ସହ ଯୋଗାଯୋଗ ହୋଇପାରିଲା ନାହିଁ।",
        savedAnswer:    "ସଞ୍ଚିତ ଉତ୍ତର",
        onlinePill:     "ଅନଲାଇନ୍",
        offlinePill:    "ଅଫଲାଇନ୍",
        micUnsupported: "ଏହି ବ୍ରାଉଜରରେ ଭଏସ୍ ଇନପୁଟ୍ ସମର୍ଥିତ ନୁହେଁ। ଦୟାକରି ଟାଇପ୍ କରନ୍ତୁ।",
        hearError:      "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ଶୁଣିପାରିଲି ନାହିଁ।",
        schemesHeading: "ପରାମର୍ଶିତ ଯୋଜନାଗୁଡ଼ିକ:",
        stopSpeaking:   "କଥା ବନ୍ଦ କରନ୍ତୁ",
        offlineAnswer:  "ଅଫଲାଇନ୍ ଉତ୍ତର",
        usefulLinks:    "ଉପଯୋଗୀ ଲିଙ୍କ",
        nearbyCenters:  "ନିକଟସ୍ଥ କେନ୍ଦ୍ର",
        openMaps:       "ମାନଚିତ୍ରରେ ଦେଖନ୍ତୁ",
        officialLink:   "ଅଧିକୃତ ଲିଙ୍କ",
        typeMessage:    "ଏକ ସନ୍ଦେଶ ଟାଇପ୍ କରନ୍ତୁ...",
        allSchemes:     "ସମସ୍ତ ଯୋଜନା",
        central:        "କେନ୍ଦ୍ର",
        offlineFeatures: "ଅଫଲାଇନ୍ ରେ ଉପଲବ୍ଧ: ସଞ୍ଚିତ ଉତ୍ତର • ଯୋଜନା ତଥ୍ୟ • ହେଲ୍ପଲାଇନ୍ ନମ୍ବର",
        syncing:        "ଅନଲାଇନ୍ ରେ ଫେରି ଆସିଛନ୍ତି! ତଥ୍ୟ ଅପଡେଟ୍ ହେଉଛି...",
        syncDone:       "ତଥ୍ୟ ଅପଡେଟ୍ ହୋଇଗଲା!",
    },
};

function getLang() {
    const v = document.getElementById("language-select").value;
    if (v && v !== "auto") return v;
    const nav = (navigator.language || navigator.userLanguage || "en").toLowerCase();
    if (nav.startsWith("hi")) return "hi";
    if (nav.startsWith("bn")) return "bn";
    if (nav.startsWith("te")) return "te";
    if (nav.startsWith("mr")) return "mr";
    if (nav.startsWith("ta")) return "ta";
    if (nav.startsWith("gu")) return "gu";
    if (nav.startsWith("kn")) return "kn";
    if (nav.startsWith("ml")) return "ml";
    if (nav.startsWith("pa")) return "pa";
    if (nav.startsWith("or")) return "or";
    return "en";
}

function t(key) {
    return (I18N[getLang()] || I18N.en)[key] || I18N.en[key] || key;
}

window.t = t;
window.getLang = getLang;

function isOnline() {
    return navigator.onLine;
}

function updateConnectivityPill() {
    const pill = document.getElementById("connectivity-pill");
    if (!pill) return;
    if (isOnline()) {
        pill.textContent = t("onlinePill");
        pill.className = "connectivity-pill online";
    } else {
        pill.textContent = t("offlinePill");
        pill.className = "connectivity-pill offline";
    }
}

const SCHEMES_CACHE_KEY = "saarthi_schemes_offline";
const EMERGENCY_CACHE_KEY = "saarthi_emergency_info";

const EMERGENCY_INFO = {
    helplines: [
        { name: "Kisan Call Center", number: "1800-180-1551", desc: "24/7 toll-free agriculture helpline" },
        { name: "PM-KISAN Helpline", number: "155261", desc: "PM-KISAN registration & status" },
        { name: "Crop Insurance (PMFBY)", number: "1800-200-7710", desc: "Crop insurance claims" },
        { name: "Soil Health Card", number: "1800-180-1551", desc: "Soil testing & card status" },
        { name: "CSC Helpline", number: "1800-121-3468", desc: "Common Service Center locator" },
        { name: "District Agriculture Officer", number: "Local DAO", desc: "Contact via District Collectorate" },
    ],
    emergency_urls: {
        "PM-KISAN": "https://pmkisan.gov.in",
        "PMFBY": "https://pmfby.gov.in",
        "Soil Health Card": "https://soilhealth.dac.gov.in",
        "e-NAM (Mandi Prices)": "https://enam.gov.in",
        "KCC": "https://eseva.csccloud.in/KCC/",
    },
};

function saveEmergencyInfo() {
    try {
        localStorage.setItem(EMERGENCY_CACHE_KEY, JSON.stringify({
            data: EMERGENCY_INFO,
            timestamp: Date.now()
        }));
    } catch (e) {}
}

function loadEmergencyInfo() {
    try {
        const raw = localStorage.getItem(EMERGENCY_CACHE_KEY);
        if (raw) return JSON.parse(raw).data;
    } catch (e) {}
    return EMERGENCY_INFO;
}

saveEmergencyInfo();

function showOfflineFeatureBanner() {
    const existing = document.getElementById("offline-features-banner");
    if (existing) existing.remove();
    if (isOnline()) return;

    const chatBox = document.getElementById("chat-box");
    if (!chatBox) return;

    const banner = document.createElement("div");
    banner.id = "offline-features-banner";
    banner.className = "mx-4 mt-2 p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-start gap-2 message-fade-in";
    banner.innerHTML = `<span class="material-symbols-outlined text-sm mt-0.5" style="font-variation-settings:'FILL' 1">wifi_off</span>
        <div>
            <div class="font-semibold mb-1">${t("offlinePill")}</div>
            <div>${t("offlineFeatures")}</div>
        </div>`;
    chatBox.insertBefore(banner, chatBox.firstChild);
}

function hideOfflineFeatureBanner() {
    const existing = document.getElementById("offline-features-banner");
    if (existing) existing.remove();
}

function syncOnReconnect() {
    if (!isOnline()) return;
    showStatus(t("syncing"));
    saveEmergencyInfo();

    fetch(`${API_URL}/schemes`)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
            if (data && data.schemes) {
                saveOfflineSchemes(data.schemes);
                showStatus(t("syncDone"));
            } else {
                showStatus("");
            }
            setTimeout(() => showStatus(""), 2000);
        })
        .catch(() => {
            showStatus("");
        });
}

window.addEventListener("online", () => {
    updateConnectivityPill();
    hideOfflineFeatureBanner();
    syncOnReconnect();
});
window.addEventListener("offline", () => {
    updateConnectivityPill();
    showOfflineFeatureBanner();
});

const PROFILE_KEY = "saarthi_farmer_profile";

function loadFarmerProfile() {
    try {
        return JSON.parse(localStorage.getItem(PROFILE_KEY)) || {};
    } catch (e) {
        return {};
    }
}

function saveFarmerProfile(profile) {
    localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

function getFarmerProfileSnapshot() {
    const p = loadFarmerProfile();
    return `${p.state || ""}|${p.crop || ""}|${p.landSize || ""}|${p.income || ""}`;
}

function openProfileDrawer() {
    const drawer   = document.getElementById("profile-drawer");
    const overlay  = document.getElementById("profile-overlay");
    if (drawer) {
        const p = loadFarmerProfile();
        document.getElementById("profile-state").value  = p.state    || "";
        document.getElementById("profile-crop").value   = p.crop     || "";
        document.getElementById("profile-land").value   = p.landSize || "";
        document.getElementById("profile-income").value = p.income   || "";
        drawer.classList.remove("hidden");
        drawer.classList.add("flex");
        drawer.style.flexDirection = "column";
    }
    if (overlay) {
        overlay.classList.remove("hidden");
        overlay.classList.add("block");
    }
}

function closeProfileDrawer() {
    const drawer  = document.getElementById("profile-drawer");
    const overlay = document.getElementById("profile-overlay");
    if (drawer) {
        drawer.classList.add("hidden");
        drawer.classList.remove("flex");
    }
    if (overlay) {
        overlay.classList.add("hidden");
        overlay.classList.remove("block");
    }
}

function saveProfileFromDrawer() {
    const profile = {
        state:    document.getElementById("profile-state").value.trim(),
        crop:     document.getElementById("profile-crop").value.trim(),
        landSize: document.getElementById("profile-land").value.trim(),
        income:   document.getElementById("profile-income").value.trim(),
    };
    saveFarmerProfile(profile);
    closeProfileDrawer();
}

const CACHE_META_KEY  = "saarthi_cache_meta";
const CACHE_MAX       = 150;
const CACHE_TTL_MS    = 14 * 24 * 60 * 60 * 1000;

function simpleHash(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) {
        h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
    }
    return Math.abs(h).toString(36);
}

function buildCacheKey(query, language, profileSnapshot) {
    return "saarthi_" + simpleHash(query + language + profileSnapshot);
}

function loadCacheMeta() {
    try {
        return JSON.parse(localStorage.getItem(CACHE_META_KEY)) || [];
    } catch (e) {
        return [];
    }
}

function saveCacheMeta(meta) {
    localStorage.setItem(CACHE_META_KEY, JSON.stringify(meta));
}

function pruneOldCacheEntries() {
    const now = Date.now();
    const meta = loadCacheMeta().filter(entry => {
        if (now - entry.timestamp > CACHE_TTL_MS) {
            localStorage.removeItem(entry.key);
            return false;
        }
        return true;
    });
    saveCacheMeta(meta);
}

function touchCacheMeta(cacheKey) {
    let meta = loadCacheMeta();
    const idx = meta.findIndex(m => m.key === cacheKey);
    if (idx !== -1) {
        const entry = meta.splice(idx, 1)[0];
        entry.lastAccessed = Date.now();
        meta.push(entry);
        saveCacheMeta(meta);
    }
}

function getCachedResponse(cacheKey) {
    try {
        const raw = localStorage.getItem(cacheKey);
        if (!raw) return null;
        const entry = JSON.parse(raw);
        if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
            localStorage.removeItem(cacheKey);
            return null;
        }
        touchCacheMeta(cacheKey);
        return entry.data;
    } catch (e) {
        return null;
    }
}

function cacheResponse(cacheKey, data, query, language) {
    const now = Date.now();
    const entry = { data, timestamp: now, query, language };
    localStorage.setItem(cacheKey, JSON.stringify(entry));

    let meta = loadCacheMeta();
    meta = meta.filter(m => m.key !== cacheKey);
    meta.push({ key: cacheKey, timestamp: now, lastAccessed: now });

    if (meta.length > CACHE_MAX) {
        meta.sort((a, b) => (a.lastAccessed || a.timestamp) - (b.lastAccessed || b.timestamp));
        const evicted = meta.shift();
        localStorage.removeItem(evicted.key);
    }
    saveCacheMeta(meta);
}

function queryWordOverlap(lq, eq) {
    const stopWords = new Set(["the","a","an","is","are","was","were","for","and","or","in","of","to","my","me","i","how","what","which","can","do","does","get","about","this","that","please","kya","hai","ka","ke","ki","ko","se","mein","kaise","mera","meri","mere"]);
    const wordsA = lq.split(/\s+/).filter(w => w.length >= 2 && !stopWords.has(w));
    const wordsB = eq.split(/\s+/).filter(w => w.length >= 2 && !stopWords.has(w));
    if (wordsA.length === 0 || wordsB.length === 0) return 0;
    let overlap = 0;
    for (const w of wordsA) {
        if (wordsB.some(b => b.includes(w) || w.includes(b))) overlap++;
    }
    return overlap / Math.max(wordsA.length, wordsB.length);
}

function findBestCachedAnswer(query, language) {
    const meta = loadCacheMeta();
    const lq = query.toLowerCase().trim();
    const now = Date.now();
    let bestMatch = null;
    let bestScore = 0;

    for (let i = meta.length - 1; i >= 0; i--) {
        const raw = localStorage.getItem(meta[i].key);
        if (!raw) continue;
        try {
            const entry = JSON.parse(raw);
            if (now - entry.timestamp > CACHE_TTL_MS) {
                localStorage.removeItem(meta[i].key);
                continue;
            }
            const eq = (entry.query || "").toLowerCase().trim();
            if (!eq) continue;
            let score = queryWordOverlap(lq, eq);
            if (entry.language === language) score += 0.1;
            if (score > bestScore && score >= 0.4) {
                bestScore = score;
                bestMatch = { data: entry.data, key: meta[i].key };
            }
        } catch (e) {}
    }

    if (bestMatch) {
        touchCacheMeta(bestMatch.key);
        return bestMatch.data;
    }
    return null;
}

const SCHEMES_CACHE_TTL = 24 * 60 * 60 * 1000;

function loadOfflineSchemes() {
    try {
        const raw = localStorage.getItem(SCHEMES_CACHE_KEY);
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        if (Date.now() - parsed.timestamp > SCHEMES_CACHE_TTL) {
            localStorage.removeItem(SCHEMES_CACHE_KEY);
            return null;
        }
        return parsed.schemes;
    } catch (e) {
        return null;
    }
}

function saveOfflineSchemes(schemes) {
    try {
        localStorage.setItem(SCHEMES_CACHE_KEY, JSON.stringify({
            schemes: schemes,
            timestamp: Date.now()
        }));
    } catch (e) {}
}

function fetchAndCacheSchemes() {
    if (!isOnline()) return;
    const existing = loadOfflineSchemes();
    if (existing && existing.length > 0) return;

    fetch(`${API_URL}/schemes`)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
            if (data && data.schemes) {
                saveOfflineSchemes(data.schemes);
            }
        })
        .catch(() => {});
}

function searchOfflineSchemes(query) {
    const schemes = loadOfflineSchemes();
    if (!schemes || schemes.length === 0) return [];

    const queryLower = query.toLowerCase();
    const words = queryLower.split(/\s+/).filter(w => w.length >= 3);
    const profile = loadFarmerProfile();

    const scored = [];
    for (const s of schemes) {
        const name = (s.name || "").toLowerCase();
        const desc = (s.description || "").toLowerCase();
        const target = (s.target_group || "").toLowerCase();
        const elig = (s.eligibility || "").toLowerCase();
        const benefits = (s.benefits || "").toLowerCase();
        const stateName = (s.state || (s.states && s.states[0]) || "").toLowerCase();

        let score = 0;
        for (const w of words) {
            if (name.includes(w)) score += 3;
            else if (target.includes(w)) score += 2;
            else if (desc.includes(w) || elig.includes(w) || benefits.includes(w)) score += 1;
        }

        if (profile.state && stateName && profile.state.toLowerCase() === stateName) {
            score += 2;
        }

        const schemeType = s.type || s.scope || "";
        if (schemeType === "central") score += 0.5;

        if (score > 0) scored.push({ score, scheme: s });
    }

    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, 5).map(s => s.scheme);
}

const OFFLINE_LABELS = {
    hi: { noMatch: "मुझे आपके सवाल से संबंधित कोई विशेष योजना नहीं मिली। कृपया अधिक विवरण दें या नजदीकी CSC केंद्र से संपर्क करें।", intro: "आपके सवाल के आधार पर यहाँ कुछ सरकारी योजनाओं की जानकारी है:", benefits: "लाभ", eligibility: "पात्रता", helpline: "हेल्पलाइन", apply: "आवेदन", footer: "अधिक जानकारी के लिए नजदीकी CSC केंद्र से संपर्क करें।", commonSchemes: "कुछ सामान्य योजनाएं:" },
    bn: { noMatch: "আপনার প্রশ্নের সাথে কোনো নির্দিষ্ট প্রকল্প পাওয়া যায়নি। অনুগ্রহ করে আরও বিশদ দিন বা নিকটতম CSC কেন্দ্রে যোগাযোগ করুন।", intro: "আপনার প্রশ্নের ভিত্তিতে এখানে কিছু সরকারি প্রকল্পের তথ্য:", benefits: "সুবিধা", eligibility: "যোগ্যতা", helpline: "হেল্পলাইন", apply: "আবেদন", footer: "আরও তথ্যের জন্য নিকটতম CSC কেন্দ্রে যোগাযোগ করুন।", commonSchemes: "কিছু সাধারণ প্রকল্প:" },
    te: { noMatch: "మీ ప్రశ్నకు సంబంధించిన నిర్దిష్ట పథకం కనుగొనబడలేదు. దయచేసి మరిన్ని వివరాలు ఇవ్వండి లేదా సమీపంలోని CSC కేంద్రాన్ని సంప్రదించండి.", intro: "మీ ప్రశ్న ఆధారంగా ఇక్కడ కొన్ని ప్రభుత్వ పథకాల సమాచారం:", benefits: "ప్రయోజనాలు", eligibility: "అర్హత", helpline: "హెల్ప్‌లైన్", apply: "దరఖాస్తు", footer: "మరిన్ని వివరాల కోసం సమీపంలోని CSC కేంద్రాన్ని సంప్రదించండి.", commonSchemes: "కొన్ని సాధారణ పథకాలు:" },
    mr: { noMatch: "तुमच्या प्रश्नाशी संबंधित विशिष्ट योजना सापडली नाही. कृपया अधिक तपशील द्या किंवा जवळच्या CSC केंद्राशी संपर्क साधा.", intro: "तुमच्या प्रश्नावर आधारित काही सरकारी योजनांची माहिती:", benefits: "फायदे", eligibility: "पात्रता", helpline: "हेल्पलाइन", apply: "अर्ज", footer: "अधिक माहितीसाठी जवळच्या CSC केंद्राशी संपर्क साधा.", commonSchemes: "काही सामान्य योजना:" },
    ta: { noMatch: "உங்கள் கேள்விக்கு பொருத்தமான திட்டம் கிடைக்கவில்லை. மேலும் விவரங்கள் தரவும் அல்லது அருகிலுள்ள CSC மையத்தை தொடர்பு கொள்ளவும்.", intro: "உங்கள் கேள்வியின் அடிப்படையில் சில அரசு திட்டங்களின் தகவல்:", benefits: "நன்மைகள்", eligibility: "தகுதி", helpline: "ஹெல்ப்லைன்", apply: "விண்ணப்பம்", footer: "மேலும் விவரங்களுக்கு அருகிலுள்ள CSC மையத்தை தொடர்பு கொள்ளவும்.", commonSchemes: "சில பொதுவான திட்டங்கள்:" },
    gu: { noMatch: "તમારા પ્રશ્ન સાથે સંબંધિત ચોક્કસ યોજના મળી નથી. કૃપા કરીને વધુ વિગતો આપો અથવા નજીકના CSC કેન્દ્રનો સંપર્ક કરો.", intro: "તમારા પ્રશ્નના આધારે અહીં કેટલીક સરકારી યોજનાઓની માહિતી:", benefits: "ફાયદા", eligibility: "પાત્રતા", helpline: "હેલ્પલાઇન", apply: "અરજી", footer: "વધુ માહિતી માટે નજીકના CSC કેન્દ્રનો સંપર્ક કરો.", commonSchemes: "કેટલીક સામાન્ય યોજનાઓ:" },
    kn: { noMatch: "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ನಿರ್ದಿಷ್ಟ ಯೋಜನೆ ಕಂಡುಬಂದಿಲ್ಲ. ಹೆಚ್ಚಿನ ವಿವರಗಳನ್ನು ನೀಡಿ ಅಥವಾ ಹತ್ತಿರದ CSC ಕೇಂದ್ರವನ್ನು ಸಂಪರ್ಕಿಸಿ.", intro: "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯ ಆಧಾರದ ಮೇಲೆ ಕೆಲವು ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಮಾಹಿತಿ:", benefits: "ಪ್ರಯೋಜನಗಳು", eligibility: "ಅರ್ಹತೆ", helpline: "ಹೆಲ್ಪ್‌ಲೈನ್", apply: "ಅರ್ಜಿ", footer: "ಹೆಚ್ಚಿನ ವಿವರಗಳಿಗಾಗಿ ಹತ್ತಿರದ CSC ಕೇಂದ್ರವನ್ನು ಸಂಪರ್ಕಿಸಿ.", commonSchemes: "ಕೆಲವು ಸಾಮಾನ್ಯ ಯೋಜನೆಗಳು:" },
    ml: { noMatch: "നിങ്ങളുടെ ചോദ്യവുമായി ബന്ധപ്പെട്ട നിർദ്ദിഷ്ട പദ്ധതി കണ്ടെത്താനായില്ല. കൂടുതൽ വിവരങ്ങൾ നൽകുക അല്ലെങ്കിൽ അടുത്തുള്ള CSC കേന്ദ്രം സന്ദർശിക്കുക.", intro: "നിങ്ങളുടെ ചോദ്യത്തിന്റെ അടിസ്ഥാനത്തിൽ ചില സർക്കാർ പദ്ധതികളുടെ വിവരങ്ങൾ:", benefits: "ആനുകൂല്യങ്ങൾ", eligibility: "യോഗ്യത", helpline: "ഹെൽപ്‌ലൈൻ", apply: "അപേക്ഷ", footer: "കൂടുതൽ വിവരങ്ങൾക്ക് അടുത്തുള്ള CSC കേന്ദ്രം സന്ദർശിക്കുക.", commonSchemes: "ചില സാധാരണ പദ്ധതികൾ:" },
    pa: { noMatch: "ਤੁਹਾਡੇ ਸਵਾਲ ਨਾਲ ਸੰਬੰਧਿਤ ਕੋਈ ਵਿਸ਼ੇਸ਼ ਯੋਜਨਾ ਨਹੀਂ ਮਿਲੀ। ਕਿਰਪਾ ਕਰਕੇ ਹੋਰ ਵੇਰਵੇ ਦਿਓ ਜਾਂ ਨੇੜਲੇ CSC ਕੇਂਦਰ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।", intro: "ਤੁਹਾਡੇ ਸਵਾਲ ਦੇ ਆਧਾਰ 'ਤੇ ਕੁਝ ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ ਦੀ ਜਾਣਕਾਰੀ:", benefits: "ਲਾਭ", eligibility: "ਯੋਗਤਾ", helpline: "ਹੈਲਪਲਾਈਨ", apply: "ਅਰਜ਼ੀ", footer: "ਹੋਰ ਜਾਣਕਾਰੀ ਲਈ ਨੇੜਲੇ CSC ਕੇਂਦਰ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।", commonSchemes: "ਕੁਝ ਆਮ ਯੋਜਨਾਵਾਂ:" },
    or: { noMatch: "ଆପଣଙ୍କ ପ୍ରଶ୍ନ ସହ ସମ୍ପର୍କିତ କୌଣସି ନିର୍ଦ୍ଦିଷ୍ଟ ଯୋଜନା ମିଳିଲା ନାହିଁ। ଦୟାକରି ଅଧିକ ବିବରଣୀ ଦିଅନ୍ତୁ ବା ନିକଟସ୍ଥ CSC କେନ୍ଦ୍ରକୁ ଯୋଗାଯୋଗ କରନ୍ତୁ।", intro: "ଆପଣଙ୍କ ପ୍ରଶ୍ନ ଆଧାରରେ ଏଠାରେ କିଛି ସରକାରୀ ଯୋଜନାର ତଥ୍ୟ:", benefits: "ଲାଭ", eligibility: "ଯୋଗ୍ୟତା", helpline: "ହେଲ୍ପଲାଇନ୍", apply: "ଆବେଦନ", footer: "ଅଧିକ ତଥ୍ୟ ପାଇଁ ନିକଟସ୍ଥ CSC କେନ୍ଦ୍ରକୁ ଯୋଗାଯୋଗ କରନ୍ତୁ।", commonSchemes: "କିଛି ସାଧାରଣ ଯୋଜନା:" },
    en: { noMatch: "I couldn't find a specific scheme matching your question. Please try asking in more detail or visit your nearest CSC center.", intro: "Based on your question, here are some relevant government schemes:", benefits: "Benefits", eligibility: "Eligibility", helpline: "Helpline", apply: "Apply", footer: "For more details, visit your nearest CSC center or Gram Panchayat office.", commonSchemes: "Some common schemes:" },
};

function getOfflineLabels() {
    const lang = getLang();
    return OFFLINE_LABELS[lang] || OFFLINE_LABELS.en;
}

function generateOfflineResponse(query, matchedSchemes) {
    const lang = getLang();
    const labels = getOfflineLabels();

    const emergency = loadEmergencyInfo();
    const helplineText = emergency.helplines.slice(0, 3)
        .map(h => `📞 ${h.name}: ${h.number}`).join("\n");

    if (!matchedSchemes || matchedSchemes.length === 0) {
        const fallbackAnswer = `${labels.noMatch}\n\n${labels.commonSchemes}\n• PM-KISAN (₹6,000) - pmkisan.gov.in\n• Ayushman Bharat (₹5 lakh) - pmjay.gov.in\n• PM Awas Yojana - pmayg.nic.in\n\n${labels.helpline}:\n${helplineText}`;

        return {
            intent: "scheme_query",
            answer: fallbackAnswer,
            recommended_schemes: [],
            response_language: lang,
            doc_links: [],
            nearest_centers: [],
        };
    }

    const top = matchedSchemes.slice(0, 3);
    let answerParts = [];
    answerParts.push(`${labels.intro}\n`);

    for (let i = 0; i < top.length; i++) {
        const s = top[i];
        const name = s.name || "Unknown";
        const schemeType = s.type || s.scope || "";
        const state = s.state || (s.states && s.states[0]) || "";
        let badge = "";
        if (schemeType === "central") badge = ` [${t("central")}]`;
        else if (schemeType === "state" && state) badge = ` [${state}]`;

        answerParts.push(`\n${i + 1}. ${name}${badge}`);
        if (s.description) {
            const desc = s.description.length > 200 ? s.description.substring(0, 197) + "..." : s.description;
            answerParts.push(`   ${desc}`);
        }
        if (s.benefits) {
            answerParts.push(`   💰 ${labels.benefits}: ${s.benefits}`);
        }
        if (s.eligibility) {
            answerParts.push(`   ✅ ${labels.eligibility}: ${s.eligibility}`);
        }
        if (s.helpline) {
            answerParts.push(`   📞 ${labels.helpline}: ${s.helpline}`);
        }
        const appUrl = s.application_url || "";
        if (appUrl.startsWith("http")) {
            answerParts.push(`   🔗 ${labels.apply}: ${appUrl}`);
        }
    }

    answerParts.push(`\n${helplineText}`);
    answerParts.push(`\n${labels.footer}`);

    const recommendations = matchedSchemes.slice(0, 5).map(s => ({
        name: s.name,
        description: s.description || "",
        type: s.type || s.scope || null,
        state: s.state || (s.states && s.states[0]) || null,
        documents_links: s.documents_links || (s.application_url ? [s.application_url] : []),
    }));

    return {
        intent: "scheme_query",
        answer: answerParts.join("\n"),
        recommended_schemes: recommendations,
        response_language: lang,
        doc_links: [],
        nearest_centers: [],
    };
}

let currentSchemeFilter = 'all';

function setSchemeFilter(filter) {
    currentSchemeFilter = filter;
    document.querySelectorAll('.scheme-filter-btn').forEach(btn => {
        btn.classList.remove('bg-primary', 'text-white', 'shadow-sm', 'active');
        btn.classList.add('bg-slate-100', 'text-slate-500');
    });
    const activeBtn = document.getElementById('filter-' + filter);
    if (activeBtn) {
        activeBtn.classList.add('bg-primary', 'text-white', 'shadow-sm', 'active');
        activeBtn.classList.remove('bg-slate-100', 'text-slate-500');
    }
    renderSuggestionChips();
}

function updateStateFilterButton() {
    const profile = loadFarmerProfile();
    const stateBtn = document.getElementById('filter-state');
    if (stateBtn) {
        if (profile.state) {
            stateBtn.textContent = profile.state;
            stateBtn.classList.remove('hidden');
        } else {
            stateBtn.classList.add('hidden');
            if (currentSchemeFilter === 'state') {
                setSchemeFilter('all');
            }
        }
    }
}

function getSeasonalChips() {
    const month = new Date().getMonth() + 1;
    const isKharif = month >= 6 && month <= 10;
    const isRabi   = month >= 11 || month <= 3;

    const centralChips = [
        { icon: "payments",          color: "text-green-600",  label: "PM-KISAN",              query: "PM-KISAN scheme eligibility and benefits", type: "central" },
        { icon: "credit_card",       color: "text-blue-500",   label: "Kisan Credit Card",      query: "Kisan Credit Card scheme details", type: "central" },
        { icon: "shield",            color: "text-yellow-600", label: "Crop Insurance (PMFBY)", query: "PMFBY crop insurance scheme benefits", type: "central" },
        { icon: "storefront",        color: "text-orange-500", label: "Mandi Prices",           query: "Mandi prices today for my crop", type: "central" },
        { icon: "eco",               color: "text-teal-500",   label: "Soil Health Card",       query: "Soil Health Card scheme how to get", type: "central" },
        { icon: "grass",             color: "text-lime-600",   label: "Free Seed Scheme",       query: "Free seed distribution scheme for farmers", type: "central" },
    ];

    const kharifChips = [
        { icon: "water_drop",         color: "text-blue-600",   label: "Paddy Farming Tips",  query: "Paddy cultivation tips for Kharif season", type: "central" },
        { icon: "energy_savings_leaf", color: "text-green-500", label: "Soybean Schemes",     query: "Government schemes for soybean farmers", type: "central" },
    ];

    const rabiChips = [
        { icon: "grain",             color: "text-amber-600",  label: "Wheat MSP",            query: "Wheat minimum support price MSP details", type: "central" },
        { icon: "spa",               color: "text-yellow-500", label: "Mustard Schemes",      query: "Government schemes for mustard farmers", type: "central" },
    ];

    const seasonal = isKharif ? kharifChips : isRabi ? rabiChips : [];
    const combined = [...centralChips];
    seasonal.forEach(chip => {
        combined.splice(Math.floor(Math.random() * (combined.length + 1)), 0, chip);
    });

    const profile = loadFarmerProfile();
    if (profile.state) {
        combined.push(
            { icon: "location_on", color: "text-purple-500", label: profile.state + " Schemes", query: "Government schemes for farmers in " + profile.state, type: "state" },
            { icon: "agriculture", color: "text-emerald-500", label: profile.state + " Agriculture", query: "Agriculture schemes in " + profile.state, type: "state" }
        );
    }

    if (currentSchemeFilter === 'central') {
        return combined.filter(c => c.type === 'central').slice(0, 8);
    } else if (currentSchemeFilter === 'state') {
        return combined.filter(c => c.type === 'state').slice(0, 8);
    }
    return combined.slice(0, 8);
}

function renderSuggestionChips() {
    const container = document.getElementById("suggestion-chips");
    if (!container) return;
    const chips = getSeasonalChips();
    container.innerHTML = chips.map(chip => `
        <button onclick="useChip(${JSON.stringify(chip.query).replace(/"/g, '&quot;')})"
            class="px-2.5 py-1.5 bg-white border border-slate-200 rounded-full text-[12px] font-medium text-slate-600 shadow-sm active:bg-slate-50 transition-colors flex items-center gap-1">
            <span class="material-symbols-outlined text-[13px] ${chip.color}">${chip.icon}</span>
            ${chip.label}
        </button>
    `).join("");
}

function useChip(query) {
    document.getElementById("text-input").value = query;
    sendTextMessage();
}

function handleEnterKeyPress(event) {
    if (event.key === "Enter") {
        sendTextMessage();
    }
}

let conversationToken = 0;

async function sendTextMessage() {
    const inputField = document.getElementById("text-input");
    const query = inputField.value.trim();
    if (!query) return;
    inputField.value = "";

    if (window.stopSpeaking) window.stopSpeaking();

    addMessageToChat(query, "user");
    conversationHistory.push({ role: "user", content: query });
    if (conversationHistory.length > MAX_CONVERSATION_HISTORY) {
        conversationHistory = conversationHistory.slice(-MAX_CONVERSATION_HISTORY);
    }
    await processQuery(query);
}

function startNewConversation() {
    conversationHistory = [];
    conversationToken++;
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = `
        <div class="flex items-start gap-2.5 max-w-[90%] message-fade-in">
            <div class="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-white shrink-0 mt-1">
                <span class="material-symbols-outlined text-[15px]" style="font-variation-settings: 'FILL' 1">agriculture</span>
            </div>
            <div class="flex flex-col gap-1">
                <span class="text-[11px] font-medium text-slate-400 ml-0.5">SaarthiAI</span>
                <div class="bg-slate-50 rounded-2xl rounded-tl-md px-4 py-3">
                    <p class="text-[14px] leading-relaxed text-slate-700">
                        How can I help you today?<br/>
                        <span class="text-slate-500 mt-1 block">${getLang() === 'hi' ? 'मैं आज आपकी कैसे मदद कर सकता हूँ?' : getLang() === 'en' ? 'Ask me about any government scheme!' : 'मैं आज आपकी कैसे मदद कर सकता हूँ?'}</span>
                    </p>
                </div>
            </div>
        </div>`;
    renderSuggestionChips();
    if (window.stopSpeaking) window.stopSpeaking();
}

function trackAssistantResponse(answer) {
    if (answer) {
        conversationHistory.push({ role: "assistant", content: answer });
        if (conversationHistory.length > MAX_CONVERSATION_HISTORY) {
            conversationHistory = conversationHistory.slice(-MAX_CONVERSATION_HISTORY);
        }
    }
}

async function processQuery(query) {
    const resolvedLang = getLang();
    const profileSnapshot = getFarmerProfileSnapshot();
    const cacheKey = buildCacheKey(query, resolvedLang, profileSnapshot);
    const myToken = conversationToken;

    showStatus(t("thinking"));

    if (!isOnline()) {
        const exact = getCachedResponse(cacheKey);
        const best  = exact || findBestCachedAnswer(query, resolvedLang);
        if (myToken !== conversationToken) return;
        if (best) {
            trackAssistantResponse(best.answer);
            displayResponse(best, true);
            addOfflineBanner(t("offline"));
        } else {
            const matched = searchOfflineSchemes(query);
            const offlineData = generateOfflineResponse(query, matched);
            trackAssistantResponse(offlineData.answer);
            displayResponse(offlineData, true, true);
            addOfflineBanner(t("noCache"));
        }
        showStatus("");
        return;
    }

    const profile = loadFarmerProfile();
    try {
        const historyToSend = conversationHistory.length > 1
            ? conversationHistory.slice(0, -1)
            : [];

        const response = await fetch(`${API_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query,
                language: resolvedLang,
                occupation: "farmer",
                state: profile.state || undefined,
                income: profile.income ? parseInt(profile.income) || undefined : undefined,
                crop: profile.crop || undefined,
                land_size: profile.landSize || undefined,
                conversation_history: historyToSend.length > 0 ? historyToSend : undefined,
            })
        });

        if (!response.ok) throw new Error("server_error");

        const data = await response.json();
        if (myToken !== conversationToken) return;
        trackAssistantResponse(data.answer);
        cacheResponse(cacheKey, data, query, resolvedLang);
        displayResponse(data, false);
    } catch (error) {
        if (myToken !== conversationToken) return;
        const isNetworkErr = !navigator.onLine || error instanceof TypeError || error.message === "Failed to fetch" || error.name === "AbortError";

        const exact   = getCachedResponse(cacheKey);
        const fallback = exact || findBestCachedAnswer(query, resolvedLang);
        if (fallback) {
            trackAssistantResponse(fallback.answer);
            displayResponse(fallback, true);
            addOfflineBanner(isNetworkErr ? t("offline") : t("serverError"));
        } else {
            const matched = searchOfflineSchemes(query);
            if (matched.length > 0) {
                const offlineData = generateOfflineResponse(query, matched);
                trackAssistantResponse(offlineData.answer);
                displayResponse(offlineData, true, true);
                addOfflineBanner(isNetworkErr ? t("noCache") : t("serverError"));
            } else {
                addMessageToChat(isNetworkErr ? t("noCache") : t("serverError"), "bot");
            }
        }
    } finally {
        showStatus("");
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function sanitizeUrl(url) {
    if (!url || typeof url !== 'string') return '';
    try {
        const parsed = new URL(url);
        if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return '';
        return parsed.href;
    } catch(e) { return ''; }
}

function renderMarkdown(str) {
    if (!str) return '';
    let html = escapeHtml(str);
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/(https?:\/\/[^\s<]+)/g, function(url) {
        const safe = sanitizeUrl(url);
        if (safe) {
            return '<a href="' + escapeHtml(safe) + '" target="_blank" rel="noopener noreferrer" class="text-primary hover:underline break-all">' + escapeHtml(safe) + '</a>';
        }
        return url;
    });
    html = html.replace(/^(#{1,3})\s+(.+)$/gm, (match, hashes, text) => {
        const level = hashes.length;
        const sizes = { 1: 'text-[16px] font-bold', 2: 'text-[15px] font-semibold', 3: 'text-[14px] font-semibold' };
        return `<div class="${sizes[level] || sizes[3]} text-slate-800 mt-2 mb-1">${text}</div>`;
    });
    html = html.replace(/^─+$/gm, '<hr class="border-slate-200 my-2">');
    return html;
}

function displayResponse(data, isCached, isOfflineGenerated) {
    let badgeText = "";
    if (isOfflineGenerated) {
        badgeText = t("offlineAnswer");
    } else if (isCached) {
        badgeText = t("savedAnswer");
    }
    const savedBadge = badgeText
        ? `<span class="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5 mt-2">
               <span class="material-symbols-outlined text-[13px]">${isOfflineGenerated ? 'wifi_off' : 'bookmark'}</span>${badgeText}
           </span>`
        : "";

    let htmlContent = `
        <div class="flex items-start gap-2.5 max-w-[90%] message-fade-in mb-3">
            <div class="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-white shrink-0 mt-1">
                <span class="material-symbols-outlined text-[15px]" style="font-variation-settings: 'FILL' 1">agriculture</span>
            </div>
            <div class="flex flex-col gap-1">
                <span class="text-[11px] font-medium text-slate-400 ml-0.5">SaarthiAI</span>
                <div class="bg-slate-50 rounded-2xl rounded-tl-md px-4 py-3">
                    <div class="text-[14px] leading-relaxed text-slate-700 message-content whitespace-pre-line">${renderMarkdown(data.answer)}</div>
                    ${savedBadge}
                </div>
            </div>
        </div>
    `;

    if (window.speakText && data.answer) {
        window.speakText(data.answer, data.response_language || getLang());
    }

    if (data.recommended_schemes && data.recommended_schemes.length > 0) {
        htmlContent += `<div class="flex flex-col gap-2 mb-3 ml-9"><span class="text-[12px] font-semibold text-slate-500 flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">auto_awesome</span>${t("schemesHeading")}</span>`;
        data.recommended_schemes.forEach(scheme => {
            const typeBadge = scheme.type
                ? `<span class="inline-flex items-center text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${scheme.type === 'central' ? 'bg-blue-50 text-blue-600' : 'bg-purple-50 text-purple-600'}">${scheme.type === 'central' ? t("central") : scheme.state || 'State'}</span>`
                : '';
            const docLinks = (scheme.documents_links && scheme.documents_links.length > 0)
                ? `<div class="flex flex-wrap gap-1 mt-1.5">${scheme.documents_links.map(url => { const safe = sanitizeUrl(url); return safe ? `<a href="${escapeHtml(safe)}" target="_blank" rel="noopener" class="inline-flex items-center gap-0.5 text-[10px] text-primary hover:underline font-medium"><span class="material-symbols-outlined text-[11px]">open_in_new</span>${t("officialLink")}</a>` : ''; }).join('')}</div>`
                : '';
            htmlContent += `
                <div class="scheme-card bg-white border border-slate-200 rounded-xl p-3 transition-all">
                    <div class="flex items-center gap-2 mb-1">
                        <h4 class="font-semibold text-primary text-[13px] flex-1 leading-tight">${escapeHtml(scheme.name)}</h4>
                        ${typeBadge}
                    </div>
                    <p class="text-[12px] text-slate-500 leading-snug">${escapeHtml(scheme.description)}</p>
                    ${docLinks}
                </div>
            `;
        });
        htmlContent += '</div>';
    }

    if (data.doc_links && data.doc_links.length > 0) {
        htmlContent += `<div class="flex flex-col gap-1.5 mb-3 ml-9"><span class="text-[12px] font-semibold text-slate-500 flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">link</span>${t("usefulLinks")}</span>`;
        data.doc_links.forEach(link => {
            const safeUrl = sanitizeUrl(link.url);
            if (safeUrl) {
                htmlContent += `
                    <a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener" class="flex items-center gap-2 bg-white border border-slate-200 rounded-xl p-2.5 hover:border-primary/40 transition-colors no-underline">
                        <span class="material-symbols-outlined text-primary text-[16px] shrink-0">open_in_new</span>
                        <span class="text-[12px] text-slate-600 font-medium leading-snug">${escapeHtml(link.title)}</span>
                    </a>
                `;
            }
        });
        htmlContent += '</div>';
    }

    if (data.nearest_centers && data.nearest_centers.length > 0) {
        htmlContent += `<div class="flex flex-col gap-1.5 mb-3 ml-9"><span class="text-[12px] font-semibold text-slate-500 flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">location_on</span>${t("nearbyCenters")}</span>`;
        data.nearest_centers.forEach(center => {
            const phoneNum = center.phone ? escapeHtml(center.phone.replace(/[^0-9+\-\s\/]/g, '')) : '';
            const phone = phoneNum ? `<a href="tel:${phoneNum}" class="inline-flex items-center gap-0.5 text-primary text-[11px] font-medium"><span class="material-symbols-outlined text-[13px]">call</span>${escapeHtml(center.phone)}</a>` : '';
            const safeMapsUrl = sanitizeUrl(center.maps_url);
            const mapsLink = safeMapsUrl ? `<a href="${escapeHtml(safeMapsUrl)}" target="_blank" rel="noopener" class="inline-flex items-center gap-0.5 text-primary text-[11px] font-medium hover:underline"><span class="material-symbols-outlined text-[13px]">map</span>${t("openMaps")}</a>` : '';
            htmlContent += `
                <div class="bg-white border border-slate-200 rounded-xl p-2.5 transition-all hover:border-slate-300">
                    <div class="flex items-start justify-between gap-2">
                        <div class="flex-1 min-w-0">
                            <h4 class="font-semibold text-[13px] text-slate-700 leading-tight">${escapeHtml(center.name)}</h4>
                            ${center.type ? `<span class="text-[10px] text-slate-400 font-medium">${escapeHtml(center.type)}</span>` : ''}
                        </div>
                        <div class="flex flex-col items-end gap-1 shrink-0">
                            ${phone}
                            ${mapsLink}
                        </div>
                    </div>
                    ${center.address ? `<p class="text-[11px] text-slate-400 mt-1 leading-snug">${escapeHtml(center.address)}${center.district ? ', ' + escapeHtml(center.district) : ''}</p>` : ''}
                </div>
            `;
        });
        htmlContent += '</div>';
    }

    addRawHtmlToChat(htmlContent, "bot");
}

function addOfflineBanner(msg) {
    const html = `
        <div class="mx-auto mb-3 px-3 py-2 bg-amber-50 border border-amber-200 rounded-xl text-[12px] text-amber-700 flex items-center gap-2 message-fade-in">
            <span class="material-symbols-outlined text-[14px]">wifi_off</span>
            ${msg}
        </div>
    `;
    addRawHtmlToChat(html, "bot");
}

function addMessageToChat(text, sender) {
    let htmlContent = "";
    if (sender === "user") {
        htmlContent = `
        <div class="flex items-end justify-end gap-2.5 w-full mb-3 message-fade-in">
            <div class="flex flex-col gap-1 items-end max-w-[85%]">
                <span class="text-[11px] font-medium text-slate-400 mr-0.5">You</span>
                <div class="bg-primary text-white rounded-2xl rounded-br-md px-4 py-2.5">
                    <p class="text-[14px] leading-relaxed">${escapeHtml(text)}</p>
                </div>
            </div>
        </div>`;
    } else {
        htmlContent = `
        <div class="flex items-start gap-2.5 max-w-[90%] message-fade-in mb-3">
            <div class="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-white shrink-0 mt-1">
                <span class="material-symbols-outlined text-[15px]" style="font-variation-settings: 'FILL' 1">agriculture</span>
            </div>
            <div class="flex flex-col gap-1">
                <span class="text-[11px] font-medium text-slate-400 ml-0.5">SaarthiAI</span>
                <div class="bg-slate-50 rounded-2xl rounded-tl-md px-4 py-3">
                    <p class="text-[14px] leading-relaxed text-slate-700">${escapeHtml(text)}</p>
                </div>
            </div>
        </div>`;
    }
    addRawHtmlToChat(htmlContent, sender);
}

function addRawHtmlToChat(htmlContent, sender) {
    const chatBox = document.getElementById("chat-box");
    chatBox.insertAdjacentHTML("beforeend", htmlContent);
    const chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showStatus(text) {
    document.getElementById("status-indicator").innerText = text;
}

document.addEventListener("DOMContentLoaded", () => {
    pruneOldCacheEntries();
    updateConnectivityPill();
    if (!isOnline()) showOfflineFeatureBanner();
    updateStateFilterButton();
    renderSuggestionChips();
    fetchAndCacheSchemes();

    document.getElementById("avatar-btn").addEventListener("click", openProfileDrawer);
    document.getElementById("profile-save-btn").addEventListener("click", () => {
        saveProfileFromDrawer();
        updateStateFilterButton();
        renderSuggestionChips();
    });
    document.getElementById("profile-cancel-btn").addEventListener("click", closeProfileDrawer);
    document.getElementById("profile-overlay").addEventListener("click", closeProfileDrawer);

    document.getElementById("language-select").addEventListener("change", () => {
        updateConnectivityPill();
        updateMicHint();
        updatePlaceholder();
    });

    updatePlaceholder();

    if (isOnline()) {
        preCachePopularQueries();
    }
});

function updatePlaceholder() {
    const input = document.getElementById("text-input");
    if (input) {
        input.placeholder = t("typeMessage");
    }
}

function preCachePopularQueries() {
    const PRECACHE_KEY = 'saarthi_precached';
    if (localStorage.getItem(PRECACHE_KEY)) return;

    const popularQueries = [
        "PM-KISAN scheme eligibility and benefits",
        "Kisan Credit Card scheme details",
        "PMFBY crop insurance scheme benefits",
        "How to apply for PM-KISAN step by step",
        "Soil Health Card scheme how to get",
        "PM Awas Yojana Gramin eligibility",
        "Ayushman Bharat health insurance for farmers",
        "PM Fasal Bima Yojana claim process",
    ];

    const profile = loadFarmerProfile();
    const resolvedLang = getLang();
    const profileSnapshot = getFarmerProfileSnapshot();

    popularQueries.forEach(query => {
        const cacheKey = buildCacheKey(query, resolvedLang, profileSnapshot);
        if (getCachedResponse(cacheKey)) return;

        fetch(`${API_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query,
                language: resolvedLang,
                occupation: "farmer",
                state: profile.state || undefined,
                income: profile.income ? parseInt(profile.income) || undefined : undefined,
                crop: profile.crop || undefined,
                land_size: profile.landSize || undefined,
            })
        }).then(res => {
            if (res.ok) return res.json();
            throw new Error('precache_fail');
        }).then(data => {
            cacheResponse(cacheKey, data, query, resolvedLang);
        }).catch(() => {});
    });

    localStorage.setItem(PRECACHE_KEY, Date.now().toString());
}

function updateMicHint() {
    const hint   = document.getElementById("mic-unsupported-hint");
    const micBtn = document.getElementById("mic-btn");
    const msg    = t("micUnsupported");
    if (hint && !hint.classList.contains("hidden")) {
        hint.textContent = msg;
    }
    if (micBtn && micBtn.disabled) {
        micBtn.title = msg;
        micBtn.setAttribute("aria-label", msg);
    }
}

window.updateMicHint = updateMicHint;
window.showStatus = showStatus;
