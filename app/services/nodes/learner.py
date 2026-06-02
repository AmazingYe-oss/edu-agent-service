# app/services/nodes/learner.py
from app.services.state import AgentState
from app.core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from app.services.tools.rag_search import search_knowledge

def learner_node(state: AgentState) -> dict:
    print("[Learner Agent] 收到任务，准备查阅资料并备课...")
    
    user_latest_msg = state["messages"][-1].content
    search_query = state.get("user_intent") or user_latest_msg
    

    context = search_knowledge(search_query)
    print(f"🔍 [Learner Agent] 知识库检索完毕，资料长度: {len(context)} 字符")
    
    system_prompt = """你是一位深受学生喜爱的特级教师。你的任务是根据提供的【参考资料】为学生讲解知识点。

【教学要求】
1. 通俗易懂：语言要幽默风趣，多用生活中的生动比喻。
2. 严谨求实：必须基于【参考资料】进行讲解，绝对不能编造资料中没有的核心概念！
3. 结构清晰：可以分为“概念引入”、“核心原理解释”、“生活实例”三个部分。
4. 启发思考：在最后抛出一个小问题，引导学生思考。

【参考资料】
{context}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])
    
    llm = get_llm()
    chain = prompt | llm
    
    print(" [Learner Agent] 正在根据资料生成教学内容...")
    response = chain.invoke({
        "context": context,
        "question": user_latest_msg
    })
    
    print("[Learner Agent] 讲解内容生成完毕！")
    
    return {
        "draft_response": response.content,
        "retrieved_context": context
    }
