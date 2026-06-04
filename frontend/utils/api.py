"""
API 调用工具函数
"""

import httpx
import json
import streamlit as st
from typing import Optional, AsyncGenerator
import os
from  dotenv import load_dotenv
load_dotenv()

# API 基础配置
API_BASE_URL = "http://localhost:8080"
RAG_API_BASE_URL=os.getenv('RAG_API_BASE_URL')


async def stream_chat(
    message: str,
    user_id: str,
    session_id: str = "default"
) -> AsyncGenerator[str, None]:
    """
    流式调用聊天 API
    
    Args:
        message: 用户消息
        user_id: 用户ID
        session_id: 会话ID
        
    Yields:
        流式文本片段
    """
    url = f"{API_BASE_URL}/api/v1/chat"
    payload = {
        "message": message,
        "session_id": session_id,
        "user_id": user_id
    }
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                yield f"错误: HTTP {response.status_code}"
                return
            
            buffer = ""
            async for chunk in response.aiter_text():
                buffer += chunk
                while "\n\n" in buffer:
                    line, buffer = buffer.split("\n\n", 1)
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            return
                        try:
                            parsed = json.loads(data)
                            text = parsed.get("text", "")
                            error = parsed.get("error", "")
                            
                            if error:
                                yield f"[错误] {error}"
                            elif text:
                                # 过滤系统状态消息，只输出 AI 回复
                                if "[系统]" not in text:
                                    yield text
                                    
                        except json.JSONDecodeError:
                            continue


def upload_files(
    files: list,
    user_id: str,
    api_url: str = f"{RAG_API_BASE_URL}/api/v1/documents/batch"
) -> dict:
    """
    批量上传文件
    
    Args:
        files: 文件列表 [(filename, file_bytes, mime_type), ...]
        user_id: 用户ID
        api_url: API 地址
        
    Returns:
        API 响应
    """
    try:
        with httpx.Client(timeout=300.0) as client:
            # 准备文件数据
            file_data = []
            for filename, file_bytes, mime_type in files:
                file_data.append(("files", (filename, file_bytes, mime_type)))
            
            # 添加 user_id
            data = {"user_id": user_id}
            
            response = client.post(api_url, files=file_data, data=data)
            
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
    except httpx.ConnectError:
        return {"success": False, "error": "无法连接到后端服务，请确保服务已启动"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_api_health() -> bool:
    """检查 API 是否可用"""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}/")
            return response.status_code == 200
    except:
        return False


# 会话管理相关 API
def get_user_sessions(user_id: str) -> list:
    """获取用户的所有会话"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_BASE_URL}/api/v1/sessions", params={"user_id": user_id})
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        print(f"获取会话列表失败: {e}")
        return []


def get_session_messages(session_id: str) -> dict:
    """获取会话详情（包含消息历史）"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_BASE_URL}/api/v1/sessions/{session_id}")
            if response.status_code == 200:
                return response.json()
            return {}
    except Exception as e:
        print(f"获取会话详情失败: {e}")
        return {}


def create_session(user_id: str, title: str = None) -> dict:
    """创建新会话"""
    try:
        with httpx.Client(timeout=10.0) as client:
            payload = {}
            if title:
                payload["title"] = title
            response = client.post(
                f"{API_BASE_URL}/api/v1/sessions",
                params={"user_id": user_id},
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            return {}
    except Exception as e:
        print(f"创建会话失败: {e}")
        return {}


def delete_session(session_id: str) -> bool:
    """删除会话"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.delete(f"{API_BASE_URL}/api/v1/sessions/{session_id}")
            return response.status_code == 200
    except Exception as e:
        print(f"删除会话失败: {e}")
        return False
