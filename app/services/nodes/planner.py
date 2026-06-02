from typing import Literal, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.services.state import AgentState
from app.core.llm import get_llm

class RouteDecision(BaseModel):
    """大模型分析用户意图后输出的路由决策"""
    user_intent: str = Field(description="用一句话总结用户的真实意图和诉求")
    next_agent: Literal["learn", "quiz", "score", "explain", "direct"] = Field(
        description="""决定下一步交给哪个Agent处理：
        - learn: 用户想学习新知识、概念讲解。
        - quiz: 用户要求出几道题、小测验。
        - score: 用户提交了答案，要求批改打分。
        - explain: 用户针对做错的题要求辅导和解答。
        - direct: 用户的输入只是简单的问候(如你好)或无关闲聊，可以直接回复。
        """
    )
    direct_response: Optional[str] = Field(default=None, description="如果 next_agent 是 'direct'，请在这里直接给出回复内容，否则留空")

def planner_node(state: AgentState) -> dict:
    """计划 Agent 的节点执行函数"""
    print("🧠 [Planner Agent] 正在分析用户意图...")
    parser = PydanticOutputParser(pydantic_object=RouteDecision)
    system_prompt = """你是一个智能教育系统的'主控路由枢纽'。
你的任务是阅读用户的输入，分析其意图，并将任务分发给最合适的专职教师(Agent)。
仔细思考用户需要的是新知识讲解、出题、批改还是错题辅导。

请严格按照以下指定的格式返回结果：
{format_instructions}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]).partial(format_instructions=parser.get_format_instructions())
    
    llm = get_llm()

    chain = prompt | llm | parser
    
    decision: RouteDecision = chain.invoke({"messages": state["messages"]})
    
    print(f"🎯 [Planner Agent] 决策结果: 交给 [{decision.next_agent}] 处理. 意图: {decision.user_intent}")
    
    return {
        "next_agent": decision.next_agent,
        "user_intent": decision.user_intent,
        "draft_response": decision.direct_response
    }