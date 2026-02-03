from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import (
    problem, submission, auth, run_code, feedback,
    board, auth_admin, auth_user
)

app = FastAPI()

allowed_origins = list(set([
    "https://miso.center",
    "https://dev.miso.center",
    "https://devadmin.miso.center",
    "https://www.miso.center",
    "https://www.dev.miso.center",
    "https://www.devadmin.miso.center"
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 실제 등록 라우터
app.include_router(problem.router, prefix="/api")
app.include_router(submission.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(run_code.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(board.router, prefix="/api")
app.include_router(auth_admin.router)
app.include_router(auth_user.router)

@app.get("/")
def read_root():
    return {"message": "Online Judge API"}
