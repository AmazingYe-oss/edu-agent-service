# app/services/nodes/explainer.py
from app.services.state import AgentState
from app.core.llm import get_chat_model
from app.tools.rag import search_knowledge_base
from app.tools.database import check_error_book_tool
from langgraph.prebuilt import create_react_agent as create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

async def explainer_node(state: AgentState, config: RunnableConfig) -> dict:
    print("[Explainer Agent] 特级辅导老师开始全副武装，准备为学生答疑解惑...")
    
    user_msg = state.get("user_message", "")
    current_kp = state.get("current_knowledge_point", "当前知识点")
    score_report = state.get("draft_response", "") # 上一步 Scorer 留下的批改分析

    system_prompt = f"""你是一位极具耐心的特级辅导老师。学生现在做错题了或者陷入了认知盲区。
为了给他提供最权威、最个性化的讲解，你拥有两个神技，请根据需要自主调用：
1. `search_knowledge_base`：去权威教材库里查阅【{current_kp}】的核心精髓。
2. `check_error_book_tool`：去查一查他以前是不是也错过类似的题，看看他是不是惯犯。

请结合你查到的所有信息，给他写一段深入浅出的错误原因分析和正确解题思路。语气要鼓励、温暖！
"""

    llm = get_chat_model().with_config({"tags": ["stream_to_user"]})
    # 装备两件神兵
    tools = [search_knowledge_base, check_error_book_tool]
    
    react_agent = create_agent(model=llm, tools=tools)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"学生说：'{user_msg}'。裁判的批改意见是：'{score_report}'。请开始辅导。")
    ]
    
    result = await react_agent.ainvoke({"messages": messages}, config=config)
    explanation = result["messages"][-1].content
    
    print("[Explainer Agent] 深度辅导内容生成完毕！")
    return {"draft_response": explanation}
