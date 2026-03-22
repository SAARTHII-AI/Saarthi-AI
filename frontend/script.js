const API_URL = (location.hostname === "localhost" || location.hostname === "127.0.0.1" || location.protocol === "file:")
    ? "http://localhost:8000"
    : "https://backend-saarthi.vercel.app";

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function sanitizeExternalUrl(url) {
    try {
        const parsed = new URL(String(url || ""), window.location.origin);
        if (parsed.protocol === "http:" || parsed.protocol === "https:") {
            return parsed.href;
        }
    } catch (error) {
        console.warn("Invalid external URL blocked:", url);
    }
    return null;
}

// Handle Enter key for text input
function handleEnterKeyPress(event) {
    if (event.key === "Enter") {
        sendTextMessage();
    }
}

// Send user query via text input
async function sendTextMessage() {
    const inputField = document.getElementById("text-input");
    const query = inputField.value.trim();
    
    if (!query) return;
    
    inputField.value = "";
    addMessageToChat(query, "user");
    
    await processQuery(query);
}

// Process query via backend API
async function processQuery(query) {
    showStatus("सोच रहा है... (Thinking...)");
    
    const language = document.getElementById("language-select").value;
    
    // Simulate caching mechanism
    const cacheKey = `query_${query}_${language}`;
    const cachedResponse = localStorage.getItem(cacheKey);
    
    if (cachedResponse) {
        console.log("Using cached response");
        const responseData = JSON.parse(cachedResponse);
        displayResponse(responseData);
        showStatus("");
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: query,
                language: language,
                // Passing dummy user data for MVP recommendations
                occupation: "farmer",
                income: 200000 
            })
        });
        
        if (!response.ok) throw new Error("API Network output error");
        
        const data = await response.json();
        
        // Cache successful response (keep last 20)
        cacheResponse(cacheKey, data);
        
        displayResponse(data);
    } catch (error) {
        console.error("Error fetching data:", error);
        addMessageToChat("माफ़ करें, अभी सर्वर से संपर्क नहीं हो पा रहा है। (Sorry, unable to contact the server.)", "bot");
    } finally {
        showStatus("");
    }
}

// Format and display response from backend
function displayResponse(data) {
    const safeAnswer = escapeHtml(data.answer);
    let htmlContent = `
        <div class="flex items-end gap-3 max-w-[90%] bot-message mb-4">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center text-white shadow-sm shrink-0">
                <span class="material-symbols-outlined text-[18px]">smart_toy</span>
            </div>
            <div class="flex flex-col gap-1">
                <span class="text-xs font-medium text-slate-500 dark:text-slate-400 ml-1">SaarthiAI</span>
                <div class="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl rounded-bl-sm p-4 shadow-sm">
                    <p class="text-[15px] leading-relaxed text-slate-800 dark:text-slate-200 message-content">${safeAnswer}</p>
                </div>
            </div>
        </div>
    `;
    
    // Speak the answer aloud using the backend-provided language code if available
    if (window.speakText) {
        window.speakText(data.answer, data.response_language);
    }
    
    if (data.recommended_schemes && data.recommended_schemes.length > 0) {
        htmlContent += '<div class="flex flex-col gap-2 mb-4 ml-11"><strong class="text-sm text-slate-600 dark:text-slate-300">अनुशंसित योजनाएं (Recommended Schemes):</strong>';
        data.recommended_schemes.forEach(scheme => {
            const safeSchemeName = escapeHtml(scheme.name);
            const safeSchemeDescription = escapeHtml(scheme.description);
            htmlContent += `
                <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 shadow-sm">
                    <h4 class="font-semibold text-primary text-[15px] mb-1">${safeSchemeName}</h4>
                    <p class="text-sm text-slate-600 dark:text-slate-300 leading-snug">${safeSchemeDescription}</p>
                </div>
            `;
        });
        htmlContent += '</div>';
    }

    if (data.document_links && data.document_links.length > 0) {
        htmlContent += '<div class="flex flex-col gap-2 mb-4 ml-11"><strong class="text-sm text-slate-600 dark:text-slate-300">ज़रूरी दस्तावेज़/ऑफिशियल लिंक (Document Links):</strong>';
        data.document_links.forEach(link => {
            const safeTitle = escapeHtml(link.title);
            const safeDescription = escapeHtml(link.description || "");
            const safeSource = escapeHtml(link.source || "official");
            const safeUrl = sanitizeExternalUrl(link.url);

            if (safeUrl) {
                htmlContent += `
                    <a href="${safeUrl}" target="_blank" rel="noopener noreferrer" class="block bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 shadow-sm hover:border-primary/40 transition-colors">
                        <h4 class="font-semibold text-primary text-[15px] mb-1">${safeTitle}</h4>
                        <p class="text-sm text-slate-600 dark:text-slate-300 leading-snug">${safeDescription}</p>
                        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Source: ${safeSource}</p>
                    </a>
                `;
            } else {
                htmlContent += `
                    <div class="block bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 shadow-sm">
                        <h4 class="font-semibold text-primary text-[15px] mb-1">${safeTitle}</h4>
                        <p class="text-sm text-slate-600 dark:text-slate-300 leading-snug">${safeDescription}</p>
                        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Source: ${safeSource}</p>
                    </div>
                `;
            }
        });
        htmlContent += '</div>';
    }
    
    addRawHtmlToChat(htmlContent, "bot");
}

// Add simple text message to chat
function addMessageToChat(text, sender) {
    const safeText = escapeHtml(text);
    let htmlContent = "";
    if (sender === "user") {
        htmlContent = `
        <div class="flex items-end justify-end gap-3 w-full mb-4">
            <div class="flex flex-col gap-1 items-end max-w-[85%]">
                <span class="text-xs font-medium text-slate-500 dark:text-slate-400 mr-1">You</span>
                <div class="bg-primary text-white rounded-2xl rounded-br-sm p-3 shadow-sm">
                    <p class="text-[15px] leading-relaxed">${safeText}</p>
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
                    <p class="text-[15px] leading-relaxed text-slate-800 dark:text-slate-200">${safeText}</p>
                </div>
            </div>
        </div>`;
    }
    
    addRawHtmlToChat(htmlContent, sender);
}

// Add raw HTML to chat
function addRawHtmlToChat(htmlContent, sender) {
    const chatBox = document.getElementById("chat-box");
    // Just append the raw HTML structure directly since we are building it with Tailwind fully inside the string
    chatBox.insertAdjacentHTML('beforeend', htmlContent);
    
    // Scroll to bottom
    const chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show temporary status
function showStatus(text) {
    document.getElementById("status-indicator").innerText = text;
}

// Offline Caching logic (stores last 20 queries)
function cacheResponse(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
    
    // Manage cache size
    let keys = JSON.parse(localStorage.getItem("saarthi_cache_keys") || "[]");
    if (!keys.includes(key)) {
        keys.push(key);
        if (keys.length > 20) {
            const oldestKey = keys.shift();
            localStorage.removeItem(oldestKey);
        }
        localStorage.setItem("saarthi_cache_keys", JSON.stringify(keys));
    }
}
