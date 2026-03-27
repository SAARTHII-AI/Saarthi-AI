const API_URL = ""; 
const MAX_CONVERSATION_HISTORY = 5;

let conversationHistory = [];

const I18N = {
    hi: {
        thinking: "सोच रहा हूँ...",
        listening: "सुन रहा हूँ...",
        understood: "समझ गया!",
        online: "ऑनलाइन",
        offline: "ऑफलाइन (सिर्फ सेव की गई जानकारी)",
        noCache: "इंटरनेट नहीं है और यह जानकारी सेव नहीं है।",
        serverError: "सर्वर में समस्या है। कृपया फिर से कोशिश करें।",
        offlineAnswer: "ऑफलाइन जवाब",
        savedAnswer: "सेव किया गया",
        schemesHeading: "आपके लिए योजनाएं",
        usefulLinks: "उपयोगी लिंक",
        nearbyCenters: "नजदीकी केंद्र",
        openMaps: "मैप्स में देखें",
        officialLink: "ऑफिशियल लिंक",
        central: "केंद्र सरकार",
        typeMessage: "अपना सवाल यहाँ लिखें...",
        micUnsupported: "इस ब्राउज़र में बोलने की सुविधा नहीं है",
        hearError: "माफ़ कीजिये, मैं सुन नहीं पाया।",
    },
    en: {
        thinking: "Thinking...",
        listening: "Listening...",
        understood: "Understood!",
        online: "Online",
        offline: "Offline (Saved info only)",
        noCache: "No internet and no saved info found.",
        serverError: "Server error. Please try again later.",
        offlineAnswer: "Offline Response",
        savedAnswer: "Saved Response",
        schemesHeading: "Recommended Schemes",
        usefulLinks: "Useful Links",
        nearbyCenters: "Nearby Centers",
        openMaps: "Open in Maps",
        officialLink: "Official Link",
        central: "Central Govt",
        typeMessage: "Type your query here...",
        micUnsupported: "Microphone not supported on this browser",
        hearError: "Sorry, I couldn't hear you.",
    },
    bn: {
        thinking: "ভাবছি...",
        listening: "শুনছি...",
        understood: "বুঝেছি!",
        online: "অনলাইন",
        offline: "অফলাইন (সংরক্ষিত তথ্য মাত্র)",
        noCache: "ইন্টারনেট নেই এবং কোনো সংরক্ষিত তথ্য নেই।",
        serverError: "সার্ভারে যোগাযোগ করা যাচ্ছে না।",
        offlineAnswer: "অফলাইন উত্তর",
        savedAnswer: "সংরক্ষিত উত্তর",
        schemesHeading: "প্রস্তাবিত প্রকল্পসমূহ",
        usefulLinks: "দরকারি লিংক",
        nearbyCenters: "নিকটবর্তী কেন্দ্র",
        openMaps: "মানচিত্রে দেখুন",
        officialLink: "অফিসিয়াল লিংক",
        central: "কেন্দ্রীয়",
        typeMessage: "একটি বার্তা টাইপ করুন...",
        micUnsupported: "এই ব্রাউজারে ভয়েস ইনপুট সমর্থিত নয়।",
        hearError: "দুঃখিত, আমি শুনতে পাইনি।",
    },
    te: {
        thinking: "ఆలోచిస్తున్నాను...",
        listening: "వింటున్నాను...",
        understood: "అర్థమైంది!",
        online: "ఆన్‌లైన్",
        offline: "ఆఫ్‌లైన్ (సేవ్ చేసిన సమాచారం మాత్రమే)",
        noCache: "ఇంటర్నెట్ లేదు మరియు సేవ్ చేసిన సమాచారం లేదు.",
        serverError: "సర్వర్‌ను సంప్రదించడం సాధ్యం కాలేదు.",
        offlineAnswer: "ఆఫ్‌లైన్ సమాధానం",
        savedAnswer: "సేవ్ చేసిన సమాధానం",
        schemesHeading: "సిఫార్సు చేసిన పథకాలు",
        usefulLinks: "ఉపయోగకరమైన లింకులు",
        nearbyCenters: "సమీపంలోని కేంద్రాలు",
        openMaps: "మ్యాప్‌లో చూడండి",
        officialLink: "అధికారిక లింక్",
        central: "కేంద్ర",
        typeMessage: "సందేశం టైప్ చేయండి...",
        micUnsupported: "ఈ బ్రౌజర్‌లో వాయిస్ ఇన్‌పుట్ మద్దతు లేదు.",
        hearError: "క్షమించండి, నేను వినలేకపోయాను.",
    },
    mr: {
        thinking: "विचार करत आहे...",
        listening: "ऐकत आहे...",
        understood: "समजले!",
        online: "ऑनलाइन",
        offline: "ऑफलाइन (फक्त सहेजलेली माहिती)",
        noCache: "इंटरनेट नाही आणि सहेजलेली माहिती नाही.",
        serverError: "सर्व्हरशी संपर्क होऊ शकला नाही.",
        offlineAnswer: "ऑफलाइन उत्तर",
        savedAnswer: "जतन केलेले उत्तर",
        schemesHeading: "शिफारस केलेल्या योजना",
        usefulLinks: "उपयुक्त दुवे",
        nearbyCenters: "जवळचे केंद्र",
        openMaps: "नकाशावर पहा",
        officialLink: "अधिकृत दुवा",
        central: "केंद्र",
        typeMessage: "संदेश टाइप करा...",
        micUnsupported: "या ब्राउझरमध्ये व्हॉइस इनपुट समर्थित नाही.",
        hearError: "माफ करा, मला ऐकू आले नाही.",
    },
    ta: {
        thinking: "யோசிக்கிறேன்...",
        listening: "கேட்கிறேன்...",
        understood: "புரிந்தது!",
        online: "ஆன்லைன்",
        offline: "ஆஃப்லைன் (சேமிக்கப்பட்ட தகவல் மட்டும்)",
        noCache: "இணையம் இல்லை மற்றும் சேமிக்கப்பட்ட தகவல் இல்லை.",
        serverError: "சர்வரை தொடர்பு கொள்ள இயலவில்லை.",
        offlineAnswer: "ஆஃப்லைன் பதில்",
        savedAnswer: "சேமிக்கப்பட்ட பதில்",
        schemesHeading: "பரிந்துரைக்கப்பட்ட திட்டங்கள்",
        usefulLinks: "பயனுள்ள இணைப்புகள்",
        nearbyCenters: "அருகிலுள்ள மையங்கள்",
        openMaps: "வரைபடத்தில் பாருங்கள்",
        officialLink: "அதிகாரப்பூர்வ இணைப்பு",
        central: "மத்திய",
        typeMessage: "செய்தியை தட்டச்சு செய்யுங்கள்...",
        micUnsupported: "இந்த உலாவியில் குரல் உள்ளீடு ஆதரிக்கப்படவில்லை.",
        hearError: "மன்னிக்கவும், என்னால் கேட்க இயலவில்லை.",
    },
    gu: {
        thinking: "વિચારી રહ્યો છું...",
        listening: "સાંભળી રહ્યો છું...",
        understood: "સમજી ગયો!",
        online: "ઑનલાઇન",
        offline: "ઑફલાઇન (ફક્ત સાચવેલી માહિતી)",
        noCache: "ઇન્ટરનેટ નથી અને સાચવેલી માહિતી નથી.",
        serverError: "સર્વર સાથે સંપર્ક કરી શકાયો નહીં.",
        offlineAnswer: "ઑફલાઇન જવાબ",
        savedAnswer: "સાચવેલો જવાબ",
        schemesHeading: "ભલામણ કરેલી યોજનાઓ",
        usefulLinks: "ઉપયોગી લિંક્સ",
        nearbyCenters: "નજીકના કેન્દ્રો",
        openMaps: "નકશામાં જુઓ",
        officialLink: "અધિકૃત લિંક",
        central: "કેન્દ્ર",
        typeMessage: "સંદેશ ટાઇપ કરો...",
        micUnsupported: "આ બ્રાઉઝરમાં અવાજ ઇનપુટ સમર્થિત નથી.",
        hearError: "માફ કરશો, હું સાંભળી શક્યો નહીં.",
    },
    kn: {
        thinking: "ಯೋಚಿಸುತ್ತಿದ್ದೇನೆ...",
        listening: "ಕೇಳುತ್ತಿದ್ದೇನೆ...",
        understood: "ಅರ್ಥವಾಯಿತು!",
        online: "ಆನ್‌ಲೈನ್",
        offline: "ಆಫ್‌ಲೈನ್ (ಉಳಿಸಿದ ಮಾಹಿತಿ ಮಾತ್ರ)",
        noCache: "ಇಂಟರ್ನೆಟ್ ಇಲ್ಲ ಮತ್ತು ಉಳಿಸಿದ ಮಾಹಿತಿ ಇಲ್ಲ.",
        serverError: "ಸರ್ವರ್ ಅನ್ನು ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
        offlineAnswer: "ಆಫ್‌ಲೈನ್ ಉತ್ತರ",
        savedAnswer: "ಉಳಿಸಿದ ಉತ್ತರ",
        schemesHeading: "ಶಿಫಾರಸು ಮಾಡಿದ ಯೋಜನೆಗಳು",
        usefulLinks: "ಉಪಯುಕ್ತ ಲಿಂಕ್‌ಗಳು",
        nearbyCenters: "ಹತ್ತಿರದ ಕೇಂದ್ರಗಳು",
        openMaps: "ನಕ್ಷೆಯಲ್ಲಿ ನೋಡಿ",
        officialLink: "ಅಧಿಕೃತ ಲಿಂಕ್",
        central: "ಕೇಂದ್ರ",
        typeMessage: "ಸಂದೇಶ ಟೈಪ್ ಮಾಡಿ...",
        micUnsupported: "ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಬೆಂಬಲಿತವಲ್ಲ.",
        hearError: "ಕ್ಷಮಿಸಿ, ನನಗೆ ಕೇಳಲಾಗಲಿಲ್ಲ.",
    },
    or: {
        thinking: "ଚିନ୍ତା କରୁଛି...",
        listening: "ଶୁଣୁଛି...",
        understood: "ବୁଝିଗଲି!",
        online: "ଅନଲାଇନ୍",
        offline: "ଅଫଲାଇନ୍ (ସଞ୍ଚିତ ତଥ୍ୟ ମାତ୍ର)",
        noCache: "ଇଣ୍ଟର୍ନେଟ୍ ନାହିଁ ଏବଂ ସଞ୍ଚିତ ତଥ୍ୟ ନାହିଁ।",
        serverError: "ସର୍ଭର ସହ ଯୋଗାଯୋଗ ହୋଇପାରିଲା ନାହିଁ।",
        offlineAnswer: "ଅଫଲାଇନ୍ ଉତ୍ତର",
        savedAnswer: "ସଞ୍ଚିତ ଉତ୍ତର",
        schemesHeading: "ପରାମର୍ଶିତ ଯୋଜନାଗୁଡ଼ିକ",
        usefulLinks: "ଉପଯୋଗୀ ଲିଙ୍କ",
        nearbyCenters: "ନିକଟସ୍ଥ କେନ୍ଦ୍ର",
        openMaps: "ମାନଚିତ୍ରରେ ଦେଖନ୍ତୁ",
        officialLink: "ଅଧିକୃତ ଲିଙ୍କ",
        central: "କେନ୍ଦ୍ର",
        typeMessage: "ଏକ ସନ୍ଦେଶ ଟାଇପ୍ କରନ୍ତୁ...",
        micUnsupported: "ଏହି ବ୍ରାଉଜରରେ ଭଏସ୍ ଇନପୁଟ୍ ସମର୍ଥିତ ନୁହେଁ।",
        hearError: "କ୍ଷମା କରନ୍ତୁ, ମୁଁ ଶୁଣିପାରିଲି ନାହିଁ।",
    },
    ml: {
        thinking: "ആലോചിക്കുന്നു...",
        listening: "കേൾക്കുന്നു...",
        understood: "മനസ്സിലായി!",
        online: "ഓൺലൈൻ",
        offline: "ഓഫ്‌ലൈൻ (സേവ് ചെയ്ത വിവരം മാത്രം)",
        noCache: "ഇന്റർനെറ്റ് ഇല്ല, സേവ് ചെയ്ത വിവരവും ഇല്ല.",
        serverError: "സെർവറുമായി ബന്ധപ്പെടാൻ കഴിയുന്നില്ല.",
        offlineAnswer: "ഓഫ്‌ലൈൻ ഉത്തരം",
        savedAnswer: "സേവ് ചെയ്ത ഉത്തരം",
        schemesHeading: "ശുപാർശ ചെയ്ത പദ്ധതികൾ",
        usefulLinks: "ഉപയോഗപ്രദമായ ലിങ്കുകൾ",
        nearbyCenters: "സമീപത്തുള്ള കേന്ദ്രങ്ങൾ",
        openMaps: "മാപ്പിൽ കാണുക",
        officialLink: "ഔദ്യോഗിക ലിങ്ക്",
        central: "കേന്ദ്ര",
        typeMessage: "ഒരു സന്ദേശം ടൈപ്പ് ചെയ്യുക...",
        micUnsupported: "ഈ ബ്രൗസറിൽ വോയ്‌സ് ഇൻപുട്ട് പിന്തുണയ്ക്കുന്നില്ല.",
        hearError: "ക്ഷമിക്കണം, എനിക്ക് കേൾക്കാൻ കഴിഞ്ഞില്ല.",
    },
    pa: {
        thinking: "ਸੋਚ ਰਿਹਾ ਹਾਂ...",
        listening: "ਸੁਣ ਰਿਹਾ ਹਾਂ...",
        understood: "ਸਮਝ ਲਿਆ!",
        online: "ਔਨਲਾਈਨ",
        offline: "ਔਫਲਾਈਨ (ਸੰਭਾਲੀ ਹੋਈ ਜਾਣਕਾਰੀ ਹੀ)",
        noCache: "ਇੰਟਰਨੈੱਟ ਨਹੀਂ ਅਤੇ ਸੰਭਾਲੀ ਜਾਣਕਾਰੀ ਨਹੀਂ।",
        serverError: "ਸਰਵਰ ਨਾਲ ਸੰਪਰਕ ਨਹੀਂ ਹੋ ਸਕਿਆ।",
        offlineAnswer: "ਔਫਲਾਈਨ ਜਵਾਬ",
        savedAnswer: "ਸੰਭਾਲਿਆ ਹੋਇਆ ਜਵਾਬ",
        schemesHeading: "ਸਿਫ਼ਾਰਸ਼ ਕੀਤੀਆਂ ਯੋਜਨਾਵਾਂ",
        usefulLinks: "ਲਾਭਦਾਇਕ ਲਿੰਕ",
        nearbyCenters: "ਨੇੜਲੇ ਕੇਂਦਰ",
        openMaps: "ਨਕਸ਼ੇ ਵਿੱਚ ਦੇਖੋ",
        officialLink: "ਅਧਿਕਾਰਤ ਲਿੰਕ",
        central: "ਕੇਂਦਰ",
        typeMessage: "ਸੁਨੇਹਾ ਟਾਈਪ ਕਰੋ...",
        micUnsupported: "ਇਸ ਬ੍ਰਾਊਜ਼ਰ ਵਿੱਚ ਅਵਾਜ਼ ਇਨਪੁੱਟ ਸਮਰਥਿਤ ਨਹੀਂ ਹੈ।",
        hearError: "ਮਾਫ਼ ਕਰਨਾ, ਮੈਂ ਸੁਣ ਨਹੀਂ ਸਕਿਆ।",
    },
};

function getLang() {
    return document.documentElement.lang || 'hi';
}

function t(key) {
    const lang = getLang();
    return I18N[lang] ? (I18N[lang][key] || key) : (I18N['hi'][key] || key);
}

function setLanguage(lang) {
    document.documentElement.lang = lang;
    try { localStorage.setItem('saarthi_lang', lang); } catch(e) { console.warn('Could not persist language preference:', e); }
    const select = document.getElementById('language-select');
    if (select && select.value !== lang) {
        select.value = lang;
    }

    updatePlaceholder();
    updateConnectivityPill();
    updateMicHint();
}

window.setLanguage = setLanguage;
window.toggleLanguage = setLanguage;

function isOnline() {
    return navigator.onLine;
}

function updateConnectivityPill() {
    const dot = document.getElementById("connectivity-dot");
    const text = document.getElementById("connectivity-text");
    if (!dot || !text) return;

    if (isOnline()) {
        dot.classList.remove("bg-red-500");
        dot.classList.add("bg-green-500");
        text.textContent = t("online");
    } else {
        dot.classList.remove("bg-green-500");
        dot.classList.add("bg-red-500");
        text.textContent = t("offline");
    }
}

window.addEventListener("online", updateConnectivityPill);
window.addEventListener("offline", updateConnectivityPill);

/* --- PROFILE MANAGEMENT --- */
function loadFarmerProfile() {
    const saved = localStorage.getItem("saarthi_profile");
    return saved ? JSON.parse(saved) : {
        name: "", phone: "", state: "", district: "", landSize: "", crop: "", income: ""
    };
}

function saveFarmerProfile(profile) {
    localStorage.setItem("saarthi_profile", JSON.stringify(profile));
}

function getFarmerProfileSnapshot() {
    const p = loadFarmerProfile();
    return `${p.state || ""}|${p.district || ""}|${p.landSize || ""}|${p.crop || ""}|${p.income || ""}`;
}

function openProfileDrawer() {
    const drawer = document.getElementById("profile-drawer");
    const overlay = document.getElementById("profile-overlay");
    const profile = loadFarmerProfile();

    const nameInput = document.getElementById("prof-name");
    if (nameInput) nameInput.value = profile.name || "";
    const phoneInput = document.getElementById("prof-phone");
    if (phoneInput) phoneInput.value = profile.phone || "";
    const stateInput = document.getElementById("prof-state") || document.getElementById("profile-state");
    if (stateInput) stateInput.value = profile.state || "";
    const districtInput = document.getElementById("prof-district");
    if (districtInput) districtInput.value = profile.district || "";
    const landInput = document.getElementById("prof-land") || document.getElementById("profile-land");
    if (landInput) landInput.value = profile.landSize || "";
    const cropInput = document.getElementById("prof-crop") || document.getElementById("profile-crop");
    if (cropInput) cropInput.value = profile.crop || "";
    const incomeInput = document.getElementById("prof-income") || document.getElementById("profile-income");
    if (incomeInput) incomeInput.value = profile.income || "";

    if (drawer) {
        drawer.classList.remove("hidden");
        drawer.classList.remove("translate-x-full");
    }
    if (overlay) {
        overlay.classList.remove("hidden");
        overlay.classList.add("block");
    }
}

function closeProfileDrawer() {
    const drawer = document.getElementById("profile-drawer");
    const overlay = document.getElementById("profile-overlay");
    if (drawer) {
        drawer.classList.add("translate-x-full");
        drawer.addEventListener("transitionend", () => drawer.classList.add("hidden"), { once: true });
    }
    if (overlay) {
        overlay.classList.remove("block");
        overlay.classList.add("hidden");
    }
}

function saveProfileFromDrawer() {
    const get = (id1, id2) => {
        const el = document.getElementById(id1) || (id2 ? document.getElementById(id2) : null);
        return el ? el.value : "";
    };
    const profile = {
        name: get("prof-name"),
        phone: get("prof-phone"),
        state: get("prof-state", "profile-state"),
        district: get("prof-district"),
        landSize: get("prof-land", "profile-land"),
        crop: get("prof-crop", "profile-crop"),
        income: get("prof-income", "profile-income"),
    };
    saveFarmerProfile(profile);
    closeProfileDrawer();
}

/* --- CACHING ENGINE --- */
const CACHE_NAME = 'saarthi_qa_v1';
const MAX_CACHE_ENTRIES = 50;

function buildCacheKey(query, lang, profileSnapshot) {
    const norm = query.toLowerCase().trim().replace(/[?.!]/g, "");
    return `q:${norm}|l:${lang}|p:${profileSnapshot}`;
}

function cacheResponse(key, data, originalQuery, lang) {
    try {
        const cache = JSON.parse(localStorage.getItem(CACHE_NAME) || "{}");
        cache[key] = {
            data: data,
            timestamp: Date.now(),
            query: originalQuery,
            lang: lang
        };
        const entries = Object.entries(cache);
        if (entries.length > MAX_CACHE_ENTRIES) {
            entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
            delete cache[entries[0][0]];
        }
        localStorage.setItem(CACHE_NAME, JSON.stringify(cache));
    } catch(e) { console.error("Cache Write Error", e); }
}

function getCachedResponse(key) {
    try {
        const cache = JSON.parse(localStorage.getItem(CACHE_NAME) || "{}");
        if (cache[key]) {
            cache[key].timestamp = Date.now();
            localStorage.setItem(CACHE_NAME, JSON.stringify(cache));
            return cache[key].data;
        }
    } catch(e) { console.error("Cache Read Error", e); }
    return null;
}

function findBestCachedAnswer(query, lang) {
    try {
        const cache = JSON.parse(localStorage.getItem(CACHE_NAME) || "{}");
        const normQuery = query.toLowerCase().trim();
        const keywords = normQuery.split(/\s+/).filter(k => k.length > 3);
        
        let best = null;
        let maxScore = 0;

        for (const key in cache) {
            const entry = cache[key];
            if (entry.lang !== lang) continue;
            let score = 0;
            keywords.forEach(kw => { if (entry.query.toLowerCase().includes(kw)) score++; });
            if (score > maxScore) { maxScore = score; best = entry.data; }
        }
        return maxScore > 0 ? best : null;
    } catch(e) { return null; }
}

function pruneOldCacheEntries() {
    try {
        const cache = JSON.parse(localStorage.getItem(CACHE_NAME) || "{}");
        const now = Date.now();
        const WEEK = 7 * 24 * 60 * 60 * 1000;
        let changed = false;
        for (const key in cache) {
            if (now - cache[key].timestamp > WEEK) { delete cache[key]; changed = true; }
        }
        if (changed) localStorage.setItem(CACHE_NAME, JSON.stringify(cache));
    } catch(e) {}
}

/* --- OFFLINE SCHEMES --- */
let OFFLINE_SCHEMES_CACHE = [];
async function fetchAndCacheSchemes() {
    if (!isOnline()) return;
    try {
        const res = await fetch(`${API_URL}/query`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: "list all schemes", language: getLang() })
        });
        if (res.ok) {
            const data = await res.json();
            if (data.recommended_schemes) {
                OFFLINE_SCHEMES_CACHE = data.recommended_schemes;
                localStorage.setItem("saarthi_schemes_offline", JSON.stringify(OFFLINE_SCHEMES_CACHE));
            }
        }
    } catch(e) {}
}

function searchOfflineSchemes(query) {
    const raw = localStorage.getItem("saarthi_schemes_offline");
    const schemes = raw ? JSON.parse(raw) : OFFLINE_SCHEMES_CACHE;
    if (!schemes || schemes.length === 0) return [];

    const terms = query.toLowerCase().split(/\s+/).filter(t => t.length > 2);
    return schemes.filter(s => {
        const text = (s.name + " " + s.description).toLowerCase();
        return terms.some(t => text.includes(t));
    }).slice(0, 3);
}

function generateOfflineResponse(query, schemes) {
    return {
        answer: schemes.length > 0 
            ? `It seems you are asking about agricultural schemes. I found matching information for: ${schemes.map(s => s.name).join(", ")}.`
            : "I am currently offline and don't have this information saved. I can help with general farming queries or your profile details.",
        recommended_schemes: schemes,
        doc_links: [],
        nearest_centers: [],
    };
}

/* --- SUGGESTION GRID --- */
function useChip(query) {
    const input = document.getElementById("text-input");
    if (input) {
        input.value = query;
        sendTextMessage();
    }
}

/* --- CHAT ENGINE --- */
let conversationToken = 0;

async function sendTextMessage(textStr) {
    const inputField = document.getElementById("text-input");
    let query = typeof textStr === 'string' ? textStr.trim() : inputField.value.trim();
    if (!query) return;
    if (typeof textStr !== 'string') inputField.value = "";


    if (window.stopSpeaking) window.stopSpeaking();

    // Hide quick actions on first message
    const quickActions = document.getElementById("quick-actions-section");
    if (quickActions) quickActions.classList.add("hidden");

    addMessageToChat(query, "user");
    conversationHistory.push({ role: "user", content: query });
    if (conversationHistory.length > MAX_CONVERSATION_HISTORY) {
        conversationHistory = conversationHistory.slice(-MAX_CONVERSATION_HISTORY);
    }
    await processQuery(query);
}

async function processQuery(query) {
    const resolvedLang = getLang();
    const profileSnapshot = getFarmerProfileSnapshot();
    const cacheKey = buildCacheKey(query, resolvedLang, profileSnapshot);
    const myToken = ++conversationToken;

    showStatus(t("thinking"));

    if (!isOnline()) {
        const exact = getCachedResponse(cacheKey);
        const best  = exact || findBestCachedAnswer(query, resolvedLang);
        if (myToken !== conversationToken) return;
        if (best) {
            trackAssistantResponse(best.answer);
            displayResponse(best, true);
        } else {
            const matched = searchOfflineSchemes(query);
            const offlineData = generateOfflineResponse(query, matched);
            trackAssistantResponse(offlineData.answer);
            displayResponse(offlineData, true, true);
        }
        showStatus("");
        return;
    }

    const profile = loadFarmerProfile();
    try {
        const historyToSend = conversationHistory.length > 1 ? conversationHistory.slice(0, -1) : [];
        const response = await fetch(`${API_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query, language: resolvedLang, occupation: "farmer",
                state: profile.state || undefined, income: profile.income ? parseInt(profile.income) || undefined : undefined,
                crop: profile.crop || undefined, land_size: profile.landSize || undefined,
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
        const exact = getCachedResponse(cacheKey);
        const fallback = exact || findBestCachedAnswer(query, resolvedLang);
        if (fallback) {
            trackAssistantResponse(fallback.answer);
            displayResponse(fallback, true);
        } else {
            addMessageToChat(t("serverError"), "bot");
        }
    } finally {
        showStatus("");
    }
}

function trackAssistantResponse(answer) {
    if (answer) {
        conversationHistory.push({ role: "assistant", content: answer });
        if (conversationHistory.length > MAX_CONVERSATION_HISTORY) {
            conversationHistory = conversationHistory.slice(-MAX_CONVERSATION_HISTORY);
        }
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
        return (parsed.protocol === 'http:' || parsed.protocol === 'https:') ? parsed.href : '';
    } catch(e) { return ''; }
}

function renderMarkdown(str) {
    if (!str) return '';
    let html = escapeHtml(str);
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/(https?:\/\/[^\s<]+)/g, function(url) {
        const safe = sanitizeUrl(url);
        return safe ? `<a href="${escapeHtml(safe)}" target="_blank" rel="noopener" class="text-primary underline font-medium">${escapeHtml(safe)}</a>` : url;
    });
    html = html.replace(/^(#{1,3})\s+(.+)$/gm, (m, hashes, text) => `<div class="font-bold text-slate-800 mt-2 mb-1">${text}</div>`);
    html = html.replace(/^─+$/gm, '<hr class="border-slate-200 my-2">');
    return html;
}

function displayResponse(data, isCached, isOfflineGenerated) {
    const badgeText = isOfflineGenerated ? t("offlineAnswer") : (isCached ? t("savedAnswer") : "");
    const badge = badgeText ? `<span class="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5 mt-2"><span class="material-symbols-outlined text-[13px]">${isOfflineGenerated ? 'wifi_off' : 'bookmark'}</span>${badgeText}</span>` : "";

    let htmlContent = `
        <div class="flex items-start gap-3 w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div class="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-primary text-[20px]">agriculture</span>
            </div>
            <div class="flex flex-col gap-1 max-w-[85%]">
                <div class="text-[16px] leading-relaxed text-slate-700 whitespace-pre-line">${renderMarkdown(data.answer)}</div>
                ${badge}
            </div>
        </div>
    `;

    if (window.speakText && data.answer) {
        const textToSpeak = data.answer_romanized || data.answer;
        const speakLang = data.answer_romanized ? "en" : (data.response_language || getLang());
        window.speakText(textToSpeak, speakLang);
    }

    if (data.recommended_schemes && data.recommended_schemes.length > 0) {
        htmlContent += `<div class="flex flex-col gap-3 mt-4 ml-12"><span class="text-[13px] font-bold text-slate-500 uppercase tracking-wide flex items-center gap-2"><span class="material-symbols-outlined text-[18px]">auto_awesome</span>${t("schemesHeading")}</span>`;
        data.recommended_schemes.forEach(scheme => {
            htmlContent += `
                <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm hover:border-primary/40 transition-all">
                    <h4 class="font-bold text-primary text-[15px] mb-1">${escapeHtml(scheme.name)}</h4>
                    <p class="text-[14px] text-slate-600 leading-snug">${escapeHtml(scheme.description)}</p>
                    ${scheme.documents_links ? `<div class="mt-3 flex gap-2">${scheme.documents_links.map(u => { const safe = sanitizeUrl(u); return safe ? `<a href="${escapeHtml(safe)}" target="_blank" rel="noopener noreferrer" class="text-[12px] text-primary font-bold flex items-center gap-1">LINK <span class="material-symbols-outlined text-[14px]">open_in_new</span></a>` : ""; }).join("")}</div>` : ""}
                </div>`;
        });
        htmlContent += '</div>';
    }

    if (data.nearest_centers && data.nearest_centers.length > 0) {
        htmlContent += `<div class="flex flex-col gap-2 mt-4 ml-12"><span class="text-[13px] font-bold text-slate-500 uppercase tracking-wide flex items-center gap-2"><span class="material-symbols-outlined text-[18px]">location_on</span>${t("nearbyCenters")}</span>`;
        data.nearest_centers.forEach(c => {
            htmlContent += `
                <div class="bg-white border border-slate-200 rounded-2xl p-3 shadow-sm">
                    <div class="font-bold text-[14px] text-slate-700">${escapeHtml(c.name)}</div>
                    <div class="text-[12px] text-slate-500">${escapeHtml(c.address || "")}</div>
                    <div class="mt-2 flex gap-3">
                        ${c.phone ? `<a href="tel:${escapeHtml(String(c.phone).replace(/[^0-9+]/g, ''))}" class="text-primary text-[13px] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">call</span> CALL</a>` : ""}
                        ${c.maps_url ? `<a href="${sanitizeUrl(c.maps_url)}" target="_blank" rel="noopener noreferrer" class="text-primary text-[13px] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">map</span> MAPS</a>` : ""}
                    </div>
                </div>`;
        });
        htmlContent += '</div>';
    }

    addRawHtmlToChat(htmlContent, "bot");
}

function addMessageToChat(text, sender) {
    let htmlContent = "";
    if (sender === "user") {
        htmlContent = `
        <div class="flex justify-end w-full animate-in fade-in slide-in-from-right-4 duration-300">
            <div class="bg-[#eaddc9] text-[#4a3f35] rounded-[24px] rounded-br-[4px] px-5 py-3 max-w-[85%] shadow-sm">
                <p class="text-[16px] leading-snug">${escapeHtml(text)}</p>
            </div>
        </div>`;
    } else {
        htmlContent = `
        <div class="flex items-start gap-3 w-full animate-in fade-in slide-in-from-left-4 duration-300">
            <div class="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-primary text-[20px]">agriculture</span>
            </div>
            <div class="flex flex-col gap-1 max-w-[85%]">
                <div class="text-[16px] leading-relaxed text-slate-700">${escapeHtml(text)}</div>
            </div>
        </div>`;
    }
    addRawHtmlToChat(htmlContent, sender);
}

function addRawHtmlToChat(htmlContent, sender) {
    const chatBox = document.getElementById("chat-box");
    const wrapper = document.createElement("div");
    wrapper.className = "mb-6";
    wrapper.innerHTML = htmlContent;
    chatBox.appendChild(wrapper);
    
    // Scroll within the chat container
    const chatContainer = document.getElementById("chat-container");
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } else {
        wrapper.scrollIntoView({ behavior: "smooth", block: "end" });
    }
}

function showStatus(text) {
    const el = document.getElementById("status-indicator");
    if (el) el.innerText = text;
}

function updatePlaceholder() {
    const input = document.getElementById("text-input");
    if (input) input.placeholder = t("typeMessage");
}

function updateMicHint() {
    const micBtn = document.getElementById("mic-btn");
    const msg = t("micUnsupported");
    if (micBtn && micBtn.disabled) {
        micBtn.title = msg;
        micBtn.setAttribute("aria-label", msg);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    pruneOldCacheEntries();
    updateConnectivityPill();
    updatePlaceholder();
    updateMicHint();
    fetchAndCacheSchemes();

    // Event Listeners
    document.getElementById("avatar-btn").addEventListener("click", openProfileDrawer);
    document.getElementById("profile-save-btn").addEventListener("click", saveProfileFromDrawer);
    document.getElementById("profile-cancel-btn").addEventListener("click", closeProfileDrawer);
    document.getElementById("profile-overlay").addEventListener("click", closeProfileDrawer);

    document.getElementById("send-btn").addEventListener("click", sendTextMessage);
    document.getElementById("text-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendTextMessage();
    });



    // Initialize language from stored preference or document lang
    const savedLang = (function() {
        try { return localStorage.getItem('saarthi_lang'); } catch(e) { return null; }
    })() || document.documentElement.lang || 'hi';
    setLanguage(savedLang);
});

window.useChip = useChip;
window.showStatus = showStatus;
window.t = t;
window.sendTextMessage = sendTextMessage;
