"""
会话管理 API - 创建会话、获取会话列表、获取会话详情
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.domain import Session as SessionModel, Message
from app.models.schemas import SessionCreate, SessionResponse, MessageResponse, SessionWithMessages

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse)
async def create_session(user_id: str, request: SessionCreate = None, db: Session = Depends(get_db)):
    """
    创建新会话
    
    - user_id: 用户ID（查询参数）
    - title: 会话标题（可选）
    """
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    title = request.title if request and request.title else "新对话"
    
    new_session = SessionModel(
        session_id=session_id,
        user_id=user_id,
        title=title
    )
    
    try:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return SessionResponse(
            session_id=new_session.session_id,
            title=new_session.title,
            created_at=str(new_session.created_at)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")


@router.get("/sessions", response_model=list[SessionResponse])
async def get_user_sessions(user_id: str, db: Session = Depends(get_db)):
    """
    获取用户的所有会话列表
    
    - user_id: 用户ID（查询参数）
    """
    sessions = db.query(SessionModel)\
        .filter(SessionModel.user_id == user_id)\
        .order_by(desc(SessionModel.created_at))\
        .all()
    
    return [
        SessionResponse(
            session_id=s.session_id,
            title=s.title,
            created_at=str(s.created_at)
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=SessionWithMessages)
async def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    """
    获取会话详情（包含消息历史）
    
    - session_id: 会话ID
    """
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    messages = db.query(Message)\
        .filter(Message.session_id == session_id)\
        .order_by(Message.created_at)\
        .all()
    
    return SessionWithMessages(
        session=SessionResponse(
            session_id=session.session_id,
            title=session.title,
            created_at=str(session.created_at)
        ),
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                intent=m.intent,
                created_at=str(m.created_at)
            )
            for m in messages
        ]
    )


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session_title(session_id: str, request: SessionCreate, db: Session = Depends(get_db)):
    """
    更新会话标题
    
    - session_id: 会话ID
    - title: 新标题
    """
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session.title = request.title
    db.commit()
    db.refresh(session)
    
    return SessionResponse(
        session_id=session.session_id,
        title=session.title,
        created_at=str(session.created_at)
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """
    删除会话（级联删除消息）
    
    - session_id: 会话ID
    """
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    try:
        db.delete(session)
        db.commit()
        return {"message": "会话已删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")
