# InteraVoice – Intelligent Voice Bot for Customer Interaction

InteraVoice is a prototype AI assistant built as part of an intern assignment on  
**“Building an Intelligent Voice Bot for Customer Interaction.”**  
It focuses on handling basic customer queries using:

- A lightweight NLU (intent matching using similarity)
- A small FAQ “database”
- A web-based chat UI
- Logging that can be used for analytics

> Note: This implementation currently demonstrates the text-based flow.  
> Voice (speech-to-text / text-to-speech) can be added on top of this backend  
> using browser APIs or external STT/TTS services.

---

## 1. Project Objective

The goal of InteraVoice is to show an end-to-end flow:

1. User enters a query in the web UI  
2. Frontend sends it to a Flask backend (`/ask` API)  
3. Backend:
   - Logs the query
   - Uses a small intent engine to find the closest matching FAQ
   - Returns the appropriate answer
4. Frontend displays the bot’s reply

This matches the assignment idea of a **customer-facing voice/chat bot** with a  
clear backend + NLU + data layer.

---

## 2. Tech Stack

**Backend:**

- Python 3
- Flask (REST API + HTML templates)
- flask-cors (for safe browser requests)
- Custom `IntentEngine` using `difflib.SequenceMatcher`
- JSON-based “database” (`data/faqs.json`)
- Custom logger utility writing to `logs/`

**Frontend:**

- HTML (served from `templates/interavoice.html`)
- CSS (`web/static/interavoice.css`)
- Vanilla JavaScript (`web/static/interavoice.js`)

---

## 3. Project Structure

```text
interavoice-voice-bot-/
├─ data/
│  └─ faqs.json           # FAQ "database" (questions + answers)
├─ logs/
│  └─ interavoice_*.log   # created at runtime by logger_utils
├─ src/
│  ├─ app.py              # Flask app, routes and API
│  ├─ datastore.py        # loads and exposes FAQ data
│  ├─ intent_engine.py    # simple NLU / intent matching logic
│  └─ logger_utils.py     # shared logging setup
├─ templates/
│  └─ interavoice.html    # main chat UI page
├─ web/
│  └─ static/
│     ├─ interavoice.css  # styling for the chat
│     └─ interavoice.js   # frontend logic (calls /ask API)
├─ requirements.txt       # Python dependencies
└─ README.md
