from flask import Flask, request, jsonify, render_template

# Create the Flask app
app = Flask(
    __name__,
    template_folder="../web/templates",
    static_folder="../web/static",
)


# Home page -> serves the HTML UI
@app.route("/")
def home():
    return render_template("interavoice.html")


# API endpoint the frontend calls
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"answer": "Please type a question first."}), 400

    # Very simple reply for now
    answer = f"You asked: '{question}'. I am InteraVoice, a demo bot."

    return jsonify({"answer": answer})


# This part actually starts the server
if __name__ == "__main__":
    print(">>> InteraVoice starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
