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
    }
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
    const select = document.getElementById('language-select');
    if (select && select.value !== lang) {
        select.value = lang;
    }

    updatePlaceholder();
    updateConnectivityPill();
    updateMicHint();
}

window.toggleLanguage = function(lang) {
    setLanguage(lang);
};

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
    return `${p.state}|${p.district}|${p.landSize}|${p.crop}|${p.income}`;
}

function openProfileDrawer() {
    const drawer = document.getElementById("profile-drawer");
    const overlay = document.getElementById("profile-overlay");
    const profile = loadFarmerProfile();

    document.getElementById("prof-name").value = profile.name || "";
    document.getElementById("prof-phone").value = profile.phone || "";
    document.getElementById("prof-state").value = profile.state || "";
    document.getElementById("prof-district").value = profile.district || "";
    document.getElementById("prof-land").value = profile.landSize || "";
    document.getElementById("prof-crop").value = profile.crop || "";
    document.getElementById("prof-income").value = profile.income || "";

    drawer.classList.remove("translate-x-full");
    overlay.classList.remove("hidden");
    overlay.classList.add("block");
}

function closeProfileDrawer() {
    const drawer = document.getElementById("profile-drawer");
    const overlay = document.getElementById("profile-overlay");
    drawer.classList.add("translate-x-full");
    overlay.classList.remove("block");
    overlay.classList.add("hidden");
}

function saveProfileFromDrawer() {
    const profile = {
        name: document.getElementById("prof-name").value,
        phone: document.getElementById("prof-phone").value,
        state: document.getElementById("prof-state").value,
        district: document.getElementById("prof-district").value,
        landSize: document.getElementById("prof-land").value,
        crop: document.getElementById("prof-crop").value,
        income: document.getElementById("prof-income").value,
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
    const quickActions = document.getElementById("quick-actions");
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
                    ${scheme.documents_links ? `<div class="mt-3 flex gap-2">${scheme.documents_links.map(u => `<a href="${sanitizeUrl(u)}" target="_blank" class="text-[12px] text-primary font-bold flex items-center gap-1">LINK <span class="material-symbols-outlined text-[14px]">open_in_new</span></a>`).join("")}</div>` : ""}
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
                        ${c.phone ? `<a href="tel:${c.phone}" class="text-primary text-[13px] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">call</span> CALL</a>` : ""}
                        ${c.maps_url ? `<a href="${sanitizeUrl(c.maps_url)}" target="_blank" class="text-primary text-[13px] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">map</span> MAPS</a>` : ""}
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
    
    // Smooth scroll
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
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



    // Initialize branding state
    setLanguage('hi'); 
});

window.useChip = useChip;
window.showStatus = showStatus;
window.t = t;
window.sendTextMessage = sendTextMessage;
