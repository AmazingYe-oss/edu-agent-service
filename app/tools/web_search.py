# app/tools/web_search.py
"""联网搜索工具 - 使用阿里云百炼联网搜索 MCP (StreamableHttp)"""

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
        api_key = settings.DASHSCOPE_API_KEY
        if not api_key:
            return "联网搜索未配置 DASHSCOPE_API_KEY，请在 .env 中配置后使用。"
        
        # 调用阿里云百炼 MCP 联网搜索 (StreamableHttp)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # MCP JSON-RPC 请求
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
        
        print(f"[WebSearch] 搜索: {query}")
        
        # 使用 httpx 同步调用 MCP 服务
        with httpx.Client(timeout=30.0) as client:
            response = client.post(BAILIAN_MCP_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            # 处理响应（可能是 JSON 或 SSE）
            content_type = response.headers.get("content-type", "")
            
            if "text/event-stream" in content_type:
                # SSE 响应，解析事件流
                return _parse_sse_response(response.text)
            else:
                # JSON 响应
                result = response.json()
                return _parse_mcp_response(result)
        
    except httpx.TimeoutException:
        return "搜索请求超时，请稍后重试"
    except httpx.HTTPStatusError as e:
        print(f"[WebSearch HTTP Error] {e.response.status_code}: {e.response.text}")
        return f"搜索请求失败 (HTTP {e.response.status_code})"
    except Exception as e:
        print(f"[WebSearch Error] {e}")
        return f"搜索失败: {str(e)}"


def _parse_sse_response(sse_text: str) -> str:
    """解析 SSE 响应"""
    results = []
    for line in sse_text.split("\n"):
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                if "result" in data and "content" in data["result"]:
                    for content in data["result"]["content"]:
                        if "text" in content:
                            results.append(content["text"])
            except json.JSONDecodeError:
                continue
    return "\n\n".join(results) if results else "搜索未返回有效结果"


def _parse_mcp_response(result: dict) -> str:
    """解析 MCP JSON 响应"""
    if "result" in result and "content" in result["result"]:
        content_list = result["result"]["content"]
        if content_list:
            texts = [c.get("text", "") for c in content_list if "text" in c]
            return "\n\n".join(texts) if texts else "搜索未返回结果"
    
    if "error" in result:
        return f"搜索错误: {result['error'].get('message', '未知错误')}"
    
    return "搜索未返回有效结果"


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
