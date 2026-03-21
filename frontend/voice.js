// Voice recognition and synthesis using Web Speech API

const micBtn = document.getElementById("mic-btn");
const languageSelect = document.getElementById("language-select");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function () {
        isListening = true;
        micBtn.classList.add("listening");
        if (window.showStatus) showStatus(window.t ? window.t("listening") : "Listening...");
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("text-input").value = transcript;
        if (window.showStatus) showStatus(window.t ? window.t("understood") : "Understood!");
        setTimeout(sendTextMessage, 500);
    };

    recognition.onerror = function (event) {
        console.error("Speech recognition error", event.error);
        if (window.showStatus) showStatus(window.t ? window.t("hearError") : "Sorry, I couldn't hear you.");
        stopListening();
    };

    recognition.onend = function () {
        stopListening();
        if (window.showStatus) showStatus("");
    };

    micBtn.addEventListener("click", () => {
        if (isListening) {
            recognition.stop();
        } else {
            const langCode = languageSelect.value;
            if (langCode === "hi") {
                recognition.lang = "hi-IN";
            } else if (langCode === "ta") {
                recognition.lang = "ta-IN";
            } else if (langCode === "en") {
                recognition.lang = "en-IN";
            } else {
                recognition.lang = "hi-IN";
            }
            try {
                recognition.start();
            } catch (e) {
                console.error("Could not start recognition", e);
            }
        }
    });
} else {
    // Mic not supported — show disabled state instead of hiding
    micBtn.disabled = true;
    micBtn.title = "Voice not supported on this browser";
    micBtn.setAttribute("aria-label", "Voice not supported on this browser");
    micBtn.classList.add("mic-disabled");

    // Replace inner icon with mic_off
    micBtn.innerHTML = '<span class="material-symbols-outlined text-3xl">mic_off</span>';

    // Show a text hint below the input area
    const hint = document.getElementById("mic-unsupported-hint");
    if (hint) {
        hint.classList.remove("hidden");
    }
}

function stopListening() {
    isListening = false;
    micBtn.classList.remove("listening");
}

// Text to Speech
window.speakText = function (text, responseLang = null) {
    if (!window.speechSynthesis) {
        console.warn("Speech Synthesis API not supported.");
        return;
    }

    const cleanText = text.replace(/[*_~`]/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanText);

    const langCode = responseLang || languageSelect.value;
    if (langCode === "hi") {
        utterance.lang = "hi-IN";
    } else if (langCode === "ta") {
        utterance.lang = "ta-IN";
    } else {
        utterance.lang = "en-IN";
    }

    window.speechSynthesis.speak(utterance);
};
