from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB 
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    knowledge_state = Column(JSONB, server_default='{}')  # 存放知识点掌握度
    learning_style = Column(String(50), server_default='unknown')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ErrorBook(Base):
    __tablename__ = "error_books"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    session_id = Column(String(50), ForeignKey("sessions.session_id", ondelete="SET NULL"))
    knowledge_point = Column(String(100), nullable=False, index=True)
    question_content = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.session_id", ondelete="CASCADE"), index=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    role = Column(String(20), nullable=False)  # 'user' 或 'assistant'
    content = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)  # 识别的意图
    created_at = Column(DateTime(timezone=True), server_default=func.now())
