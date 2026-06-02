import httpx
from langchain_core.tools import tool
from app.core.config import settings
from app.tools.rag_search import SearchResponse

@tool
def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """
    【核心工具】当用户询问具体的学科知识、定理、公式或教材内容时，调用此工具检索标准答案。
    参数 query: 应该是一个精简的搜索关键词（如 "牛顿第一定律" 或 "勾股定理公式"）。
    如果检索结果为空，请基于你自己的常识进行回答，但要向用户说明“教材库中未找到，以下基于通用知识解答”。
    """
    print(f"🔧 [Tool 触发] AI 决定使用 RAG 工具，搜索关键词: {query}")
    url = f"{settings.RAG_API_BASE_URL}/api/v1/search"
    payload = {
        "query": query,
        "top_k": top_k
    }
    try:
        response = httpx.post(url, json=payload, timeout=15.0)
        response.raise_for_status()
        search_data = SearchResponse(**response.json())
        
        if not search_data.results:
            return "数据库中未检索到相关资料。"
        
        context = ""
        for item in search_data.results:
            context += f"【参考资料 {item.index}】(来源: {item.file_name})\n{item.content}\n\n"
            
        return context
        
    except Exception as e:
        print(f" [RAG Tool] 检索失败: {e}")
        return "知识库检索服务暂不可用，请根据自身知识进行解答。"
