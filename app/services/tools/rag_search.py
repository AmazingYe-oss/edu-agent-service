import httpx
from typing import Dict, Any, List
from app.services.state import GraphState, SearchDocument
from app.core.config import settings

async def search_rag_api(query: str, top_k: int = 5) -> List[SearchDocument]:
    """调用 RAG API 进行搜索"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.RAG_API_BASE_URL}/api/v1/search",
                json={
                    "query": query,
                    "top_k": top_k
                },
                headers={
                    "Authorization": f"Bearer {settings.RAG_API_KEY}" if settings.RAG_API_KEY else "",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append(SearchDocument(
                    content=item.get("content", ""),
                    source=item.get("source"),
                    score=item.get("score", 0.0),
                    metadata=item.get("metadata")
                ))
            return results
            
        except Exception as e:
            print(f"RAG API 调用失败: {e}")
            return []

async def rag_search_tool(state: GraphState) -> Dict[str, Any]:
    """RAG 搜索工具节点"""
    try:
        # 从计划中提取关键词进行搜索
        query = state.user_query
        
        # 如果有计划，使用计划中的关键词
        if state.plan:
            # 简单的关键词提取（实际项目中可以更复杂）
            lines = state.plan.split("\n")
            for line in lines:
                if "搜索" in line or "查找" in line:
                    query = line.split("：")[-1] if "：" in line else line
                    break
        
        results = await search_rag_api(query)
        
        return {
            "search_results": results,
            "current_agent": "learner"  # 返回给 learner 处理
        }
    except Exception as e:
        return {
            "error": f"RAG 搜索错误: {str(e)}",
            "search_results": []
        }
