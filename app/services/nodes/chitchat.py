# app/services/nodes/chitchat.py
"""闲聊节点 - 通用对话，支持记忆访问和联网搜索"""

from app.services.state import AgentState
from app.core.llm import get_chat_model
from app.core.dashclient import search_long_term_memory
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig


async def chitchat_node(state: AgentState, config: RunnableConfig) -> dict:
    """通用闲聊节点，直接输出，不经过 critic 和 summarizer"""
    print("[Chitchat Agent] 进入闲聊模式，正在检索记忆...")
    
    user_message = state.get("user_message", "")
    user_id = state.get("user_id", "")
    history = state.get("history", [])
    
    # 检索长时记忆
    long_term_memory = ""
    if user_id:
        try:
            long_term_memory = search_long_term_memory(user_id, user_message)
            if long_term_memory:
                print(f"[Chitchat Agent] 检索到 {len(long_term_memory)} 字的长时记忆")
        except Exception as e:
            print(f"[Chitchat Agent] 长时记忆检索失败: {e}")
    
    system_prompt = f"""你是一个友好、智能的 AI 助手。你可以和用户进行自然的闲聊对话。

【你的特点】
- 语气亲切、自然，像朋友一样交流
- 记住用户之前告诉你的信息
- 可以聊任何话题，不限于学习

【记忆信息】
长期记忆：{long_term_memory if long_term_memory else "暂无"}

【近期对话】
{str(history[-5:]) if history else "这是对话开始"}

请用自然、友好的语气回复用户。"""
    
    # 直接调用 LLM，使用 final_output tag 以便前端捕获输出
    llm = get_chat_model().with_config({"tags": ["final_output"]})
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    result = await llm.ainvoke(messages, config=config)
    response = result.content
    
    print(f"[Chitchat Agent] 闲聊回复生成完毕！(长度: {len(response)})")
    
    # 直接返回，不经过 critic 和 summarizer
    return {"draft_response": response}
