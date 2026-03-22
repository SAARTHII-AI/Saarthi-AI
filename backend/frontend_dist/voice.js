const micBtn = document.getElementById("mic-btn");
const languageSelect = document.getElementById("language-select");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;
let isSpeaking = false;
let currentUtterance = null;
let speechQueue = [];

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

const FEMALE_VOICE_NAMES = [
    "heera", "swara", "kalpana", "shruti",
    "zira", "hazel", "susan", "samantha", "karen",
    "monika", "amala", "aditi", "raveena", "priya",
    "neerja", "lekha", "meera", "female",
    "google हिन्दी", "google hindi",
    "google বাংলা", "google తెలుగు", "google தமிழ்",
    "google ગુજરાતી", "google ಕನ್ನಡ", "google മലയാളം",
];

const MALE_VOICE_NAMES = [
    "ravi", "hemant", "male", "madhur", "prabhat",
];

function getRecognitionLang() {
    const langCode = languageSelect.value;
    if (langCode && INDIAN_LANG_MAP[langCode]) {
        return INDIAN_LANG_MAP[langCode];
    }
    const nav = (navigator.language || "").toLowerCase();
    for (const [code, bcp] of Object.entries(INDIAN_LANG_MAP)) {
        if (nav.startsWith(code)) return bcp;
    }
    return "hi-IN";
}

function resolveLangCode(langCode) {
    if (!langCode) return { short: "hi", bcp: "hi-IN" };
    if (INDIAN_LANG_MAP[langCode]) return { short: langCode, bcp: INDIAN_LANG_MAP[langCode] };
    const lower = langCode.toLowerCase();
    for (const [code, bcp] of Object.entries(INDIAN_LANG_MAP)) {
        if (lower === bcp.toLowerCase() || lower.startsWith(code + "-")) {
            return { short: code, bcp: bcp };
        }
    }
    return { short: langCode.split("-")[0], bcp: langCode };
}

function selectBestVoice(langCode) {
    const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    if (!voices.length) return null;

    const resolved = resolveLangCode(langCode);
    const targetLang = resolved.bcp;
    const langPrefix = resolved.short;

    let bestVoice = null;
    let bestScore = -1;

    for (const voice of voices) {
        if (!voice.lang.toLowerCase().startsWith(langPrefix)) continue;

        let score = 0;
        const nameLower = voice.name.toLowerCase();

        if (voice.lang === targetLang) score += 2;

        const isFemale = FEMALE_VOICE_NAMES.some(fn => nameLower.includes(fn));
        const isMale = MALE_VOICE_NAMES.some(mn => nameLower.includes(mn));

        if (isFemale && !isMale) score += 10;
        if (isMale && !isFemale) score -= 5;

        const premiumKeywords = ["neural", "natural", "premium", "wavenet", "enhanced"];
        for (const kw of premiumKeywords) {
            if (nameLower.includes(kw)) { score += 6; break; }
        }

        const providerKeywords = ["google", "microsoft"];
        for (const kw of providerKeywords) {
            if (nameLower.includes(kw)) { score += 4; break; }
        }

        if (!voice.localService) score += 2;

        if (score > bestScore) {
            bestScore = score;
            bestVoice = voice;
        }
    }

    if (bestVoice) {
        console.log(`[SaarthiAI] Selected voice: "${bestVoice.name}" (${bestVoice.lang})`);
    }

    return bestVoice;
}

function stopSpeaking() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
    speechQueue = [];
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

function cleanTextForSpeech(text) {
    return text
        .replace(/\*\*(.+?)\*\*/g, "$1")
        .replace(/\*(.+?)\*/g, "$1")
        .replace(/#{1,3}\s*/g, "")
        .replace(/[_~`]/g, "")
        .replace(/https?:\/\/\S+/g, "")
        .replace(/[─━═▬]{2,}/g, "")
        .replace(/[💰✅📄📞🔗📋📍🛡️📝🌐]/g, "")
        .replace(/\d+\)\s*/g, "")
        .replace(/[-•]\s*/g, "")
        .replace(/\(\s*\)/g, "")
        .replace(/\n{2,}/g, ". ")
        .replace(/\n/g, ". ")
        .replace(/\.\s*\./g, ".")
        .replace(/\s{2,}/g, " ")
        .replace(/,\s*,/g, ",")
        .trim();
}

function splitAtBoundary(text, maxLen, separatorPattern) {
    if (text.length <= maxLen) return [text];

    const parts = text.split(separatorPattern).filter(p => p.length > 0);
    const chunks = [];
    let current = "";

    for (const part of parts) {
        if (current.length + part.length + 1 > maxLen && current.length > 0) {
            chunks.push(current.trim());
            current = part;
        } else {
            current += (current ? " " : "") + part;
        }
    }
    if (current.trim()) chunks.push(current.trim());
    return chunks;
}

function splitTextIntoChunks(text, maxLen) {
    if (text.length <= maxLen) return [text];

    let chunks = splitAtBoundary(text, maxLen, /[।.!?]+\s*/);

    const result = [];
    for (const chunk of chunks) {
        if (chunk.length <= maxLen) {
            result.push(chunk);
        } else {
            const commaChunks = splitAtBoundary(chunk, maxLen, /[,;:]\s*/);
            for (const cc of commaChunks) {
                if (cc.length <= maxLen) {
                    result.push(cc);
                } else {
                    const words = cc.split(/\s+/);
                    let line = "";
                    for (const word of words) {
                        if (line.length + word.length + 1 > maxLen && line.length > 0) {
                            result.push(line.trim());
                            line = word;
                        } else {
                            line += (line ? " " : "") + word;
                        }
                    }
                    if (line.trim()) result.push(line.trim());
                }
            }
        }
    }

    return result;
}

function speakNextChunk() {
    if (speechQueue.length === 0) {
        isSpeaking = false;
        currentUtterance = null;
        updateVoiceOrb();
        hideStopButton();
        return;
    }

    const { text, langCode, voice } = speechQueue.shift();
    const resolvedLang = INDIAN_LANG_MAP[langCode] || "hi-IN";

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = resolvedLang;

    if (voice) utterance.voice = voice;

    utterance.rate = 0.92;
    utterance.pitch = 1.12;
    utterance.volume = 1.0;

    utterance.onstart = function () {
        isSpeaking = true;
        updateVoiceOrb();
        showStopButton();
    };

    utterance.onend = function () {
        speakNextChunk();
    };

    utterance.onerror = function (e) {
        if (e.error !== "interrupted") {
            console.warn("TTS error:", e.error);
        }
        speechQueue = [];
        isSpeaking = false;
        currentUtterance = null;
        updateVoiceOrb();
        hideStopButton();
    };

    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
}

window.speakText = function (text, responseLang = null) {
    if (!window.speechSynthesis) {
        console.warn("Speech Synthesis API not supported.");
        return;
    }

    stopSpeaking();

    const cleanText = cleanTextForSpeech(text);
    if (!cleanText || cleanText.length < 2) return;

    const langCode = responseLang || languageSelect.value || "hi";
    const voice = selectBestVoice(langCode);

    const chunks = splitTextIntoChunks(cleanText, 180);

    speechQueue = chunks.map(chunk => ({
        text: chunk,
        langCode: langCode,
        voice: voice,
    }));

    speakNextChunk();
};

window.stopSpeaking = stopSpeaking;
window.isSpeaking = () => isSpeaking;

const textInput = document.getElementById("text-input");
if (textInput) {
    textInput.addEventListener("input", () => {
        if (isSpeaking) stopSpeaking();
    });
}
