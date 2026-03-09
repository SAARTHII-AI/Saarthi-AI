const API_URL = "http://localhost:8000";

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
    let htmlContent = `<div class="message-content">${data.answer}</div>`;
    
    // Speak the answer aloud
    if (window.speakText) {
        window.speakText(data.answer);
    }
    
    if (data.recommended_schemes && data.recommended_schemes.length > 0) {
        htmlContent += '<div class="recommendations"><strong>कुछ अनुशंसित योजनाएं (Recommended Schemes):</strong>';
        data.recommended_schemes.forEach(scheme => {
            htmlContent += `
                <div class="recommendation-card">
                    <h4>${scheme.name}</h4>
                    <p>${scheme.description}</p>
                </div>
            `;
        });
        htmlContent += '</div>';
    }
    
    addRawHtmlToChat(htmlContent, "bot");
}

// Add simple text message to chat
function addMessageToChat(text, sender) {
    const htmlContent = `<div class="message-content">${text}</div>`;
    addRawHtmlToChat(htmlContent, sender);
}

// Add raw HTML to chat (for formatted bot responses)
function addRawHtmlToChat(htmlContent, sender) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = htmlContent;
    chatBox.appendChild(messageDiv);
    
    // Scroll to bottom
    const chatContainer = document.querySelector('.chat-container');
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
