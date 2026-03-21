const micBtn = document.getElementById("mic-btn");
const languageSelect = document.getElementById("language-select");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;
let isSpeaking = false;
let currentUtterance = null;

function selectBestVoice(langCode) {
    const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    if (!voices.length) return null;

    const langMap = {
        "hi": "hi-IN",
        "en": "en-IN",
    };
    const targetLang = langMap[langCode] || "hi-IN";

    const preferredKeywords = ["google", "microsoft", "neural", "natural", "premium"];
    const fallbackKeywords = ["female", "zira", "heera"];

    let bestVoice = null;
    let bestScore = -1;

    for (const voice of voices) {
        if (!voice.lang.startsWith(targetLang.split("-")[0])) continue;
        let score = 0;
        const nameLower = voice.name.toLowerCase();

        if (voice.lang === targetLang) score += 2;

        for (const kw of preferredKeywords) {
            if (nameLower.includes(kw)) { score += 3; break; }
        }
        for (const kw of fallbackKeywords) {
            if (nameLower.includes(kw)) { score += 1; break; }
        }

        if (!voice.localService) score += 1;

        if (score > bestScore) {
            bestScore = score;
            bestVoice = voice;
        }
    }

    return bestVoice;
}

function stopSpeaking() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
    isSpeaking = false;
    currentUtterance = null;
    updateVoiceOrb();
    hideStopButton();
}

function showStopButton() {
    const btn = document.getElementById("stop-speech-btn");
    if (btn) btn.classList.remove("hidden");
}

function hideStopButton() {
    const btn = document.getElementById("stop-speech-btn");
    if (btn) btn.classList.add("hidden");
}

function updateVoiceOrb() {
    const orb = document.getElementById("mic-btn");
    if (!orb) return;

    orb.classList.remove("listening", "speaking");
    if (isListening) {
        orb.classList.add("listening");
    } else if (isSpeaking) {
        orb.classList.add("speaking");
    }
}

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function () {
        isListening = true;
        updateVoiceOrb();
        if (window.showStatus) showStatus(window.t ? window.t("listening") : "Listening...");
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("text-input").value = transcript;
        if (window.showStatus) showStatus(window.t ? window.t("understood") : "Understood!");
        setTimeout(sendTextMessage, 400);
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
        if (isSpeaking) {
            stopSpeaking();
            return;
        }

        if (isListening) {
            recognition.stop();
        } else {
            const langCode = languageSelect.value;
            if (langCode === "hi") {
                recognition.lang = "hi-IN";
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
    micBtn.disabled = true;
    micBtn.classList.add("mic-disabled");
    micBtn.innerHTML = '<span class="material-symbols-outlined text-3xl">mic_off</span>';

    const hint = document.getElementById("mic-unsupported-hint");
    if (hint) {
        hint.classList.remove("hidden");
        hint.textContent = "Voice not supported on this browser — please type your message.";
    }

    const setMicLabel = () => {
        const msg = window.t ? window.t("micUnsupported") : "Voice not supported on this browser";
        micBtn.title = msg;
        micBtn.setAttribute("aria-label", msg);
        if (hint) hint.textContent = msg;
    };
    document.addEventListener("DOMContentLoaded", setMicLabel);
}

function stopListening() {
    isListening = false;
    updateVoiceOrb();
}

if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = function () {};
}

window.speakText = function (text, responseLang = null) {
    if (!window.speechSynthesis) {
        console.warn("Speech Synthesis API not supported.");
        return;
    }

    stopSpeaking();

    const cleanText = text
        .replace(/[*_~`#]/g, "")
        .replace(/\n{2,}/g, ". ")
        .replace(/\n/g, ". ")
        .replace(/\s{2,}/g, " ")
        .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);

    const langCode = responseLang || languageSelect.value;
    if (langCode === "hi") {
        utterance.lang = "hi-IN";
    } else {
        utterance.lang = "en-IN";
    }

    const voice = selectBestVoice(langCode === "hi" ? "hi" : "en");
    if (voice) {
        utterance.voice = voice;
    }

    utterance.rate = 0.9;
    utterance.pitch = 1.05;
    utterance.volume = 1.0;

    utterance.onstart = function () {
        isSpeaking = true;
        updateVoiceOrb();
        showStopButton();
    };

    utterance.onend = function () {
        isSpeaking = false;
        currentUtterance = null;
        updateVoiceOrb();
        hideStopButton();
    };

    utterance.onerror = function () {
        isSpeaking = false;
        currentUtterance = null;
        updateVoiceOrb();
        hideStopButton();
    };

    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
};

window.stopSpeaking = stopSpeaking;

const textInput = document.getElementById("text-input");
if (textInput) {
    textInput.addEventListener("focus", () => {
        if (isSpeaking) stopSpeaking();
    });
}
