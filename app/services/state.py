from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SearchDocument(BaseModel):
    """搜索文档"""
    content: str
    source: Optional[str] = None
    score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

class GraphState(BaseModel):
    """LangGraph 图状态定义"""
    messages: List[Dict[str, str]] = Field(default_factory=list, description="对话历史")
    user_query: str = Field(default="", description="当前用户查询")
    current_agent: str = Field(default="planner", description="当前活跃的代理")
    plan: Optional[str] = Field(default=None, description="执行计划")
    search_results: List[SearchDocument] = Field(default_factory=list, description="搜索结果")
    response: Optional[str] = Field(default=None, description="最终响应")
    conversation_id: Optional[str] = Field(default=None, description="对话ID")
    error: Optional[str] = Field(default=None, description="错误信息")
