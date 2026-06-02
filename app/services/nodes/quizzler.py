# app/services/nodes/quizzler.py
from app.services.state import AgentState
from app.core.llm import get_chat_model
from app.tools.database import check_error_book_tool
from langgraph.prebuilt import create_react_agent as create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

def quizzler_node(state: AgentState, config: RunnableConfig) -> dict:
    print("📝 [Quizzler Agent] 考官正在翻阅学生错题本，准备量身定制题目...")
    
    # 尝试从历史中或者上下文获取当前的知识点，如果没有就基于常识出题
    current_kp = state.get("current_knowledge_point", "通用常识")
    
    system_prompt = f"""你是一位擅长“举一反三”的明星出题官。
你的任务是出一道高质量的选择题。
为了实现精准教学，你必须调用 `check_error_book_tool` 技能，去查一下学生近期在【{current_kp}】这个知识点上犯过什么错误。
- 如果有错题记录：请根据他上次错的原因，出一道“换汤不换药”的相似题，帮他攻克盲区！
- 如果没有记录：请直接出一道该知识点的基础测试题。

格式要求：给出题目情景、选项A B C D。不要直接给答案！
"""

    llm = get_chat_model()
    tools = [check_error_book_tool]
    
    react_agent = create_agent(model=llm, tools=tools)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"请针对知识点【{current_kp}】出一道考题。")
    ]
    
    result = react_agent.invoke({"messages": messages}, config=config)
    quiz_content = result["messages"][-1].content
    
    print("📝 [Quizzler Agent] 随堂测试题出好了！")
    return {"draft_response": quiz_content}
