from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datastore import DataStore
from intent_engine import IntentEngine
from logger_utils import get_logger
import os
import speech_recognition as sr
import tempfile
import wave
import audioop

logger = get_logger("App")

# Use absolute paths
template_path = "/workspaces/interavoice-voice-bot-/web/templates"
static_path = "/workspaces/interavoice-voice-bot-/web/static"

app = Flask(
    __name__,
    template_folder=template_path,
    static_folder=static_path,
)

CORS(app)

store = DataStore()
engine = IntentEngine()

@app.route("/")
def home():
    logger.info("Serving UI page")
    return render_template("interavoice.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()

    logger.info("Received user message: %s", question)

    if not question:
        return jsonify({"answer": "Please type a question first."}), 400

    faqs = store.all_faqs()
    match = engine.best_match(question, faqs)

    if match:
        answer = match["answer"]
    else:
        answer = (
            "I'm not fully sure about that. "
            "Try asking about InteraVoice, support, or pricing."
        )

    logger.info("Final answer: %s", answer)

    return jsonify({"answer": answer})

@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    temp_audio_path = None
    try:
        if 'audio' not in request.files:
            logger.error("No audio file in request")
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            logger.error("Empty audio filename")
            return jsonify({"error": "No audio file selected"}), 400
        
        # Get file size for debugging
        audio_data = audio_file.read()
        audio_file_size = len(audio_data)
        logger.info(f"Processing audio file: {audio_file.filename}, size: {audio_file_size} bytes")
        
        if audio_file_size == 0:
            logger.error("Empty audio file")
            return jsonify({"error": "Empty audio file recorded"}), 400
        
        # Reset file pointer and save to temporary file
        audio_file.seek(0)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name
        
        # Initialize speech recognizer
        recognizer = sr.Recognizer()
        
        # Configure recognizer settings for better accuracy
        recognizer.energy_threshold = 300  # Adjust for sensitivity
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8   # Longer pause detection
        
        try:
            # Process the audio file
            with sr.AudioFile(temp_audio_path) as source:
                logger.info("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                logger.info("Recording audio...")
                audio_data = recognizer.record(source)
                
                # Log audio properties
                duration = len(audio_data.frame_data) / (audio_data.sample_rate * audio_data.sample_width)
                logger.info(f"Audio duration: {duration:.2f} seconds, Sample rate: {audio_data.sample_rate}Hz")
                
            logger.info("Sending to Google Speech Recognition...")
            
            # Use Google Speech Recognition with better configuration
            text = recognizer.recognize_google(
                audio_data,
                language='en-US',  # Specify English
                show_all=False     # Get only the best result
            )
            
            logger.info(f"Speech-to-text successful: '{text}'")
            
            return jsonify({"text": text.strip()})
            
        except sr.UnknownValueError:
            logger.error("Google Speech Recognition could not understand the audio")
            return jsonify({"error": "Could not understand audio. Please speak clearly and try again."}), 400
            
        except sr.RequestError as e:
            logger.error(f"Error with Google Speech Recognition service: {e}")
            return jsonify({"error": "Speech recognition service unavailable. Please check your internet connection."}), 500
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return jsonify({"error": "Error processing audio file"}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in speech-to-text: {e}")
        return jsonify({"error": "Internal server error processing audio"}), 500
        
    finally:
        # Always clean up temporary file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
                logger.debug("Cleaned up temporary audio file")
            except Exception as e:
                logger.warning(f"Could not delete temp file {temp_audio_path}: {e}")

@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        logger.info(f"Text-to-speech request: '{text}'")
        
        return jsonify({
            "message": "Text received for speech synthesis",
            "text": text,
            "note": "Currently using client-side TTS. Integrate cloud TTS service here if needed."
        })
        
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "InteraVoice API",
        "features": ["text-chat", "speech-to-text", "text-to-speech"]
    })

@app.route("/debug-audio", methods=["POST"])
def debug_audio():
    """Debug endpoint to check audio file properties"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 400
            
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        return jsonify({
            "filename": audio_file.filename,
            "size_bytes": len(audio_data),
            "content_type": audio_file.content_type
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🎯 InteraVoice Voice Bot Started!")
    print("📍 Running at: http://0.0.0.0:5000")
    print("🔊 Voice Features: ENABLED (Google Speech Recognition)")
    print("")
    print("📡 Available Endpoints:")
    print("   GET  /                 - Web Interface")
    print("   POST /ask              - Text Chat")
    print("   POST /speech-to-text   - Voice Input")
    print("   POST /text-to-speech   - Voice Output")
    print("   GET  /health           - Health Check")
    print("   POST /debug-audio      - Audio Debug")
    print("")
    print("🎤 Voice Recording Tips:")
    print("   - Speak clearly into your microphone")
    print("   - Ensure microphone permissions are granted")
    print("   - Keep background noise to a minimum")
    print("")
    
    app.run(host="0.0.0.0", port=5000, debug=True)