const micBtn = document.getElementById("mic-btn");
const languageSelect = document.getElementById("language-select");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;
let isSpeaking = false;
let currentUtterance = null;

const INDIAN_LANG_MAP = {
    "hi": "hi-IN",
    "en": "en-IN",
    "mr": "mr-IN",
    "bn": "bn-IN",
    "te": "te-IN",
    "ta": "ta-IN",
    "kn": "kn-IN",
    "gu": "gu-IN",
    "pa": "pa-IN",
    "or": "or-IN",
    "ml": "ml-IN",
    "as": "as-IN",
    "ur": "ur-IN",
};

function getRecognitionLang() {
    const langCode = languageSelect.value;
    if (langCode === "hi") return "hi-IN";
    if (langCode === "en") return "en-IN";

    const nav = (navigator.language || "").toLowerCase();
    for (const [code, bcp] of Object.entries(INDIAN_LANG_MAP)) {
        if (nav.startsWith(code)) return bcp;
    }
    return "hi-IN";
}

function selectBestVoice(langCode) {
    const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    if (!voices.length) return null;

    const targetLang = INDIAN_LANG_MAP[langCode] || "hi-IN";
    const langPrefix = targetLang.split("-")[0];

    const preferredKeywords = ["google", "microsoft", "neural", "natural", "premium", "wavenet"];
    const fallbackKeywords = ["female", "zira", "heera", "swara"];

    let bestVoice = null;
    let bestScore = -1;

    for (const voice of voices) {
        if (!voice.lang.toLowerCase().startsWith(langPrefix)) continue;
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
    if (btn) {
        btn.classList.remove("hidden");
        btn.classList.add("flex");
    }
}

function hideStopButton() {
    const btn = document.getElementById("stop-speech-btn");
    if (btn) {
        btn.classList.add("hidden");
        btn.classList.remove("flex");
    }
}

function updateVoiceOrb() {
    const orb = document.getElementById("mic-btn");
    if (!orb) return;

    orb.classList.remove("listening", "speaking");

    const micIcon = orb.querySelector(".material-symbols-outlined");

    if (isListening) {
        orb.classList.add("listening");
        if (micIcon) micIcon.textContent = "hearing";
    } else if (isSpeaking) {
        orb.classList.add("speaking");
        if (micIcon) micIcon.textContent = "volume_up";
    } else {
        if (micIcon) micIcon.textContent = "mic";
    }
}

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = function () {
        isListening = true;
        updateVoiceOrb();
        if (window.showStatus) window.showStatus(window.t ? window.t("listening") : "Listening...");
    };

    recognition.onresult = function (event) {
        let finalTranscript = "";
        let interimTranscript = "";

        for (let i = 0; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }

        const textInput = document.getElementById("text-input");

        if (finalTranscript) {
            textInput.value = finalTranscript;
            if (window.showStatus) window.showStatus(window.t ? window.t("understood") : "Understood!");
            setTimeout(sendTextMessage, 400);
        } else if (interimTranscript) {
            textInput.value = interimTranscript;
        }
    };

    recognition.onerror = function (event) {
        console.error("Speech recognition error", event.error);

        if (event.error === "not-allowed" || event.error === "service-not-allowed") {
            if (window.showStatus) window.showStatus("Microphone access denied. Please allow microphone in browser settings.");
        } else if (event.error === "no-speech") {
            if (window.showStatus) window.showStatus("No speech detected. Try again.");
        } else if (event.error === "network") {
            if (window.showStatus) window.showStatus("Network error. Check your connection.");
        } else {
            if (window.showStatus) window.showStatus(window.t ? window.t("hearError") : "Sorry, I couldn't hear you.");
        }
        stopListening();
    };

    recognition.onend = function () {
        stopListening();
    };

    micBtn.addEventListener("click", () => {
        if (isSpeaking) {
            stopSpeaking();
            return;
        }

        if (isListening) {
            recognition.stop();
        } else {
            recognition.lang = getRecognitionLang();
            try {
                recognition.start();
            } catch (e) {
                console.error("Could not start recognition", e);
                if (e.message && e.message.includes("already started")) {
                    recognition.stop();
                    setTimeout(() => {
                        recognition.lang = getRecognitionLang();
                        recognition.start();
                    }, 300);
                }
            }
        }
    });
} else {
    micBtn.disabled = true;
    micBtn.classList.add("mic-disabled");
    micBtn.innerHTML = '<span class="material-symbols-outlined text-2xl">mic_off</span>';

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
    if (window.showStatus) window.showStatus("");
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
        .replace(/https?:\/\/\S+/g, "")
        .replace(/\n{2,}/g, ". ")
        .replace(/\n/g, ". ")
        .replace(/\s{2,}/g, " ")
        .replace(/\. \./g, ".")
        .trim();

    if (!cleanText || cleanText.length < 2) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);

    const langCode = responseLang || languageSelect.value || "hi";
    const resolvedLang = INDIAN_LANG_MAP[langCode] || "hi-IN";
    utterance.lang = resolvedLang;

    const voice = selectBestVoice(langCode);
    if (voice) {
        utterance.voice = voice;
    }

    utterance.rate = 0.88;
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

    utterance.onerror = function (e) {
        if (e.error !== "interrupted") {
            console.warn("TTS error:", e.error);
        }
        isSpeaking = false;
        currentUtterance = null;
        updateVoiceOrb();
        hideStopButton();
    };

    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
};

window.stopSpeaking = stopSpeaking;
window.isSpeaking = () => isSpeaking;

const textInput = document.getElementById("text-input");
if (textInput) {
    textInput.addEventListener("input", () => {
        if (isSpeaking) stopSpeaking();
    });
}
