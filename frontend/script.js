const API_URL = "";

// ─── i18n Strings ──────────────────────────────────────────────────────────
const I18N = {
    hi: {
        thinking:       "सोच रहा है...",
        listening:      "सुन रहा हूँ...",
        understood:     "समझ लिया!",
        offline:        "आप ऑफलाइन हैं। सहेजा गया उत्तर दिखा रहा है।",
        noCache:        "आप ऑफलाइन हैं और कोई सहेजा गया उत्तर नहीं है।",
        serverError:    "सर्वर से संपर्क नहीं हो पा रहा है।",
        savedAnswer:    "सहेजा गया उत्तर",
        onlinePill:     "ऑनलाइन",
        offlinePill:    "ऑफलाइन",
        micUnsupported: "इस ब्राउज़र में वॉइस इनपुट समर्थित नहीं है। कृपया टाइप करें।",
        hearError:      "माफ़ करें, मैं सुन नहीं पाया।",
        schemesHeading: "अनुशंसित योजनाएं:",
    },
    ta: {
        thinking:       "யோசிக்கிறேன்...",
        listening:      "கேட்கிறேன்...",
        understood:     "புரிந்தது!",
        offline:        "நீங்கள் ஆஃப்லைனில் உள்ளீர்கள். சேமித்த பதில் காட்டுகிறது.",
        noCache:        "நீங்கள் ஆஃப்லைனில் உள்ளீர்கள், சேமித்த பதில் இல்லை.",
        serverError:    "சேவையகத்தை தொடர்பு கொள்ள முடியவில்லை.",
        savedAnswer:    "சேமித்த பதில்",
        onlinePill:     "ஆன்லைன்",
        offlinePill:    "ஆஃப்லைன்",
        micUnsupported: "இந்த உலாவியில் குரல் உள்ளீடு ஆதரிக்கப்படவில்லை. தயவுசெய்து தட்டச்சு செய்யுங்கள்.",
        hearError:      "மன்னிக்கவும், என்னால் கேட்க முடியவில்லை.",
        schemesHeading: "பரிந்துரைக்கப்பட்ட திட்டங்கள்:",
    },
    en: {
        thinking:       "Thinking...",
        listening:      "Listening...",
        understood:     "Understood!",
        offline:        "You are offline. Showing saved answer.",
        noCache:        "You are offline and no saved answer found.",
        serverError:    "Unable to contact the server.",
        savedAnswer:    "Saved answer",
        onlinePill:     "Online",
        offlinePill:    "Offline",
        micUnsupported: "Voice input not supported on this browser. Please type.",
        hearError:      "Sorry, I couldn't hear you.",
        schemesHeading: "Recommended Schemes:",
    },
};

function getLang() {
    const v = document.getElementById("language-select").value;
    if (v === "hi") return "hi";
    if (v === "ta") return "ta";
    if (v === "en") return "en";
    // "auto" — detect from browser navigator
    const nav = (navigator.language || navigator.userLanguage || "en").toLowerCase();
    if (nav.startsWith("hi")) return "hi";
    if (nav.startsWith("ta")) return "ta";
    return "en";
}

function t(key) {
    return (I18N[getLang()] || I18N.en)[key] || key;
}

// Make t() and getLang() accessible to voice.js
window.t = t;
window.getLang = getLang;

// ─── Online/Offline indicator ───────────────────────────────────────────────
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

window.addEventListener("online",  updateConnectivityPill);
window.addEventListener("offline", updateConnectivityPill);

// ─── Farmer Profile ─────────────────────────────────────────────────────────
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

// ─── Smart Cache (LRU, 50 entries, 7-day TTL) ────────────────────────────────
const CACHE_META_KEY  = "saarthi_cache_meta";
const CACHE_MAX       = 50;
const CACHE_TTL_MS    = 7 * 24 * 60 * 60 * 1000;

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

function querySimilar(lq, eq) {
    return eq.includes(lq) || lq.includes(eq);
}

function findBestCachedAnswer(query, language) {
    const meta = loadCacheMeta();
    const lq = query.toLowerCase().trim();
    // Pass 1: same-language match (both inclusion directions)
    for (let i = meta.length - 1; i >= 0; i--) {
        const raw = localStorage.getItem(meta[i].key);
        if (!raw) continue;
        try {
            const entry = JSON.parse(raw);
            const eq = (entry.query || "").toLowerCase().trim();
            if (entry.language === language && eq && querySimilar(lq, eq)) {
                touchCacheMeta(meta[i].key);
                return entry.data;
            }
        } catch (e) {}
    }
    // Pass 2: any-language match (both inclusion directions)
    for (let i = meta.length - 1; i >= 0; i--) {
        const raw = localStorage.getItem(meta[i].key);
        if (!raw) continue;
        try {
            const entry = JSON.parse(raw);
            const eq = (entry.query || "").toLowerCase().trim();
            if (eq && querySimilar(lq, eq)) {
                touchCacheMeta(meta[i].key);
                return entry.data;
            }
        } catch (e) {}
    }
    return null;
}

// ─── Seasonal Suggestion Chips ───────────────────────────────────────────────
function getSeasonalChips() {
    const month = new Date().getMonth() + 1;
    // Kharif: June–October; Rabi: November–March; neutral: April–May
    const isKharif = month >= 6 && month <= 10;
    const isRabi   = month >= 11 || month <= 3;

    const baseChips = [
        { icon: "payments",          color: "text-green-600",  label: "PM-KISAN",              query: "PM-KISAN scheme eligibility and benefits" },
        { icon: "credit_card",       color: "text-blue-500",   label: "Kisan Credit Card",      query: "Kisan Credit Card scheme details" },
        { icon: "shield",            color: "text-yellow-600", label: "Crop Insurance (PMFBY)", query: "PMFBY crop insurance scheme benefits" },
        { icon: "storefront",        color: "text-orange-500", label: "Mandi Prices",           query: "Mandi prices today for my crop" },
        { icon: "eco",               color: "text-teal-500",   label: "Soil Health Card",       query: "Soil Health Card scheme how to get" },
        { icon: "grass",             color: "text-lime-600",   label: "Free Seed Scheme",       query: "Free seed distribution scheme for farmers" },
    ];

    const kharifChips = [
        { icon: "water_drop",         color: "text-blue-600",   label: "Paddy Farming Tips",  query: "Paddy cultivation tips for Kharif season" },
        { icon: "energy_savings_leaf", color: "text-green-500", label: "Soybean Schemes",     query: "Government schemes for soybean farmers" },
    ];

    const rabiChips = [
        { icon: "grain",             color: "text-amber-600",  label: "Wheat MSP",            query: "Wheat minimum support price MSP details" },
        { icon: "spa",               color: "text-yellow-500", label: "Mustard Schemes",      query: "Government schemes for mustard farmers" },
    ];

    const seasonal = isKharif ? kharifChips : isRabi ? rabiChips : [];
    const combined = [...baseChips];
    seasonal.forEach(chip => {
        combined.splice(Math.floor(Math.random() * (combined.length + 1)), 0, chip);
    });
    return combined.slice(0, 8);
}

function renderSuggestionChips() {
    const container = document.getElementById("suggestion-chips");
    if (!container) return;
    const chips = getSeasonalChips();
    container.innerHTML = chips.map(chip => `
        <button onclick="useChip(${JSON.stringify(chip.query).replace(/"/g, '&quot;')})"
            class="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full text-sm font-medium text-slate-700 dark:text-slate-300 shadow-sm active:bg-slate-50 dark:active:bg-slate-700 transition-colors flex items-center gap-1.5">
            <span class="material-symbols-outlined text-[16px] ${chip.color}">${chip.icon}</span>
            ${chip.label}
        </button>
    `).join("");
}

function useChip(query) {
    document.getElementById("text-input").value = query;
    sendTextMessage();
}

// ─── Handle Enter key ────────────────────────────────────────────────────────
function handleEnterKeyPress(event) {
    if (event.key === "Enter") {
        sendTextMessage();
    }
}

// ─── Send text message ───────────────────────────────────────────────────────
async function sendTextMessage() {
    const inputField = document.getElementById("text-input");
    const query = inputField.value.trim();
    if (!query) return;
    inputField.value = "";
    addMessageToChat(query, "user");
    await processQuery(query);
}

// ─── Offline-first processQuery ──────────────────────────────────────────────
async function processQuery(query) {
    const language = document.getElementById("language-select").value;
    const resolvedLang = getLang();
    const profileSnapshot = getFarmerProfileSnapshot();
    const cacheKey = buildCacheKey(query, resolvedLang, profileSnapshot);

    showStatus(t("thinking"));

    if (!isOnline()) {
        const exact = getCachedResponse(cacheKey);
        const best  = exact || findBestCachedAnswer(query, resolvedLang);
        if (best) {
            displayResponse(best, true);
            addOfflineBanner(t("offline"));
        } else {
            addMessageToChat(t("noCache"), "bot");
        }
        showStatus("");
        return;
    }

    // Online: always fetch from backend for fresh/personalised results
    const profile = loadFarmerProfile();
    try {
        const response = await fetch(`${API_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query,
                language: resolvedLang,
                occupation: "farmer",
                state:      profile.state    || "",
                crop:       profile.crop     || "",
                land_size:  profile.landSize || "",
                income:     profile.income   || "",
            })
        });

        if (!response.ok) throw new Error("server_error");

        const data = await response.json();
        cacheResponse(cacheKey, data, query, resolvedLang);
        displayResponse(data, false);
    } catch (error) {
        const isNetworkErr = !navigator.onLine || error instanceof TypeError || error.message === "Failed to fetch" || error.name === "AbortError";

        // Fetch failed — fall back to cache and always mark as cached
        const exact   = getCachedResponse(cacheKey);
        const fallback = exact || findBestCachedAnswer(query, resolvedLang);
        if (fallback) {
            displayResponse(fallback, true);
            addOfflineBanner(isNetworkErr ? t("offline") : t("serverError"));
        } else {
            addMessageToChat(isNetworkErr ? t("noCache") : t("serverError"), "bot");
        }
    } finally {
        showStatus("");
    }
}

// ─── Display response ────────────────────────────────────────────────────────
function displayResponse(data, isCached) {
    const savedBadge = isCached
        ? `<span class="inline-flex items-center gap-1 text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5 mt-2">
               <span class="material-symbols-outlined text-[14px]">bookmark</span>${t("savedAnswer")}
           </span>`
        : "";

    let htmlContent = `
        <div class="flex items-end gap-3 max-w-[90%] bot-message mb-4">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center text-white shadow-sm shrink-0">
                <span class="material-symbols-outlined text-[18px]">smart_toy</span>
            </div>
            <div class="flex flex-col gap-1">
                <span class="text-xs font-medium text-slate-500 dark:text-slate-400 ml-1">SaarthiAI</span>
                <div class="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl rounded-bl-sm p-4 shadow-sm">
                    <p class="text-[15px] leading-relaxed text-slate-800 dark:text-slate-200 message-content">${data.answer}</p>
                    ${savedBadge}
                </div>
            </div>
        </div>
    `;

    if (window.speakText) {
        window.speakText(data.answer, data.response_language);
    }

    if (data.recommended_schemes && data.recommended_schemes.length > 0) {
        htmlContent += `<div class="flex flex-col gap-2 mb-4 ml-11"><strong class="text-sm text-slate-600 dark:text-slate-300">${t("schemesHeading")}</strong>`;
        data.recommended_schemes.forEach(scheme => {
            htmlContent += `
                <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 shadow-sm">
                    <h4 class="font-semibold text-primary text-[15px] mb-1">${scheme.name}</h4>
                    <p class="text-sm text-slate-600 dark:text-slate-300 leading-snug">${scheme.description}</p>
                </div>
            `;
        });
        htmlContent += '</div>';
    }

    addRawHtmlToChat(htmlContent, "bot");
}

// ─── Add offline banner ───────────────────────────────────────────────────────
function addOfflineBanner(msg) {
    const html = `
        <div class="mx-auto mb-3 px-4 py-2 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-800 flex items-center gap-2">
            <span class="material-symbols-outlined text-[16px]">wifi_off</span>
            ${msg}
        </div>
    `;
    addRawHtmlToChat(html, "bot");
}

// ─── Add message to chat ─────────────────────────────────────────────────────
function addMessageToChat(text, sender) {
    let htmlContent = "";
    if (sender === "user") {
        htmlContent = `
        <div class="flex items-end justify-end gap-3 w-full mb-4">
            <div class="flex flex-col gap-1 items-end max-w-[85%]">
                <span class="text-xs font-medium text-slate-500 dark:text-slate-400 mr-1">You</span>
                <div class="bg-primary text-white rounded-2xl rounded-br-sm p-3 shadow-sm">
                    <p class="text-[15px] leading-relaxed">${text}</p>
                </div>
            </div>
        </div>`;
    } else {
        htmlContent = `
        <div class="flex items-end gap-3 max-w-[90%] bot-message mb-4">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center text-white shadow-sm shrink-0">
                <span class="material-symbols-outlined text-[18px]">smart_toy</span>
            </div>
            <div class="flex flex-col gap-1">
                <span class="text-xs font-medium text-slate-500 dark:text-slate-400 ml-1">SaarthiAI</span>
                <div class="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl rounded-bl-sm p-4 shadow-sm">
                    <p class="text-[15px] leading-relaxed text-slate-800 dark:text-slate-200">${text}</p>
                </div>
            </div>
        </div>`;
    }
    addRawHtmlToChat(htmlContent, sender);
}

// ─── Add raw HTML to chat ────────────────────────────────────────────────────
function addRawHtmlToChat(htmlContent, sender) {
    const chatBox = document.getElementById("chat-box");
    chatBox.insertAdjacentHTML("beforeend", htmlContent);
    const chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ─── Show status ─────────────────────────────────────────────────────────────
function showStatus(text) {
    document.getElementById("status-indicator").innerText = text;
}

// ─── Init ────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    pruneOldCacheEntries();
    updateConnectivityPill();
    renderSuggestionChips();

    document.getElementById("avatar-btn").addEventListener("click", openProfileDrawer);
    document.getElementById("profile-save-btn").addEventListener("click", saveProfileFromDrawer);
    document.getElementById("profile-cancel-btn").addEventListener("click", closeProfileDrawer);
    document.getElementById("profile-overlay").addEventListener("click", closeProfileDrawer);

    document.getElementById("language-select").addEventListener("change", () => {
        updateConnectivityPill();
        updateMicHint();
    });
});

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
