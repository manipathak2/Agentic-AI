// ==============================
// 🎤 Voice Assistant Engine (FIXED)
// ==============================

let recognition;
let isListening = false;
let isActive = true;
let isAwake = true;
let isSpeaking = false;

const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

// ==============================
// 🌊 UI STATES
// ==============================
function setThinkingState() {
    document.body.classList.remove("voice-speaking");
}

function setSpeakingState() {
    document.body.classList.add("voice-speaking");
}

// ==============================
// 🎯 MIC UI
// ==============================
function setMicListening(active) {
    const mic = document.getElementById("micButton");
    if (!mic) return;

    active ? mic.classList.add("listening") : mic.classList.remove("listening");
}

// ==============================
// ✅ INIT SPEECH RECOGNITION
// ==============================
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    // 🎤 START
    recognition.onstart = () => {
        isListening = true;
        setMicListening(true);
        console.log("🎤 Listening started");
    };

    // 🔁 END
    recognition.onend = () => {
        isListening = false;

        if (isActive && !isSpeaking) {
            console.log("🔁 Restarting recognition...");
            try {
                recognition.start();
            } catch (e) { }
        } else {
            setMicListening(false);
        }
    };

    // 🧠 RESULT
    recognition.onresult = async (event) => {
        const transcriptRaw =
            event.results[event.results.length - 1][0].transcript;

        const transcript = transcriptRaw.trim().toLowerCase();

        // 🚫 IGNORE NOISE
        if (transcript.length < 3) return;

        console.log("🗣 Heard:", transcript);

        // 🚫 PREVENT SELF LISTENING (MAIN FIX)
        if (isSpeaking) {
            console.log("⚠️ Ignoring self voice (echo prevention)");
            return;
        }

        // ==========================
        // 🔴 SHUTDOWN
        // ==========================
        if (
            transcript.includes("shutdown") ||
            transcript.includes("shut down") ||
            transcript.includes("stop assistant") ||
            transcript.includes("exit") ||
            transcript.includes("quit")
        ) {
            isActive = false;
            isAwake = false;

            window.speechSynthesis.cancel();
            speak("Shutting down. Goodbye.");

            recognition.stop();

            setTimeout(() => {
                window.location.href = "/";
            }, 2000);

            return;
        }

        // ==========================
        // 🧠 WAKE WORD
        // ==========================
        if (
            transcript.includes("hey xaros") ||
            transcript.includes("wake up")
        ) {
            speak("Yes, I'm listening.");
            return;
        }

        // ==========================
        // 🤖 THINKING STATE
        // ==========================
        document.getElementById("loaderWrap").style.display = "flex";
        setThinkingState();

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: transcript,
                    is_voice: true
                })
            });

            const data = await response.json();

            // hide loader
            document.getElementById("loaderWrap").style.display = "flex";

            speak(data.reply);

        } catch (err) {
            console.error("❌ Error:", err);
            speak("Sorry, something went wrong.");
        }
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
    };

} else {
    alert("Speech recognition not supported in this browser.");
}

// ==============================
// 🔊 SPEAK FUNCTION (FIXED)
// ==============================
function speak(text) {
    if (!text) return;

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(text);
    speech.rate = 1;
    speech.pitch = 1;
    speech.volume = 1;

    isSpeaking = true;

    // 🔥 STOP MIC
    if (isListening) {
        try { recognition.stop(); } catch (e) { }
    }

    // 🔥 SHOW FULL SCREEN TEXT
    const el = document.getElementById("aiResponseText");
    if (el) {
        let i = 0;
        el.innerText = "";

        const typing = setInterval(() => {
            el.innerText = text.slice(0, i);
            i++;
            if (i >= text.length) clearInterval(typing);
        }, 20);
    }

    setSpeakingState();

    speech.onend = () => {
        isSpeaking = false;

        // clear text after speaking
        const el = document.getElementById("aiResponseText");
        if (el) {
            el.innerText = "";
        }

        setThinkingState();

        setTimeout(() => {
            if (isActive && !isListening) {
                try { recognition.start(); } catch (e) { }
            }
        }, 800);
    };

    window.speechSynthesis.speak(speech);
}

// ==============================
// 🚀 AUTO START
// ==============================
window.onload = () => {
    try {
        recognition.start();
    } catch (e) { }
};

// ==============================
// ❌ EXIT BUTTON FIX
// ==============================
function exitVoice() {
    isActive = false;
    isAwake = false;

    window.speechSynthesis.cancel();

    try {
        recognition.stop();
    } catch (e) { }

    window.location.href = "/";
}