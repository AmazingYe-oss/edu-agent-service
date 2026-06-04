from app.services.state import AgentState
from app.core.llm import get_chat_model
from app.tools.database import get_user_profile_tool, search_user_memory_tool
from langgraph.prebuilt import create_react_agent as create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

async def planner_node(state: AgentState, config: RunnableConfig) -> dict:
    print("[Planner Agent] 指挥官正在结合历史记忆与学生画像，分析用户意图...")
    
    user_message = state.get("user_message", "")
    history = state.get("history", [])

    system_prompt = """你是一个高智商的教学总监（Planner）。你的核心任务是分析用户的输入，并决定下一步路由给哪个教学节点。

【可调用的技能箱】
- 如果你对学生的背景、水平一无所知，请先调用 `get_user_profile_tool` 查阅学生画像。
- 如果用户提到了过去的事情、或者你觉得需要回顾历史，调用 `search_user_memory_tool`。

【意图路由规则】
分析完所有信息后，你必须在回复的最后一行，给出明确的路由标签：
- 用户想学习新知识、问“是什么” -> 输出：INTENT: learn
- 用户请求出题测试、或者你觉得他该做题了 -> 输出：INTENT: quiz
- 用户在回答上一道题（包含A/B/C/D或具体答案） -> 输出：INTENT: score
- 用户答错了题，在请求解析、或者对错题感到困惑 -> 输出：INTENT: explain
- 用户在闲聊、打招呼、问与学习无关的问题、或者想聊天 -> 输出：INTENT: chitchat

【知识点提取】
在路由标签之前，你必须输出：KP: <提取的知识点>
例如：KP: 微积分-导数
KP: 牛顿第一定律
如果用户在闲聊，可以输出：KP: 闲聊

【极端重要：输出格式】
你可以进行思考，但最终的决定必须是：
KP: 知识点名称
INTENT: 对应标签。
"""

    llm = get_chat_model()
    # 装备查画像和查长期记忆的武器
    tools = [get_user_profile_tool, search_user_memory_tool]
    
    react_agent = create_agent(model=llm, tools=tools)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"当前用户输入：'{user_message}'\n近期对话历史：{str(history[-3:])}")
    ]
    
    
    result = await react_agent.ainvoke({"messages": messages}, config=config)
    ai_thought = result["messages"][-1].content
    

    intent = "learn"  # 默认值
    if "INTENT: quiz" in ai_thought:
        intent = "quiz"
    elif "INTENT: score" in ai_thought:
        intent = "score"
    elif "INTENT: explain" in ai_thought:
        intent = "explain"
    elif "INTENT: chitchat" in ai_thought:
        intent = "chitchat"
    elif "INTENT: learn" in ai_thought:
        intent = "learn"
    
    # 提取知识点
    knowledge_point = "通用知识"
    if "KP:" in ai_thought:
        try:
            kp_line = [line for line in ai_thought.split("\n") if "KP:" in line][0]
            knowledge_point = kp_line.split("KP:")[1].strip()
        except:
            pass
        
    print(f"[Planner Agent] 意图分析完毕。决定路由给 -> 【{intent}】，知识点 -> 【{knowledge_point}】")
    return {
        "user_message": user_message,  # 传递用户原始消息
        "user_intent": intent,
        "current_knowledge_point": knowledge_point,  # 传递知识点
        "next_agent": intent  
    }
