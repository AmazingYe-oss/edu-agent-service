from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.services.state import AgentState
from app.core.llm import get_llm

class CriticDecision(BaseModel):
    is_approved: bool = Field(description="审查是否通过。如果满足所有要求，返回 true；否则返回 false。")
    feedback: str = Field(description="如果未通过，给出严厉且具体的修改意见；如果通过，可以写'同意发布'。")

def critic_node(state: AgentState) -> dict:
    print("[Critic Agent] 教导主任开始审查内容质量...")
    
    draft = state.get("draft_response", "")
    context = state.get("retrieved_context", "")
    current_retry = state.get("retry_count", 0)
    
    system_prompt = """你是一位严苛的教导主任。你的任务是审查【草稿内容】。

【⚠️ 极其重要的格式要求】
你必须且只能返回纯 JSON 对象，不允许有任何额外的废话！
JSON 的 Key 必须严格是英文：
1. "is_approved": true 或者 false
2. "feedback": 你的审查意见（字符串）

绝对不能使用 "审查结果" 等中文作为 Key！

请给出审查结果。如果未通过，请明确指出哪里需要修改。

【参考资料】
{context}

【草稿内容】
{draft}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(CriticDecision)
    chain = prompt | structured_llm
    
    decision: CriticDecision = chain.invoke({
        "context": context,
        "draft": draft
    })
    
    new_retry_count = current_retry + 1
    
    if decision.is_approved:
        print("[Critic Agent] 审查通过！准备发送给用户。")
    else:
        print(f"[Critic Agent] 审查未通过！打回重做。意见: {decision.feedback} (当前重试次数: {new_retry_count})")
    
    # 更新全局状态
    return {
        "is_approved": decision.is_approved,
        "critic_feedback": decision.feedback,
        "retry_count": new_retry_count
    }
