from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    """对话请求模型"""
    message: str = Field(..., description="用户消息")
    conversation_id: Optional[str] = Field(None, description="对话ID，用于多轮对话")

class ChatResponse(BaseModel):
    """对话响应模型"""
    response: str = Field(..., description="代理响应")
    conversation_id: Optional[str] = Field(None, description="对话ID")

class RAGSearchResult(BaseModel):
    """RAG搜索结果"""
    content: str
    source: Optional[str] = None
    score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

class AgentState(BaseModel):
    """LangGraph 状态定义"""
    messages: List[Dict[str, str]] = []
    current_agent: str = "planner"
    user_query: str = ""
    plan: Optional[str] = None
    search_results: List[RAGSearchResult] = []
    response: Optional[str] = None
    conversation_id: Optional[str] = None
