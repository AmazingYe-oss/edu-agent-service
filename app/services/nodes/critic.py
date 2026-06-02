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
    
    system_prompt = """你是一位严苛的教导主任。你的任务是审查其他老师(Agent)生成的【草稿内容】。
请根据以下标准进行审查：
1. 准确性：草稿内容是否严格基于【参考资料】？有没有瞎编乱造？
2. 教育性：语气是否适合学生？如果是出题，是否直接泄露了答案？
3. 完整性：内容是否有头有尾，排版是否清晰？

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
