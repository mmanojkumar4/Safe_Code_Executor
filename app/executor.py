import subprocess
import os
import tempfile
import shutil

def run_code_in_docker(language, code):
    

    #  Create temp directory + code file
    temp_dir = tempfile.mkdtemp()

    if language == "python":
        filename = "script.py"
        image = "python:3.11-slim"
        run_cmd = ["python", f"/app/{filename}"]

    elif language in ["javascript", "js"]:
        filename = "script.js"
        image = "node:18-slim"
        run_cmd = ["node", f"/app/{filename}"]

    else:
        return {
            "stdout": "",
            "stderr": "Unsupported language",
            "exit_code": -1
        }

    script_path = os.path.join(temp_dir, filename)

    # Write user code to file
    with open(script_path, "w") as f:
        f.write(code)

    #  Docker run command with full sandboxing
    command = [
        "docker", "run", "--rm",

        # Security limits
        "--memory=128m",
        "--memory-swap=128m",
        "--network", "none",
        "--read-only",

        # Mount script file (read-only)
        "-v", f"{script_path}:/app/{filename}:ro",

        image
    ] + run_cmd

    try:
        #  Execute inside Docker with timeout
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
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

    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Internal error: {str(e)}",
            "exit_code": -1
        }

    finally:
        # Cleanup temporary directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
