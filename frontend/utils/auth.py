"""
认证相关工具函数 - 调用后端 API
"""

import streamlit as st
import httpx
from typing import Optional, Tuple

# API 基础配置
API_BASE_URL = "http://localhost:8080"


def init_session_state():
    """初始化 session state"""
    defaults = {
        "authenticated": False,
        "username": None,
        "user_id": None,
        "chat_history": [],
        "current_session_id": "default"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login(username: str, password: str) -> Tuple[bool, str]:
    """
    登录验证 - 调用后端 API
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        (是否成功, 消息)
    """
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state["authenticated"] = True
                st.session_state["username"] = data.get("username")
                st.session_state["user_id"] = data.get("user_id")
                return True, "登录成功"
            else:
                error_detail = response.json().get("detail", "登录失败")
                return False, error_detail
                
    except httpx.ConnectError:
        return False, "无法连接到服务器，请确保后端服务已启动"
    except Exception as e:
        return False, f"登录失败: {str(e)}"


def register(username: str, password: str) -> Tuple[bool, str]:
    """
    注册 - 调用后端 API
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        (是否成功, 消息)
    """
    # 前端验证
    if len(username) < 3:
        return False, "用户名至少3位"
    if len(password) < 6:
        return False, "密码至少6位"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/v1/auth/register",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                return True, "注册成功，请登录"
            else:
                error_detail = response.json().get("detail", "注册失败")
                return False, error_detail
                
    except httpx.ConnectError:
        return False, "无法连接到服务器，请确保后端服务已启动"
    except Exception as e:
        return False, f"注册失败: {str(e)}"


def logout():
    """退出登录"""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["user_id"] = None
    st.session_state["chat_history"] = []


def get_current_user() -> Optional[dict]:
    """获取当前登录用户信息"""
    if st.session_state.get("authenticated"):
        return {
            "user_id": st.session_state.get("user_id"),
            "username": st.session_state.get("username")
        }
    return None


def require_auth():
    """要求用户登录"""
    if not st.session_state.get("authenticated"):
        st.warning("请先登录")
        st.stop()
