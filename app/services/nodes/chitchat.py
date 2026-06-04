# app/services/nodes/chitchat.py
"""闲聊节点 - 通用对话，支持记忆访问和联网搜索"""

from app.services.state import AgentState
from app.core.llm import get_chat_model
from app.core.dashclient import search_long_term_memory
from app.tools.web_search import web_search
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig


async def chitchat_node(state: AgentState, config: RunnableConfig) -> dict:
    """通用闲聊节点，直接输出，不经过 critic 和 summarizer"""
    print("[Chitchat Agent] 进入闲聊模式，正在检索记忆...")
    
    user_message = state.get("user_message", "")
    user_id = state.get("user_id", "")
    messages = state.get("messages", [])
    
    print(f"[Chitchat Agent] 当前 messages 数量: {len(messages)}")
    
    # 检索长时记忆
    long_term_memory = ""
    if user_id:
        try:
            print(f"[Chitchat Agent] 开始检索长时记忆，user_id={user_id}, query={user_message}")
            long_term_memory = search_long_term_memory(user_id, user_message)
            if long_term_memory:
                print(f"[Chitchat Agent] 检索到长时记忆: {long_term_memory[:100]}")
            else:
                print(f"[Chitchat Agent] 未检索到长时记忆")
        except Exception as e:
            print(f"[Chitchat Agent] 长时记忆检索异常: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"[Chitchat Agent] 无 user_id，跳过长时记忆检索")
    
    # 判断是否需要联网搜索
    search_keywords = ["天气", "新闻", "最新", "今天", "现在", "实时", "价格", "股票", "比赛"]
    need_search = any(keyword in user_message for keyword in search_keywords)
    print(f"[Chitchat Agent] 用户消息: {user_message}, need_search: {need_search}")
    
    search_result = ""
    if need_search:
        print(f"[Chitchat Agent] 检测到需要联网搜索")
        try:
            search_result = web_search.invoke({"query": user_message})
            print(f"[Chitchat Agent] 搜索完成，结果: {search_result[:200] if search_result else '空'}")
        except Exception as e:
            print(f"[Chitchat Agent] 联网搜索失败: {e}")
    
    # 构建对话历史字符串
    history_str = ""
    if messages:
        history_str = "\n".join([f"{'用户' if isinstance(msg, HumanMessage) else 'AI'}: {msg.content}" for msg in messages[-5:]])
    
    system_prompt = f"""你是一个友好、智能的 AI 助手。你可以和用户进行自然的闲聊对话。

【你的特点】
- 语气亲切、自然，像朋友一样交流
- 记住用户之前告诉你的信息
- 可以聊任何话题，不限于学习
- 如果用户问到需要联网搜索的问题（如天气、新闻等），请使用搜索结果回答

【记忆信息】
长期记忆：{long_term_memory if long_term_memory else "暂无"}

【联网搜索结果】
{search_result if search_result else "无需搜索或搜索未返回结果"}

【近期对话】
{history_str if history_str else "这是对话开始"}

请用自然、友好的语气回复用户。"""
    
    # 直接调用 LLM
    llm = get_chat_model().with_config({"tags": ["final_output"]})
    
    llm_messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    result = await llm.ainvoke(llm_messages, config=config)
    response = result.content
    
    print(f"[Chitchat Agent] 闲聊回复生成完毕！(长度: {len(response)})")
    
    # 关键：更新 messages 字段，让 checkpointer 保存对话历史
    new_messages = messages + [HumanMessage(content=user_message), AIMessage(content=response)]
    
    return {
        "draft_response": response,
        "messages": new_messages  # 更新消息历史
    }
