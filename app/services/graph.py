from langgraph.graph import StateGraph, END
from app.services.state import AgentState
from app.services.nodes.planner import planner_node
from app.services.nodes.learner import learner_node
from app.services.nodes.quizzler import quizzler_node
from app.services.nodes.scorer import scorer_node
from app.services.nodes.explainer import explainer_node
from app.services.nodes.critic import critic_node 

def route_from_planner(state: AgentState) -> str:
    next_agent = state.get("next_agent")
    mapping = {
        "learn": "learner_node",
        "quiz": "quizzler_node",
        "score": "scorer_node",
        "explain": "explainer_node",
        "direct": END
    }
    return mapping.get(next_agent, END)

def route_from_critic(state: AgentState) -> str:
    """核心循环逻辑：根据审查结果决定是结束，还是打回"""
    is_approved = state.get("is_approved", False)
    retry_count = state.get("retry_count", 0)
    MAX_RETRIES = 2  
    
    if is_approved:
        return END
    elif retry_count >= MAX_RETRIES:
        print(f"🚨 达到最大重试次数({MAX_RETRIES})，强制输出当前草稿！")
        return END
    else:
        next_agent = state.get("next_agent")
        mapping = {
            "learn": "learner_node",
            "quiz": "quizzler_node",
            "score": "scorer_node",
            "explain": "explainer_node"
        }
        return mapping.get(next_agent, END)

def build_graph():
    workflow = StateGraph(AgentState)
    
    # 注册节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("learner_node", learner_node)
    workflow.add_node("quizzler_node", quizzler_node)
    workflow.add_node("scorer_node", scorer_node)
    workflow.add_node("explainer_node", explainer_node)
    workflow.add_node("critic_node", critic_node) # 🌟 注册审查节点
    
    workflow.set_entry_point("planner")
    
    workflow.add_conditional_edges("planner", route_from_planner)
    
    workflow.add_edge("learner_node", "critic_node")
    workflow.add_edge("quizzler_node", "critic_node")
    workflow.add_edge("scorer_node", "critic_node")
    workflow.add_edge("explainer_node", "critic_node")
    
    workflow.add_conditional_edges("critic_node", route_from_critic)
    
    return workflow.compile()

edu_agent_app = build_graph()
