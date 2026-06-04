# app/tools/web_search.py
"""联网搜索工具 - 使用阿里云百炼联网搜索 MCP"""

import httpx
import json
from langchain_core.tools import tool
from app.core.config import settings


# 阿里云百炼 MCP 联网搜索配置
BAILIAN_MCP_URL = "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp"


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    联网搜索工具：搜索互联网获取实时信息。
    当用户询问天气、新闻、实时信息等问题时使用此工具。
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数量，默认5条
    
    Returns:
        搜索结果的文本摘要
    """
    try:
        # 检查是否配置了搜索 API Key
        if not settings.XIAOMI_API_KEY:
            return "联网搜索未配置 API Key，请配置后使用。"
        
        # 调用阿里云百炼 MCP 联网搜索
        headers = {
            "Authorization": f"Bearer {settings.XIAOMI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "web_search",
                "arguments": {
                    "query": query,
                    "max_results": max_results
                }
            },
            "id": 1
        }
        
        # 使用 httpx 同步调用 MCP 服务
        with httpx.Client(timeout=30) as client:
            response = client.post(BAILIAN_MCP_URL, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
        
        # 解析 MCP 响应
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            if content and len(content) > 0:
                return content[0].get("text", "搜索未返回结果")
        
        return "搜索未返回有效结果"
        
    except httpx.TimeoutException:
        return "搜索请求超时，请稍后重试"
    except Exception as e:
        print(f"[WebSearch Error] {e}")
        return f"搜索失败: {str(e)}"


@tool  
def web_search_with_context(query: str, context: str = "") -> str:
    """
    带上下文的联网搜索工具。
    当需要结合用户具体情况进行搜索时使用。
    
    Args:
        query: 搜索关键词
        context: 上下文信息（如用户位置、时间等）
    
    Returns:
        搜索结果摘要
    """
    try:
        full_query = f"{context} {query}" if context else query
        return web_search.invoke({"query": full_query})
        
    except Exception as e:
        return f"搜索失败: {str(e)}"
