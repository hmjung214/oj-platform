import os
import subprocess
import uuid
import logging

logger = logging.getLogger(__name__)

HOST_CODE_DIR = "/tmp"
CONTAINER_CODE_DIR = "/code"

def execute_python_code(code: str, stdin_data: str = "") -> str:
    unique_name = f"{uuid.uuid4().hex}.py"
    host_path = os.path.join(HOST_CODE_DIR, unique_name)
    container_path = os.path.join(CONTAINER_CODE_DIR, unique_name)

    try:
        with open(host_path, "w") as f:
            f.write(code)

        result = subprocess.run(
            [
                "docker", "run", "--rm", "-i",
                "-v", f"{HOST_CODE_DIR}:{CONTAINER_CODE_DIR}", 
                "python:3.10",
                "python", container_path
            ],
            input=stdin_data,
            text=True,
            capture_output=True,
            timeout=5
        )
        output = result.stdout.strip()

    except subprocess.TimeoutExpired:
        output = "Timeout"
    except Exception as e:
        output = f"Error: {e}"
    finally:
        if os.path.exists(host_path):
            os.remove(host_path)

    return output
