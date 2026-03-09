// Voice recognition and synthesis using Web Speech API

const micBtn = document.getElementById("mic-btn");
const languageSelect = document.getElementById("language-select");

// Check browser support
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = function() {
        isListening = true;
        micBtn.classList.add("listening");
        showStatus("सुन रहा हूँ... (Listening...)");
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("text-input").value = transcript;
        showStatus("समझ लिया! (Understood!)");
        
        // Auto-send query after voice recognition
        setTimeout(sendTextMessage, 500);
    };
    
    recognition.onerror = function(event) {
        console.error("Speech recognition error", event.error);
        showStatus("माफ़ करें, मैं सुन नहीं पाया। (Sorry, I couldn't hear.)");
        stopListening();
    };
    
    recognition.onend = function() {
        stopListening();
        showStatus("");
    };
} else {
    console.warn("Speech Recognition API not supported in this browser.");
    micBtn.style.display = 'none';
    showStatus("आपका ब्राउज़र वॉइस इनपुट का समर्थन नहीं करता है। (Speech recognition not supported.)");
}

micBtn.addEventListener("click", () => {
    if (!SpeechRecognition) return;
    
    if (isListening) {
        recognition.stop();
    } else {
        // Set language based on selection
        const langCode = languageSelect.value;
        if (langCode === 'hi') {
            recognition.lang = 'hi-IN';
        } else if (langCode === 'ta') {
            recognition.lang = 'ta-IN';
        } else {
            recognition.lang = 'en-IN';
        }
        
        try {
            recognition.start();
        } catch (e) {
            console.error("Could not start recognition", e);
        }
    }
});

function stopListening() {
    isListening = false;
    micBtn.classList.remove("listening");
}

// Text to Speech
window.speakText = function(text) {
    if (!window.speechSynthesis) {
        console.warn("Speech Synthesis API not supported.");
        return;
    }
    
    // Process text to remove some markdown components if necessary for TTS
    const cleanText = text.replace(/[*_~`]/g, '');
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    
    // Set language
    const langCode = languageSelect.value;
    if (langCode === 'hi') {
        utterance.lang = 'hi-IN';
    } else if (langCode === 'ta') {
        utterance.lang = 'ta-IN';
    } else {
        utterance.lang = 'en-IN';
    }
    
    window.speechSynthesis.speak(utterance);
};
