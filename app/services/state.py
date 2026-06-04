from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    定义 LangGraph 在各个节点(Agent)间流转的全局状态
    """
    user_message: Optional[str]      # 用户原始消息
    messages: List[BaseMessage]
    next_agent: Optional[str]        
    user_intent: Optional[str]      
    current_knowledge_point: Optional[str]  # 当前知识点
    retrieved_context: Optional[str] 
    draft_response: Optional[str]   
    retry_count: int                
    is_approved: bool                
    critic_feedback: Optional[str]   
