from app.services.state import AgentState
from app.core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from app.services.tools.rag_search import search_knowledge

def explainer_node(state: AgentState) -> dict:
    print("[Explain Agent] 收到任务，准备针对疑难/错题进行辅导...")
    
    user_latest_msg = state["messages"][-1].content
    intent = state.get("user_intent") or user_latest_msg
    
    search_query = f"{intent} 详细解析 解题步骤 易错点剖析"
    
    context = search_knowledge(search_query)
    print(f"[Explain Agent] 辅导资料检索完毕，资料长度: {len(context)} 字符")
    
    system_prompt = """你是一位极具耐心的金牌私教辅导老师。
用户的输入通常是因为他们做错了题目，或者对某道题的解析有疑问。你需要根据【辅导资料】为他们答疑解惑。

【辅导要求】
1. 安抚情绪：先肯定学生的钻研精神，不要有高高在上的说教感。
2. 抽丝剥茧：不要直接把标准答案糊在学生脸上。要一步一步地拆解【解题思路】。
3. 暴露盲区：指出这道题容易踩坑的地方（易错点），分析学生为什么会产生疑问。
4. 启发苏格拉底式提问：在讲解的最后，留一个微小的一步让学生自己推导，或者反问学生一个引导性问题。

【辅导资料】
{context}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "我的疑问或错题情况是：\n{question}")
    ])
    
    llm = get_llm()
    chain = prompt | llm
    
    print("[Explain Agent] 正在撰写循循善诱的辅导内容...")
    response = chain.invoke({
        "context": context,
        "question": user_latest_msg
    })
    
    print("[Explain Agent] 辅导内容生成完毕！")
    
    return {
        "draft_response": response.content,
        "retrieved_context": context
    }
