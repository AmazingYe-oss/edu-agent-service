"""
Edu Multi-Agent Service - Streamlit 前端应用
"""

import streamlit as st
from utils.auth import init_session_state, logout, login, register

# 页面配置
st.set_page_config(
    page_title="Edu AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session state
init_session_state()

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .sidebar .sidebar-content {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# 主页面逻辑
def main():
    # 侧边栏
    with st.sidebar:
        st.title("🎓 Edu AI Assistant")
        st.divider()
        
        if st.session_state.get("authenticated", False):
            st.success(f"欢迎, {st.session_state.get('username', '用户')}!")
            st.divider()
            
            # 导航菜单
            page = st.radio(
                "导航",
                ["💬 智能对话", "📁 文件上传", "📊 学习记录"]
            )
            
            st.divider()
            
            if st.button("🚪 退出登录", use_container_width=True):
                logout()
                st.rerun()
        else:
            page = "🏠 登录"
    
    # 页面路由
    if not st.session_state.get("authenticated", False):
        show_landing_page()
    elif page == "💬 智能对话":
        show_chat_page()
    elif page == "📁 文件上传":
        show_upload_page()
    elif page == "📊 学习记录":
        show_records_page()

def show_landing_page():
    """首页/登录页面"""
    st.markdown('<h1 class="main-header">🎓 Edu AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">基于多智能体的个性化教育辅导系统</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["登录", "注册"])
        
        with tab1:
            show_login_form()
        
        with tab2:
            show_register_form()
        
        st.divider()
        st.markdown("""
        <div style="text-align: center; color: #888;">
            <p>功能特点：</p>
            <ul style="list-style: none; padding: 0;">
                <li>🤖 多智能体协作 - 7个专业AI Agent</li>
                <li>📚 RAG检索增强 - 基于权威教材</li>
                <li>🎯 个性化学习 - 智能出题与批改</li>
                <li>📊 学习追踪 - 错题本与知识图谱</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_login_form():
    """登录表单"""
    with st.form("login_form"):
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        submit = st.form_submit_button("登录", use_container_width=True)
        
        if submit:
            if username and password:
                success, message = login(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("请填写完整信息")

def show_register_form():
    """注册表单"""
    with st.form("register_form"):
        new_username = st.text_input("新用户名", placeholder="请设置用户名")
        new_password = st.text_input("新密码", type="password", placeholder="请设置密码")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        submit = st.form_submit_button("注册", use_container_width=True)
        
        if submit:
            if new_username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("两次密码不一致")
                else:
                    success, message = register(new_username, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.warning("请填写完整信息")

def show_chat_page():
    """聊天页面"""
    from components.chat import render_chat_page
    render_chat_page()

def show_upload_page():
    """文件上传页面"""
    from components.upload import render_upload_page
    render_upload_page()

def show_records_page():
    """学习记录页面"""
    from components.records import render_records_page
    render_records_page()

if __name__ == "__main__":
    main()
