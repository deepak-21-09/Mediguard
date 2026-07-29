from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from core.database import get_db
from core.auth import get_current_user_id
from memory.hindsight import get_memory
from agents.medagent import get_agent
from models.chat import ChatSession, ChatMessage, MessageRole
from api.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    memory = get_memory()
    agent = get_agent()

    # Get or create session
    session_id = data.session_id
    if session_id:
        sess_result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id, ChatSession.user_id == user_id
            )
        )
        session = sess_result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = ChatSession(user_id=user_id, title=data.message[:50])
        db.add(session)
        await db.flush()
        session_id = session.id

    # Load history
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .limit(20)  # last 20 messages for context
    )
    history = [
        {"role": m.role.value, "content": m.content}
        for m in history_result.scalars().all()
    ]

    # Run MedAgent
    reply = await agent.chat(
        user_id=user_id,
        message=data.message,
        history=history,
        db_session=db,
        memory=memory,
    )

    # Persist messages
    db.add(ChatMessage(session_id=session_id, role=MessageRole.USER, content=data.message))
    db.add(ChatMessage(session_id=session_id, role=MessageRole.ASSISTANT, content=reply))
    await db.commit()

    return ChatResponse(reply=reply, session_id=session_id)


@router.get("/sessions")
async def get_sessions(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {"id": s.id, "title": s.title, "created_at": s.created_at}
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatMessage)
        .join(ChatSession)
        .where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return [
        {"role": m.role.value, "content": m.content, "created_at": m.created_at}
        for m in messages
    ]
