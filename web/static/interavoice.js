const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const messagesDiv = document.getElementById("messages");

// Voice recording variables
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Create and add voice button
function initializeVoiceButton() {
    const voiceBtn = document.createElement("button");
    voiceBtn.id = "voice-btn";
    voiceBtn.innerHTML = "🎤";
    voiceBtn.title = "Start/Stop Voice Recording";
    voiceBtn.style.marginLeft = "10px";
    voiceBtn.style.padding = "10px 15px";
    voiceBtn.style.border = "none";
    voiceBtn.style.borderRadius = "5px";
    voiceBtn.style.cursor = "pointer";
    voiceBtn.style.background = "#28a745";
    voiceBtn.style.color = "white";
    voiceBtn.style.fontSize = "16px";

    voiceBtn.addEventListener("click", toggleRecording);
    
    // Insert voice button after the send button
    sendBtn.parentNode.insertBefore(voiceBtn, sendBtn.nextSibling);
}

function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = processAudio;

        mediaRecorder.start();
        isRecording = true;
        updateVoiceButton(true);
        addMessage("🔴 Recording... Speak now", "system");
        
    } catch (error) {
        console.error("Error accessing microphone:", error);
        addMessage("❌ Microphone access denied. Please allow microphone permissions.", "system");
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;
        updateVoiceButton(false);
    }
}

async function processAudio() {
    try {
        addMessage("🔄 Processing voice...", "system");
        
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob);

        console.log("Audio blob size:", audioBlob.size, "bytes");
        
        // Send audio to backend for speech-to-text
        const response = await fetch('/speech-to-text', {
            method: 'POST',
            body: formData
        });

        console.log("Response status:", response.status);
        const data = await response.json();
        console.log("Response data:", data);
        
        if (data.text && data.text.trim()) {
            addMessage(`✅ Transcribed: "${data.text}"`, "system");
            // Update the input field with transcribed text
            input.value = data.text;
            // Auto-send the message
            sendMessage();
        } else if (data.error) {
            addMessage(`❌ ${data.error}`, "system");
        } else {
            addMessage("❌ Could not understand audio. Please try again.", "system");
        }
        
    } catch (error) {
        console.error("Error processing audio:", error);
        addMessage("❌ Error processing voice input. Please try again.", "system");
    }
}

function updateVoiceButton(recording) {
    const voiceBtn = document.getElementById("voice-btn");
    if (voiceBtn) {
        voiceBtn.innerHTML = recording ? "⏹️" : "🎤";
        voiceBtn.style.background = recording ? "#dc3545" : "#28a745";
        voiceBtn.title = recording ? "Stop Recording" : "Start Voice Recording";
    }
}

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.textContent = text;
    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    try {
        const res = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: text })
        });

        const data = await res.json();
        addMessage(data.answer, "bot");
        
        // Speak the bot's response
        speakText(data.answer);
        
    } catch (error) {
        console.error("Error:", error);
        addMessage("❌ Sorry, there was an error processing your request.", "system");
    }
}

// Temporary: Test if audio is being recorded
function testAudioRecording() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    console.log("Audio recorded:", {
        chunks: audioChunks.length,
        blobSize: audioBlob.size,
        blobType: audioBlob.type
    });
    
    // Create a temporary audio element to play back what was recorded
    const audioUrl = URL.createObjectURL(audioBlob);
    const testAudio = new Audio(audioUrl);
    testAudio.controls = true;
    testAudio.style.position = 'fixed';
    testAudio.style.bottom = '10px';
    testAudio.style.right = '10px';
    testAudio.style.zIndex = '1000';
    document.body.appendChild(testAudio);
    
    addMessage("🔊 Test: Can you hear your recording?", "system");
}

// Text-to-Speech function
function speakText(text) {
    if ('speechSynthesis' in window) {
        // Stop any ongoing speech
        window.speechSynthesis.cancel();
        
        const speech = new SpeechSynthesisUtterance();
        speech.text = text;
        speech.volume = 1;
        speech.rate = 0.9;
        speech.pitch = 1;
        
        // Optional: Try to get a pleasant voice
        const voices = speechSynthesis.getVoices();
        const englishVoice = voices.find(voice => 
            voice.lang.includes('en') && voice.name.includes('Female')
        ) || voices.find(voice => voice.lang.includes('en'));
        
        if (englishVoice) {
            speech.voice = englishVoice;
        }
        
        window.speechSynthesis.speak(speech);
    }
}

// Load voices when available (for better TTS)
if ('speechSynthesis' in window) {
    speechSynthesis.onvoiceschanged = function() {
        // Voices are loaded
    };
}

// Event listeners
sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// Initialize voice features when page loads
document.addEventListener("DOMContentLoaded", function() {
    initializeVoiceButton();
});