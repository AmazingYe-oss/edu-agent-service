"""
聊天页面 - 类似 ChatGPT 的界面
"""

import streamlit as st
import asyncio
from utils.api import stream_chat


def render_chat_page():
    """渲染聊天页面"""
    st.title("智能对话")
    st.caption("与 AI 助手进行多轮对话，支持学习、出题、批改、解析等功能")
    
    # 初始化聊天历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 显示聊天历史
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("输入你的问题..."):
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
                        session_id=st.session_state.get("current_session_id", "default")
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
        st.subheader("对话设置")
        
        # 新建对话按钮
        if st.button("新建对话", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_session_id = f"session_{len(st.session_state.chat_history)}"
            st.rerun()
        
        # 对话历史数量
        st.metric("对话轮次", len(st.session_state.chat_history) // 2)
        
        st.divider()
        st.subheader("功能说明")
        st.markdown("""
        - **学习模式**: 直接提问知识点
        - **出题模式**: 请求出题测试
        - **批改模式**: 提交答案批改
        - **解析模式**: 请求错题解析
        """)
