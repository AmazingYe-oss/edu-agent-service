from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    定义 LangGraph 在各个节点(Agent)间流转的全局状态
    """
    messages: List[BaseMessage]
    
    next_agent: Optional[str]        
    user_intent: Optional[str]
    
    retrieved_context: Optional[str] 
    
    draft_response: Optional[str]    
    
    retry_count: int                 
    is_approved: bool                
