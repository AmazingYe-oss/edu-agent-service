from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.state import GraphState
from app.core.config import settings

PLANNER_SYSTEM_PROMPT = """你是一个教育规划助手。你的任务是分析学生的问题，制定一个清晰的学习计划。

请按照以下步骤：
1. 理解学生的具体需求
2. 将复杂问题分解为可管理的小步骤
3. 确定需要查找的知识点
4. 制定学习路径

输出格式：
- 问题分析：...
- 学习计划：
  1. ...
  2. ...
  3. ...
- 需要搜索的知识点：...
"""

async def planner_node(state: GraphState) -> Dict[str, Any]:
    """规划节点 - 分析用户查询并制定计划"""
    try:
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        
        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=state.user_query)
        ]
        
        response = await llm.ainvoke(messages)
        
        return {
            "plan": response.content,
            "current_agent": "planner",
            "messages": state.messages + [
                {"role": "assistant", "content": response.content, "agent": "planner"}
            ]
        }
    except Exception as e:
        return {
            "error": f"规划节点错误: {str(e)}",
            "current_agent": "planner"
        }
