from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.board import Board
from app.models.post import Post
from app.schemas.board import BoardCreate, BoardOut, BoardUpdate
from app.schemas.post import PostCreate, PostOut
from app.core.auth import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/boards", tags=["Board"])

# 관리자 인증
async def get_admin_user(user=Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")
    return user

# Board 가져오는 공통 헬퍼
async def get_board_obj(board_id: str, db: AsyncSession) -> Board:
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="게시판을 찾을 수 없습니다.")
    return board

# fsboard 권한 계층 반전
def convert_level(fsboard_level: int) -> int:
    return 11 - fsboard_level

async def check_board_permission(board: Board, user: dict, permission: str):
    required_level = convert_level(getattr(board, f"{permission}_level"))
    user_level = convert_level(user.get("level", 10))  # 비회원 기본 10
    if user_level < required_level:
        raise HTTPException(status_code=403, detail=f"{permission} 권한 없음")

# ------------------------ #

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_board(
    data: BoardCreate,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Board).where(Board.name == data.name))
    if result.scalar():
        raise HTTPException(status_code=400, detail="이미 존재하는 게시판 이름입니다.")

    payload = data.dict()
    if not payload["category"]:
        payload["category"] = None

    board = Board(id=str(uuid.uuid4()), **payload)
    db.add(board)
    await db.commit()
    await db.refresh(board)

    return {"message": f"{board.id} 게시판 생성 완료", "board_id": board.id}

@router.get("/{board_id}", response_model=BoardOut, summary="게시판 단건 조회 (관리자 전용)")
async def get_board(
    board_id: str,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    board = await get_board_obj(board_id, db)
    return board

@router.patch("/{board_id}", summary="게시판 수정 (관리자 전용)")
async def update_board(
    board_id: str,
    data: BoardUpdate,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    board = await get_board_obj(board_id, db)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(board, key, value)

    await db.commit()
    await db.refresh(board)

    return {"message": f"{board_id} 게시판 수정 완료"}

@router.get("/", response_model=List[BoardOut], summary="게시판 목록 조회")
async def get_board_list(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Board).order_by(Board.created_at.desc()))
    boards = result.scalars().all()

    return [
        BoardOut(
            id=b.id,
            name=b.name,
            category=b.category,
            list_level=b.list_level,
            view_level=b.view_level,
            write_level=b.write_level,
            reply_level=b.reply_level,
            comment_level=b.comment_level,
            link_level=b.link_level,
            upload_level=b.upload_level,
            download_level=b.download_level,
            html_level=b.html_level,
            use_secret=b.use_secret,
            use_dhtml=b.use_dhtml,
            upload_count=b.upload_count,
            upload_size=b.upload_size,
            created_at=b.created_at or datetime.utcnow()
        )
        for b in boards
    ]

@router.post("/{board_id}/posts", status_code=status.HTTP_201_CREATED, summary="게시글 작성")
async def create_post(
    board_id: str,
    data: PostCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    board = await get_board_obj(board_id, db)
    await check_board_permission(board, user, "write")

    new_post = Post(
        board_id=board_id,
        course_id=data.course_id,
        category=data.category,
        title=data.title,
        content=data.content,
        user_id=user["user_id"],
        username=user["username"]
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return {"message": "게시글이 등록되었습니다.", "post_id": new_post.id}

@router.get("/{board_id}/posts", response_model=List[PostOut], summary="게시글 목록")
async def list_posts(
    board_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    board = await get_board_obj(board_id, db)
    await check_board_permission(board, user, "list")

    result = await db.execute(
        select(Post).where(Post.board_id == board_id).order_by(Post.created_at.desc())
    )
    posts = result.scalars().all()
    return posts

@router.get("/{board_id}/posts/{post_id}", response_model=PostOut, summary="게시글 상세")
async def get_post(
    board_id: str,
    post_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    board = await get_board_obj(board_id, db)
    await check_board_permission(board, user, "view")

    result = await db.execute(
        select(Post).where(Post.board_id == board_id, Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post

@router.delete("/{board_id}", summary="게시판 삭제 (관리자 JWT + 내부키)")
async def delete_board(
    board_id: str,
    request: Request,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    if request.headers.get("X-Internal-Key") != settings.internal_key:
        raise HTTPException(status_code=403, detail="내부키 불일치")

    board = await get_board_obj(board_id, db)
    await db.delete(board)
    await db.commit()
    return {"message": f"{board_id} 게시판 삭제 완료"}
