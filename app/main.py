import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template
from executor import run_code_in_docker
import json
import datetime

# ---------- FIX: ABSOLUTE HISTORY FILE PATH ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # /path/to/app
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
print("Using history file at:", HISTORY_FILE)


app = Flask(__name__)


# ---------- Helper: Save Execution History ----------
def save_history(entry):
    """Save execution entry to history.json (max 10 entries)."""
    try:
        # Load existing history
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []

        # Add new entry
        history.append(entry)

        # Keep only last 10 entries
        history = history[-10:]

        # Save back to file
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

    except Exception as e:
        print("History save error:", e)


# ---------- Routes ----------

@app.route("/")
def home():
    return "Safe Code Executor API is running!", 200


@app.route("/ui")
def ui_page():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json(silent=True)

    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field"}), 400

    # Language (default = python)
    language = data.get("language", "python").lower()
    code = data["code"]

    # Code length limit
    if len(code) > 5000:
        return jsonify({
            "error": "Code too long. Maximum allowed length is 5000 characters."
        }), 400

    # Supported languages
    if language not in ["python", "javascript", "js"]:
        return jsonify({"error": f"Unsupported language: {language}"}), 400

    # Execute in Docker
    result = run_code_in_docker(language, code)

    # Prepare history entry
    history_entry = {
        "language": language,
        "code": code,
        "output": result["stdout"],
        "error": result["stderr"],
        "exit_code": result["exit_code"],
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save history
    save_history(history_entry)

    # Return result
    if result["exit_code"] == 0:
        return jsonify({"output": result["stdout"]}), 200
    else:
        return jsonify({
            "error": result["stderr"] or "Execution failed.",
            "exit_code": result["exit_code"]
        }), 400


@app.route("/history", methods=["GET"])
def get_history():
    """Return last 10 executions."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    return jsonify(history), 200


# ---------- Run Server ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
