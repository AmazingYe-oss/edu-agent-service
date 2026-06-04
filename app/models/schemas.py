from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户的输入信息")
    session_id: Optional[str] = Field("default", description="会话ID，后续做多轮记忆时使用")
    user_id: Optional[str] = Field(None, description="用户ID，后续做用户个性化时使用")


class ChatResponse(BaseModel):
    response: str | None = Field(None, description="Agent的最终回复")
    intent: Optional[str] = Field(None, description="大模型识别出的用户意图")
    agent_used: Optional[str] = Field(None, description="最终处理该请求的Agent名称")


# 用户认证相关 Schemas
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    message: str = Field(..., description="响应消息")


# 会话相关 Schemas
class SessionCreate(BaseModel):
    title: Optional[str] = Field(None, description="会话标题，可选")


class SessionResponse(BaseModel):
    session_id: str = Field(..., description="会话ID")
    title: Optional[str] = Field(None, description="会话标题")
    created_at: str = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int = Field(..., description="消息ID")
    role: str = Field(..., description="角色：user 或 assistant")
    content: str = Field(..., description="消息内容")
    intent: Optional[str] = Field(None, description="识别的意图")
    created_at: str = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class SessionWithMessages(BaseModel):
    session: SessionResponse
    messages: list[MessageResponse] = Field(default_factory=list, description="会话消息列表")
