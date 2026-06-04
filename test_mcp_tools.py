import httpx
import json
from app.core.config import settings

BAILIAN_MCP_URL = "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp"

headers = {
    "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

# 获取可用工具列表
payload = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
}

print("获取 MCP 可用工具列表...")
with httpx.Client(timeout=30.0) as client:
    response = client.post(BAILIAN_MCP_URL, json=payload, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:2000]}")
