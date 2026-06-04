# app/services/nodes/summarizer.py
from app.services.state import AgentState
from app.core.llm import get_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

async def summarizer_node(state: AgentState, config: RunnableConfig) -> dict:
    print("[Summarizer Agent] 总结节点正在整合信息，生成最终回复...")
    
    user_message = state.get("user_message", "")
    intent = state.get("user_intent", "")
    knowledge_point = state.get("current_knowledge_point", "")
    draft_response = state.get("draft_response", "")
    critic_feedback = state.get("critic_feedback", "")
    is_approved = state.get("is_approved", False)
    
    system_prompt = f"""你是一位专业的学习助手。你的任务是整合其他AI助手的工作成果，生成最终的高质量回复。

【当前上下文】
- 用户意图：{intent}
- 知识点：{knowledge_point}
- 审查状态：{'通过' if is_approved else '需要修改'}

【你的任务】
1. 如果审查通过：对草稿进行润色，使其更加清晰、友好、易于理解
2. 如果审查未通过：根据审查反馈修改草稿，然后输出修改后的版本

【输出要求】
- 直接输出最终内容，不要包含任何元数据或JSON
- 排版清晰，语气亲切
- 保持专业性的同时易于理解"""

    llm = get_chat_model().with_config({"tags": ["final_output"]})
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户问题：{user_message}\n\nAI助手的草稿：\n{draft_response}\n\n审查反馈：{critic_feedback}")
    ]
    
    result = await llm.ainvoke(messages, config=config)
    final_response = result.content
    
    print(f"[Summarizer Agent] 最终回复生成完毕！(长度: {len(final_response)})")
    
    return {"draft_response": final_response}
