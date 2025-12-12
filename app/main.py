import os
import json
import tempfile
import zipfile
from flask import Flask, request, jsonify, render_template
from executor import run_python_in_docker, run_js_in_docker, run_python_zip, run_js_zip

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

# Create history file if missing
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

print("Using history file:", HISTORY_FILE)

def save_history(entry):
    """ Save last 10 executions """
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    history.insert(0, entry)
    history = history[:10]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


@app.route("/")
def home():
    return "Safe Code Executor API is running!"


@app.route("/ui")
def ui():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()

    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field"}), 400

    code = data["code"]
    language = data.get("language", "python")

    # Length check
    if len(code) > 5000:
        return jsonify({"error": "Code too long. Max 5000 chars."}), 400

    if language == "python":
        result = run_python_in_docker(code)
    elif language == "javascript":
        result = run_js_in_docker(code)
    else:
        return jsonify({"error": "Unsupported language"}), 400

    # Save to history
    save_history({
        "language": language,
        "code": code[:120],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "exit_code": result.get("exit_code", 0),
        "time": ""
    })

    return jsonify(result)


@app.route("/history")
def history():
    with open(HISTORY_FILE, "r") as f:
        return jsonify(json.load(f))


# ------------------------------------------------------------
# ZIP EXECUTION SUPPORT
# ------------------------------------------------------------
@app.route("/run-zip", methods=["POST"])
def run_zip_project():
    if "file" not in request.files:
        return jsonify({"stderr": "No ZIP file uploaded", "stdout": ""}), 400

    file = request.files["file"]

    if not file.filename.endswith(".zip"):
        return jsonify({"stderr": "File must be a ZIP", "stdout": ""}), 400

    # Create temp folder
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "project.zip")
    file.save(zip_path)

    # Extract
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
    except:
        return jsonify({"stderr": "Invalid ZIP structure", "stdout": ""}), 400

    # Detect entry file
    entry_py = os.path.join(temp_dir, "main.py")
    entry_js = os.path.join(temp_dir, "index.js")

    if os.path.exists(entry_py):
        result = run_python_zip(temp_dir)
    elif os.path.exists(entry_js):
        result = run_js_zip(temp_dir)
    else:
        return jsonify({"stderr": "ZIP must contain main.py or index.js", "stdout": ""}), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
