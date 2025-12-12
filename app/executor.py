import subprocess
import tempfile
import os
import json


# ---------------------------------------------------
# Helper to run commands safely
# ---------------------------------------------------
def run_command_safe(cmd):
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10  # 10 second timeout
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out after 10 seconds.",
            "exit_code": -2
        }


# ---------------------------------------------------
# Run Python code inside Secure Docker
# ---------------------------------------------------
def run_python_in_docker(code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp.flush()

    cmd = [
        "docker", "run",
        "--rm",
        "--network", "none",
        "--read-only",
        "--memory=128m",
        "-v", f"{tmp.name}:/app/script.py:ro",
        "python:3.11-slim",
        "python", "/app/script.py"
    ]

    return run_command_safe(cmd)


# ---------------------------------------------------
# Run JavaScript code inside Secure Docker
# ---------------------------------------------------
def run_js_in_docker(code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as tmp:
        tmp.write(code.encode())
        tmp.flush()

    cmd = [
        "docker", "run",
        "--rm",
        "--network", "none",
        "--read-only",
        "--memory=128m",
        "-v", f"{tmp.name}:/app/script.js:ro",
        "node:18-slim",
        "node", "/app/script.js"
    ]

    return run_command_safe(cmd)


# ---------------------------------------------------
# Run Python ZIP project
# ---------------------------------------------------
def run_python_zip(folder_path):
    cmd = [
        "docker", "run",
        "--rm",
        "--network", "none",
        "--read-only",
        "--memory=256m",
        "-v", f"{folder_path}:/app:ro",
        "python:3.11-slim",
        "python", "/app/main.py"
    ]
    return run_command_safe(cmd)


# ---------------------------------------------------
# Run JavaScript ZIP project
# ---------------------------------------------------
def run_js_zip(folder_path):
    cmd = [
        "docker", "run",
        "--rm",
        "--network", "none",
        "--read-only",
        "--memory=256m",
        "-v", f"{folder_path}:/app:ro",
        "node:18-slim",
        "node", "/app/index.js"
    ]
    return run_command_safe(cmd)
