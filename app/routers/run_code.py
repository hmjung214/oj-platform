from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import uuid
import os

router = APIRouter()

CODE_DIR = os.path.abspath("./code_host")
os.makedirs(CODE_DIR, exist_ok=True)

class CodeRunRequest(BaseModel):
    code: str
    language: str = "python"  # 현재는 python만 지원

class CodeRunResponse(BaseModel):
    stdout: str
    stderr: str

@router.post("/run", response_model=CodeRunResponse)
def run_code(data: CodeRunRequest):
    if data.language != "python":
        raise HTTPException(status_code=400, detail="지원되지 않는 언어입니다.")

    unique_name = f"{uuid.uuid4().hex}.py"
    host_path = os.path.join(CODE_DIR, unique_name)

    try:
        with open(host_path, "w") as f:
            f.write(data.code)

        print(f"코드 저장 위치: {host_path}")

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{CODE_DIR}:/code_host",
                "python:3.10", "python", f"/code_host/{unique_name}"
            ],
            capture_output=True,
            timeout=5
        )

        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")

        return CodeRunResponse(stdout=stdout, stderr=stderr)

    except subprocess.TimeoutExpired:
        return CodeRunResponse(stdout="", stderr="⏱️ 실행 시간 초과")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(host_path):
            os.remove(host_path)
