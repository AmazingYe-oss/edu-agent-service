from app.services.state import AgentState
from app.core.llm import get_chat_model
from app.tools.rag import search_knowledge_base
from langgraph.prebuilt import create_react_agent as create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
async def learner_node(state: AgentState, config: RunnableConfig) -> dict:
    print(" [Learner Agent] 收到学习需求，开始自主思考是否需要查阅资料...")
    
    user_message = state.get("user_message", "")
    intent = state.get("user_intent", "")
    feedback = state.get("critic_feedback", "")
    
    system_prompt = """你是一位循循善诱的AI金牌私教。
你的任务是根据用户的需求，讲解知识点。
你有权力使用工具箱中的 `search_knowledge_base` 工具来查阅教材。
如果你搜不到内容，请自信地使用你的内在常识进行解答，不要崩溃或拒绝回答。
输出格式要求：直接输出讲解内容，排版清晰，语气亲切。
"""
    if feedback and not state.get("is_approved"):
        system_prompt += f"\n\n【教导主任的打回意见】：{feedback}\n请务必针对上述意见修改你的讲解！"

    llm = get_chat_model().with_config({"tags": ["stream_to_user"]})
    tools = [search_knowledge_base] 
    
    react_agent = create_agent(model=llm, tools=tools)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户的学习意图是：{intent}。\n\n用户的具体问题是：{user_message}\n\n请根据用户的问题进行讲解。")
    ]
    result = await react_agent.ainvoke({"messages": messages}, config=config)
    draft = result["messages"][-1].content
    
    print(f"[Learner Agent] 讲解草稿撰写完毕！(长度: {len(draft)})")
    
    return {"draft_response": draft}
