from langgraph.graph import StateGraph, END
from app.services.state import AgentState
from app.services.nodes.planner import planner_node
from app.services.nodes.learner import learner_node
from app.services.nodes.quizzler import quizzler_node
from app.services.nodes.scorer import scorer_node
from app.services.nodes.explainer import explainer_node
from app.services.nodes.critic import critic_node
from app.services.nodes.summarizer import summarizer_node
from app.services.nodes.chitchat import chitchat_node
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from app.core.config import settings

# 全局 graph 实例
edu_agent_app = None

def route_from_planner(state: AgentState) -> str:
    next_agent = state.get("next_agent")
    mapping = {
        "learn": "learner_node",
        "quiz": "quizzler_node",
        "score": "scorer_node",
        "explain": "explainer_node",
        "chitchat": "chitchat_node",
        "direct": END
    }
    return mapping.get(next_agent, END)

def route_from_critic(state: AgentState) -> str:
    """核心逻辑：根据审查结果决定是打回重做，还是送去总结"""
    is_approved = state.get("is_approved", False)
    retry_count = state.get("retry_count", 0)
    MAX_RETRIES = 2  
    
    if is_approved:
        # 通过审查 -> 送去总结节点
        return "summarizer_node"
    elif retry_count >= MAX_RETRIES:
        print(f"[Critic] 达到最大重试次数({MAX_RETRIES})，强制送去总结！")
        return "summarizer_node"
    else:
        # 未通过 -> 打回重做
        next_agent = state.get("next_agent")
        mapping = {
            "learn": "learner_node",
            "quiz": "quizzler_node",
            "score": "scorer_node",
            "explain": "explainer_node"
        }
        return mapping.get(next_agent, END)

def build_graph(checkpointer=None):
    workflow = StateGraph(AgentState)
    
    # 注册节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("learner_node", learner_node)
    workflow.add_node("quizzler_node", quizzler_node)
    workflow.add_node("scorer_node", scorer_node)
    workflow.add_node("explainer_node", explainer_node)
    workflow.add_node("critic_node", critic_node)
    workflow.add_node("summarizer_node", summarizer_node)
    workflow.add_node("chitchat_node", chitchat_node)  # 新增：闲聊节点
    
    workflow.set_entry_point("planner")
    
    workflow.add_conditional_edges("planner", route_from_planner)
    
    # 教学节点 -> critic 审查
    workflow.add_edge("learner_node", "critic_node")
    workflow.add_edge("quizzler_node", "critic_node")
    workflow.add_edge("scorer_node", "critic_node")
    workflow.add_edge("explainer_node", "critic_node")
    
    workflow.add_conditional_edges("critic_node", route_from_critic)
    
    # 闲聊节点直接输出，不经过 critic 和 summarizer
    workflow.add_edge("chitchat_node", END)
    
    # 总结节点 -> END
    workflow.add_edge("summarizer_node", END)
    
    # 编译时传入 checkpointer（如果有的话）
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()

async def init_graph():
    """异步初始化 graph 和 checkpointer"""
    global edu_agent_app
    
    # 创建连接池（设置 autocommit=True 以支持 CREATE INDEX CONCURRENTLY）
    pool = AsyncConnectionPool(
        conninfo=settings.POSTGRES_URL,
        min_size=1,
        max_size=10,
        kwargs={"autocommit": True}
    )
    await pool.open()
    print("[Graph] PostgreSQL 连接池创建完成")
    
    # 创建 AsyncPostgresSaver 并初始化表
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()
    print("[Graph] AsyncPostgresSaver 初始化完成，已创建 checkpoint 表")
    
    # 编译 graph
    edu_agent_app = build_graph(checkpointer)
    print("[Graph] LangGraph 编译完成，已绑定 PostgreSQL checkpointer")
