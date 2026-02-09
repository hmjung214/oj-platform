from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from fastapi.responses import StreamingResponse
from app.core.config import settings
import os

router = APIRouter()
client = OpenAI(api_key=settings.openai_api_key)

class FeedbackItem(BaseModel):
    text: str
    comment: str

class FeedbackRequest(BaseModel):
    items: List[FeedbackItem]
    description: str
    manual_comment: str

@router.post("/generate-feedback")
async def generate_feedback(data: FeedbackRequest):
    system_prompt = (
        "너는 학습자의 작업 결과에 대해 분석적이고 기술적인 피드백을 작성하는 교강사이다. "
        "다음 규칙을 따른다:\n"
        "1. 각 문장은 약 30~50단어의 복합문으로 구성\n"
        "2. 구현 방식, 설계 원리, 기능 구조 또는 개선 가능성 중 최소 2가지 이상 포함\n"
        "3. '~좋았어요', '~편했어요', '~같아요' 등 감정적 표현 적극사용\n"
        "4. 문장 앞에 기호 (-, *, 숫자 등) 붙이지 않음\n"
        "5. 각 문장은 줄바꿈(\\n)으로 구분\n"
        "6. 잘한부분에 대한 긍정적 평가 및 응원하는 어조 사용\n"
        "7. 전체 내용은 300자 이내로 작성"
    )

    item_prompts = "\n".join(
        f"[피드백 항목]: {item.text}\n[교강사 코멘트]: {item.comment}" for item in data.items
    )

    user_prompt = (
        f"과제 설명:\n{data.description.strip()}\n\n"
        f"개별 항목 평가:\n{item_prompts}\n\n"
        f"교강사의 전체 첨언:\n{data.manual_comment.strip()}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    def stream_generator():
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.4,
                max_tokens=300,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            yield f"[AI 피드백 생성 중 오류 발생: {str(e)}]"

    return StreamingResponse(stream_generator(), media_type="text/html")
