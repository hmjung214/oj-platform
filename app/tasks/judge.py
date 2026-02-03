from celery import Celery
from app.database import SessionLocal
from app.models.submission import Submission
from app.models.problem import Problem
from sqlalchemy.orm import Session
import logging
import re

from app.utils.code_checker import detect_hardcoding
from app.utils.code_executor import execute_python_code

celery_app = Celery(
    "judge",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

logger = logging.getLogger(__name__)

def sanitize_traceback(tb: str) -> str:
    return re.sub(r'File ".*?code_host/[a-zA-Z0-9_]+\.py"', 'File "main.py"', tb)

@celery_app.task(name="app.tasks.judge.judge_submission")
def judge_submission(submission_id: int):
    logger.warning("judge_submission 실행됨! submission_id: %s", submission_id)
    db: Session = SessionLocal()

    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()

        input_data = problem.input_example.strip()
        expected_output = problem.output_example.strip()

        if detect_hardcoding(submission.code, expected_output):
            submission.result = "Rejected"
            submission.stdout = ""
            submission.stderr = "하드코딩(정답 리터럴 포함) 감지: 코드에 정답 직접 출력이 포함되어 있습니다."
            db.commit()
            return

        try:
            output = execute_python_code(submission.code, input_data)
            actual_output = output.strip()
            submission.stdout = output
            submission.stderr = ""
        except Exception as e:
            actual_output = f"Error: {str(e)}"
            submission.stdout = ""
            submission.stderr = str(e)

        submission.result = "Accepted" if actual_output == expected_output else "Wrong Answer"
        db.commit()

        logger.warning("expected_output: %s", expected_output)
        logger.warning("actual_output: %s", actual_output)

    except Exception as e:
        logger.error("judge_submission error: %s", str(e))
        db.rollback()
    finally:
        db.close()
