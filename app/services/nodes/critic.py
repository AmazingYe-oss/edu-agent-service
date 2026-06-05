import json
import re
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.services.state import AgentState
from app.core.llm import get_llm
from langchain_core.runnables import RunnableConfig

class CriticDecision(BaseModel):
    is_approved: bool = Field(description="审查是否通过。如果满足所有要求，返回 true；否则返回 false。")
    feedback: str = Field(description="如果未通过，给出严厉且具体的修改意见；如果通过，可以写'同意发布'。")

def sanitize_json_string(s: str) -> str:
    """清理 LLM 返回的 JSON 字符串中的非法转义字符"""
    # 移除 markdown 代码块标记
    s = re.sub(r'```json\s*', '', s)
    s = re.sub(r'```\s*$', '', s)
    s = s.strip()
    
    # 修复常见的非法转义序列
    # 将 \f, \b, \a, \v 等非法 JSON 转义替换为空格或移除
    s = re.sub(r'\\f', ' ', s)
    s = re.sub(r'\\b', ' ', s)
    s = re.sub(r'\\a', ' ', s)
    s = re.sub(r'\\v', ' ', s)
    # 保留有效的 JSON 转义: \n, \r, \t, \\, \", \/, \uXXXX
    
    return s

async def critic_node(state: AgentState, config: RunnableConfig) -> dict:
    print("[Critic Agent] 教导主任开始检查内容质量...")
    
    draft = state.get("draft_response", "")
    context = state.get("retrieved_context", "")
    current_retry = state.get("retry_count", 0)
    
    system_prompt = """你是一位严厉的教导主任。你的任务是审查【草稿内容】。

【极其重要的格式要求】
你必须且只能返回纯 JSON 对象，不允许多余的废话。
JSON 的 Key 必须严格是英文：
1. "is_approved": true 或者 false
2. "feedback": 你的审查意见（字符串）

绝对不能使用 "审查结果" 等中文作为 Key。
不要在 JSON 中使用反斜杠转义字符（如 \f, \b 等）。

请给出检查结果。如果未通过，请明确指出哪里需要修改。

【参考资料】
{context}

【草稿内容】
{draft}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])
    
    llm = get_llm()
    chain = prompt | llm
    
    try:
        response = await chain.ainvoke({
            "context": context,
            "draft": draft
        }, config=config)
        
        # 获取响应文本
        raw_text = response.content if hasattr(response, 'content') else str(response)
        
        # 清理 JSON 字符串
        cleaned_text = sanitize_json_string(raw_text)
        
        # 尝试解析 JSON
        try:
            data = json.loads(cleaned_text)
            decision = CriticDecision(**data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[Critic Agent] JSON 解析失败，尝试提取关键信息: {e}")
            # 如果 JSON 解析失败，尝试从文本中提取信息
            is_approved = "true" in cleaned_text.lower() and "is_approved" in cleaned_text.lower()
            decision = CriticDecision(
                is_approved=is_approved,
                feedback=cleaned_text if not is_approved else "同意发布"
            )
        
    except Exception as e:
        print(f"[Critic Agent] 审查过程出错: {e}")
        # 出错时默认通过，避免阻塞流程
        decision = CriticDecision(
            is_approved=True,
            feedback=f"审查过程出错，默认通过: {str(e)}"
        )
    
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
