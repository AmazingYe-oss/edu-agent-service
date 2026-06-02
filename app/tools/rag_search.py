import httpx
from pydantic import BaseModel, Field
from app.core.config import settings

class SearchResultItem(BaseModel):
    index: int = Field(..., description="排名序号")
    content: str = Field(..., description="检索到的文本片段")
    file_name: str = Field(default="未知文件", description="来源文件名")
    file_type: str = Field(default="", description="文件类型扩展名")
    score: float | None = Field(default=None, description="相似度分数")

class SearchResponse(BaseModel):
    query: str = Field(..., description="原始查询语句")
    results: list[SearchResultItem] = Field(default_factory=list, description="检索结果列表")
    count: int = Field(default=0, description="结果总数")

def search_knowledge(query: str, top_k: int = 3) -> str:
    """
    调用底层的 edu-rag-bot 搜索接口获取相关知识
    """
    
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