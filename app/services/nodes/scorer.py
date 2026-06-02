from app.services.state import AgentState
from app.core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from app.services.tools.rag_search import search_knowledge

def scorer_node(state: AgentState) -> dict:
    print("[Score Agent] 收到任务，准备检索标准答案并批改作业...")
    
    user_latest_msg = state["messages"][-1].content
    intent = state.get("user_intent") or user_latest_msg
    search_query = f"{intent} 标准答案 评分标准 解析"
    context = search_knowledge(search_query)
    print(f"[Score Agent] 答案检索完毕，资料长度: {len(context)} 字符")
    
    system_prompt = """你是一位公正严明且充满鼓励的阅卷老师。
用户的输入是他们提交的题目答案。你的任务是根据【参考答案资料】批改用户的解答。

【批改要求】
1. 明确判定：首先明确告诉学生“回答正确”、“回答错误”或“部分正确”。
2. 对比分析：简明扼要地指出学生的答案与标准答案的差异。
3. 给出评分：如果合适，给出一个虚拟的得分（例如 80/100 分）。
4. 适度点评：给出鼓励性的评语。如果学生做错了，简单点出错误原因，但不要在这里长篇大论地从头讲授知识点（那是辅导老师的工作）。

【参考答案资料】
{context}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "我的答案/解答是：\n{question}")
    ])
    
    llm = get_llm()
    chain = prompt | llm
    
    print("[Score Agent] 正在对比答案，进行批改打分...")
    response = chain.invoke({
        "context": context,
        "question": user_latest_msg
    })
    
    print("[Score Agent] 批改完毕！")
    
    return {
        "draft_response": response.content,
        "retrieved_context": context
    }
