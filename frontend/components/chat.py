"""
聊天页面 - 类似 ChatGPT 的界面
"""

import streamlit as st
import asyncio
from utils.api import stream_chat, get_user_sessions, get_session_messages, create_session, delete_session


def render_chat_page():
    """渲染聊天页面"""
    st.title("智能对话")
    st.caption("与 AI 助手进行多轮对话，支持学习、出题、批改、解析等功能")
    
    # 初始化会话状态
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    
    # 显示聊天历史
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("输入你的问题..."):
        # 确保有会话 ID
        if not st.session_state.current_session_id:
            user_id = st.session_state.get("user_id", "anonymous")
            new_session = create_session(user_id)
            if new_session:
                st.session_state.current_session_id = new_session["session_id"]
            else:
                st.error("创建会话失败，请重试")
                return
        
        # 添加用户消息到历史
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 显示 AI 回复（流式输出）
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 调用流式 API
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def get_stream_response():
                    nonlocal full_response
                    async for chunk in stream_chat(
                        message=prompt,
                        user_id=st.session_state.get("user_id", "anonymous"),
                        session_id=st.session_state.current_session_id
                    ):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                
                loop.run_until_complete(get_stream_response())
                loop.close()
                
            except Exception as e:
                full_response = f"发生错误: {str(e)}"
                message_placeholder.error(full_response)
        
        # 添加 AI 回复到历史
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
    
    # 侧边栏功能
    with st.sidebar:
        st.divider()
        st.subheader("对话管理")
        
        # 新建对话按钮
        if st.button("新建对话", use_container_width=True, type="primary"):
            user_id = st.session_state.get("user_id", "anonymous")
            new_session = create_session(user_id)
            if new_session:
                st.session_state.current_session_id = new_session["session_id"]
                st.session_state.chat_history = []
                st.rerun()
        
        # 获取会话列表
        user_id = st.session_state.get("user_id", "anonymous")
        sessions = get_user_sessions(user_id)
        
        if sessions:
            st.divider()
            st.subheader("历史会话")
            
            for s in sessions:
                session_id = s["session_id"]
                title = s.get("title", "新对话")
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    # 会话按钮
                    is_current = session_id == st.session_state.current_session_id
                    btn_label = f"{title}" + (" [当前]" if is_current else "")
                    if st.button(btn_label, key=f"session_{session_id}", use_container_width=True):
                        # 加载会话消息
                        detail = get_session_messages(session_id)
                        if detail and "messages" in detail:
                            st.session_state.chat_history = [
                                {"role": m["role"], "content": m["content"]}
                                for m in detail["messages"]
                            ]
                            st.session_state.current_session_id = session_id
                            st.rerun()
                with col2:
                    # 删除按钮
                    if st.button("X", key=f"delete_{session_id}"):
                        if delete_session(session_id):
                            if st.session_state.current_session_id == session_id:
                                st.session_state.current_session_id = None
                                st.session_state.chat_history = []
                            st.rerun()
        
        # 对话历史数量
        st.divider()
        st.metric("对话轮次", len(st.session_state.chat_history) // 2)
        
        st.divider()
        st.subheader("功能说明")
        st.markdown("""
        - **学习模式**: 直接提问知识点
        - **出题模式**: 请求出题测试
        - **批改模式**: 提交答案批改
        - **解析模式**: 请求错题解析
        """)
