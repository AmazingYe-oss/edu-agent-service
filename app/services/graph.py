from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor
from typing import Dict, Any, Optional
import uuid

from app.services.state import GraphState
from app.services.nodes.planner import planner_node
from app.services.nodes.learner import learner_node
from app.services.tools.rag_search import rag_search_tool

def create_graph() -> Graph:
    """创建 LangGraph 图"""
    
    # 创建状态图
    workflow = StateGraph(GraphState)
    
    # 添加节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("learner", learner_node)
    
    # 添加工具节点
    workflow.add_node("rag_search", rag_search_tool)
    
    # 定义边
    def should_continue(state: GraphState) -> str:
        """决定下一步流向"""
        if state.error:
            return "end"
        if state.current_agent == "planner" and state.plan:
            return "learner"
        elif state.current_agent == "learner" and state.response:
            return "end"
        elif state.search_results:
            return "learner"
        return "end"
    
    # 添加条件边
    workflow.add_conditional_edges(
        "planner",
        should_continue,
        {
            "learner": "learner",
            "end": "__end__"
        }
    )
    
    workflow.add_conditional_edges(
        "learner",
        should_continue,
        {
            "rag_search": "rag_search",
            "end": "__end__"
        }
    )
    
    workflow.add_edge("rag_search", "learner")
    
    # 设置入口
    workflow.set_entry_point("planner")
    
    return workflow.compile()

# 创建图实例
graph = create_graph()

async def run_graph(user_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """运行图"""
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    # 初始化状态
    initial_state = GraphState(
        user_query=user_message,
        conversation_id=conversation_id,
        messages=[{"role": "user", "content": user_message}]
    )
    
    # 运行图
    final_state = await graph.ainvoke(initial_state)
    
    return {
        "response": final_state.response or "抱歉，我无法处理您的请求。",
        "conversation_id": final_state.conversation_id
    }
