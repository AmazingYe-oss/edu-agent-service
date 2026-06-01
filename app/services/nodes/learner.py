from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.state import GraphState
from app.core.config import settings

LEARNER_SYSTEM_PROMPT = """你是一个专业的教育辅导助手。基于提供的学习计划和搜索结果，为学生提供详细、易懂的解答。

请遵循以下原则：
1. 使用清晰、简洁的语言
2. 提供具体的例子
3. 将复杂概念分解为简单步骤
4. 鼓励学生并提供学习建议

如果提供了搜索结果，请基于这些信息回答问题。
"""

async def learner_node(state: GraphState) -> Dict[str, Any]:
    """学习节点 - 根据计划和搜索结果生成最终响应"""
    try:
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        
        # 构建上下文
        context = state.plan or ""
        if state.search_results:
            context += "\n\n搜索结果:\n"
            for i, doc in enumerate(state.search_results, 1):
                context += f"{i}. {doc.content}\n   来源: {doc.source or '未知'}\n"
        
        messages = [
            SystemMessage(content=LEARNER_SYSTEM_PROMPT),
            HumanMessage(content=f"用户问题: {state.user_query}\n\n计划和上下文:\n{context}")
        ]
        
        response = await llm.ainvoke(messages)
        
        return {
            "response": response.content,
            "current_agent": "learner",
            "messages": state.messages + [
                {"role": "assistant", "content": response.content, "agent": "learner"}
            ]
        }
    except Exception as e:
        return {
            "error": f"学习节点错误: {str(e)}",
            "current_agent": "learner"
        }
