const API_URL = "";

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
        stopSpeaking:   "बोलना बंद करें",
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
        stopSpeaking:   "Stop Speaking",
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
    return (I18N[getLang()] || I18N.en)[key] || key;
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

window.addEventListener("online",  updateConnectivityPill);
window.addEventListener("offline", updateConnectivityPill);

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

async function sendTextMessage() {
    const inputField = document.getElementById("text-input");
    const query = inputField.value.trim();
    if (!query) return;
    inputField.value = "";

    if (window.stopSpeaking) window.stopSpeaking();

    addMessageToChat(query, "user");
    await processQuery(query);
}

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

    const profile = loadFarmerProfile();
    try {
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
            })
        });

        if (!response.ok) throw new Error("server_error");

        const data = await response.json();
        cacheResponse(cacheKey, data, query, resolvedLang);
        displayResponse(data, false);
    } catch (error) {
        const isNetworkErr = !navigator.onLine || error instanceof TypeError || error.message === "Failed to fetch" || error.name === "AbortError";

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

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function displayResponse(data, isCached) {
    const savedBadge = isCached
        ? `<span class="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5 mt-2">
               <span class="material-symbols-outlined text-[13px]">bookmark</span>${t("savedAnswer")}
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
                    <p class="text-[14px] leading-relaxed text-slate-700 message-content whitespace-pre-line">${escapeHtml(data.answer)}</p>
                    ${savedBadge}
                </div>
            </div>
        </div>
    `;

    if (window.speakText) {
        window.speakText(data.answer, data.response_language);
    }

    if (data.recommended_schemes && data.recommended_schemes.length > 0) {
        htmlContent += `<div class="flex flex-col gap-2 mb-3 ml-9"><span class="text-[12px] font-semibold text-slate-500 flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">auto_awesome</span>${t("schemesHeading")}</span>`;
        data.recommended_schemes.forEach(scheme => {
            const typeBadge = scheme.type
                ? `<span class="inline-flex items-center text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${scheme.type === 'central' ? 'bg-blue-50 text-blue-600' : 'bg-purple-50 text-purple-600'}">${scheme.type === 'central' ? 'Central' : scheme.state || 'State'}</span>`
                : '';
            const docLinks = (scheme.documents_links && scheme.documents_links.length > 0)
                ? `<div class="flex flex-wrap gap-1 mt-1.5">${scheme.documents_links.map(url => `<a href="${url}" target="_blank" rel="noopener" class="inline-flex items-center gap-0.5 text-[10px] text-primary hover:underline font-medium"><span class="material-symbols-outlined text-[11px]">open_in_new</span>Official Link</a>`).join('')}</div>`
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
        htmlContent += `<div class="flex flex-col gap-1.5 mb-3 ml-9"><span class="text-[12px] font-semibold text-slate-500 flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">link</span>Useful Links</span>`;
        data.doc_links.forEach(link => {
            htmlContent += `
                <a href="${link.url}" target="_blank" rel="noopener" class="flex items-center gap-2 bg-white border border-slate-200 rounded-xl p-2.5 hover:border-primary/40 transition-colors no-underline">
                    <span class="material-symbols-outlined text-primary text-[16px] shrink-0">open_in_new</span>
                    <span class="text-[12px] text-slate-600 font-medium leading-snug">${escapeHtml(link.title)}</span>
                </a>
            `;
        });
        htmlContent += '</div>';
    }

    if (data.nearest_centers && data.nearest_centers.length > 0) {
        htmlContent += `<div class="flex flex-col gap-1.5 mb-3 ml-9"><span class="text-[12px] font-semibold text-slate-500 flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">location_on</span>Nearby Centers</span>`;
        data.nearest_centers.forEach(center => {
            const phone = center.phone ? `<a href="tel:${center.phone}" class="inline-flex items-center gap-0.5 text-primary text-[11px] font-medium"><span class="material-symbols-outlined text-[13px]">call</span>${escapeHtml(center.phone)}</a>` : '';
            const mapsLink = center.maps_url ? `<a href="${center.maps_url}" target="_blank" rel="noopener" class="inline-flex items-center gap-0.5 text-primary text-[11px] font-medium hover:underline"><span class="material-symbols-outlined text-[13px]">map</span>Open in Maps</a>` : '';
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
    updateStateFilterButton();
    renderSuggestionChips();

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
    });

    if (isOnline()) {
        preCachePopularQueries();
    }
});

function preCachePopularQueries() {
    const PRECACHE_KEY = 'saarthi_precached';
    if (localStorage.getItem(PRECACHE_KEY)) return;

    const popularQueries = [
        "PM-KISAN scheme eligibility and benefits",
        "Kisan Credit Card scheme details",
        "PMFBY crop insurance scheme benefits",
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
