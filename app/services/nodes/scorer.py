# app/services/nodes/score.py
from app.services.state import AgentState
from app.core.llm import get_chat_model
from app.tools.rag import search_knowledge_base
from langgraph.prebuilt import create_react_agent as create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
async def scorer_node(state: AgentState, config: RunnableConfig) -> dict:
    print("[Scorer Agent] 裁判正在查阅权威教材，核对学生答案...")
    
    user_answer = state.get("user_message", "")
    current_kp = state.get("current_knowledge_point", "通用知识")
    
    system_prompt = f"""你是一位铁面无私的阅卷裁判。
用户的输入是他们对某道题的回答。你现在需要判定他们的回答是否正确。
为了防止你自己发生幻觉，你必须使用 `search_knowledge_base` 工具，检索关于【{current_kp}】的标准定义和权威答案。

核对完毕后，请返回以下两部分内容：
1. 是否正确（明确告知对错）
2. 简短的分步判定理由。
"""

    llm = get_chat_model().with_config({"tags": ["stream_to_user"]})
    tools = [search_knowledge_base] # 给裁判分发 RAG 教材库工具
    
    react_agent = create_agent(model=llm, tools=tools)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"学生的回答是：'{user_answer}'。请结合权威资料进行批改。")
    ]
    
    # 批改不需要传 user_id，所以这里不用特意传 config
    result = await react_agent.ainvoke({"messages": messages}, config=config)
    score_analysis = result["messages"][-1].content
    
    # 极其简易的启发式判断，用于告诉下游要不要落盘错题本
    # 只要AI回复里包含了“错”、“不正确”、“错误”，就判定为不通过
    is_approved = True
    if any(word in score_analysis for word in ["错", "不正确", "不完美", "误"]):
        is_approved = False
        
    print(f"[Scorer Agent] 批改完毕。判定结果 -> 【{'通过' if is_approved else '错误'}】")
    return {
        "draft_response": score_analysis,
        "is_approved": is_approved
    }
