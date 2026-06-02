from app.services.state import AgentState
from app.core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from app.services.tools.rag_search import search_knowledge

def quizzler_node(state: AgentState) -> dict:
    print("📚 [Quizzler Agent] 收到任务，准备生成测验题目...")
    
    user_latest_msg = state["messages"][-1].content
    intent = state.get("user_intent") or user_latest_msg
    search_query = f"{intent} 相关的练习题 测试题 考题"
    

    context = search_knowledge(search_query)
    print(f"🔍 [Quizzler Agent] 知识库检索完毕，资料长度: {len(context)} 字符")
    
    system_prompt = """你是一位经验丰富、要求严格的出题老师。
你的任务是根据提供的【题库资料】，为学生生成几道高质量的练习题。

【出题要求】
1. 贴合需求：必须紧扣用户要求的知识点和难度。
2. 基于资料：优先使用【题库资料】中检索到的原题或改编题。如果资料里完全没有题，请基于资料中的知识点自行出题，保证不超纲。
3. 题目数量：如果没有特别说明，默认出 2-3 道题（题型可以包含选择题或解答题）。
4. 格式排版：请清晰地列出题目序号。
5. 绝对禁令：千万不要直接给出答案和解析！你的目的是考学生，不是把答案喂给他们！

【题库资料】
{context}
"""
    feedback = state.get("critic_feedback")
    if feedback and not state.get("is_approved"):
        print(f" [Quizzler Agent] 收到教导主任的打回意见，正在反思修改...")
        system_prompt += f"\n\n【教导主任打回意见】\n你上一次的回答未通过审查，原因是：{feedback}\n请务必针对上述意见，重新生成一份更好的题目！"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])
    
    llm = get_llm()
    chain = prompt | llm
    
    print(" [Quizzler Agent] 正在根据资料生成测验题目...")
    response = chain.invoke({
        "context": context,
        "question": user_latest_msg
    })
    
    print("[Quizzler Agent] 测验题目生成完毕！")
    
    return {
        "draft_response": response.content,
        "retrieved_context": context
    }
