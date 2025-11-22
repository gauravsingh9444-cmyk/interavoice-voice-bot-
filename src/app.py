from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from datastore import DataStore
from intent_engine import IntentEngine
from logger_utils import get_logger

logger = get_logger("App")

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../web/static",
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


if __name__ == "__main__":
    print(">>> InteraVoice running at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
