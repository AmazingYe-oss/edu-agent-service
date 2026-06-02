from langgraph.graph import StateGraph, END
from app.services.state import AgentState
from app.services.nodes.planner import planner_node
from app.services.nodes.learner import learner_node
from app.services.nodes.quizzler import quizzler_node
from app.services.nodes.scorer import scorer_node     
from app.services.nodes.explainer import explainer_node

def route_from_planner(state: AgentState) -> str:
    """根据 Planner 的决策，决定 Graph 的下一跳"""
    next_agent = state.get("next_agent")
    
    # 完整的路由映射表
    if next_agent == "learn":
        return "learner_node"
    elif next_agent == "quiz":
        return "quizzler_node"
    elif next_agent == "score":
        return "scorer_node"      
    elif next_agent == "explain":
        return "explainer_node"   
    elif next_agent == "direct":
        return END  
    else:
        print(f"节点 [{next_agent}] 异常或未识别，直接结束")
        return END 

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("learner_node", learner_node)
    workflow.add_node("quizzler_node", quizzler_node)
    workflow.add_node("scorer_node", scorer_node)         
    workflow.add_node("explainer_node", explainer_node)   
    
    workflow.set_entry_point("planner")
    
    workflow.add_conditional_edges(
        "planner",
        route_from_planner,
        {
            "learner_node": "learner_node",
            "quizzler_node": "quizzler_node",
            "scorer_node": "scorer_node",           
            "explainer_node": "explainer_node",     
            END: END
        }
    )
    
    workflow.add_edge("learner_node", END)
    workflow.add_edge("quizzler_node", END)
    workflow.add_edge("scorer_node", END)           
    workflow.add_edge("explainer_node", END)     
    
    return workflow.compile()

edu_agent_app = build_graph()
