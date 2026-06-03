"""
文件上传页面 - 支持批量上传
"""

import streamlit as st
from utils.api import upload_files


def render_upload_page():
    """渲染文件上传页面"""
    st.title("文件上传")
    st.caption("批量上传学习资料，支持 PDF、Word、TXT 等格式")
    
    # 文件上传区域
    uploaded_files = st.file_uploader(
        "选择文件",
        type=["pdf", "docx", "doc", "txt", "md"],
        accept_multiple_files=True,
        help="支持批量上传，最多同时上传 10 个文件"
    )
    
    # 显示已选择的文件
    if uploaded_files:
        st.subheader(f"已选择 {len(uploaded_files)} 个文件")
        
        # 文件列表
        file_info = []
        for file in uploaded_files:
            file_size = len(file.getvalue()) / 1024  # KB
            file_info.append({
                "文件名": file.name,
                "大小": f"{file_size:.1f} KB",
                "类型": file.type
            })
        
        st.dataframe(file_info, use_container_width=True)
        
        st.divider()
        
        # 上传按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("开始上传", use_container_width=True, type="primary"):
                upload_files_to_server(uploaded_files)
    
    # 上传说明
    st.divider()
    st.subheader("支持的文件格式")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **文档格式:**
        - PDF (.pdf)
        - Word (.docx, .doc)
        - 纯文本 (.txt)
        - Markdown (.md)
        """)
    
    with col2:
        st.markdown("""
        **使用说明:**
        1. 点击"选择文件"按钮
        2. 按住 Ctrl 可多选文件
        3. 点击"开始上传"按钮
        4. 等待上传完成
        """)


def upload_files_to_server(uploaded_files):
    """上传文件到服务器"""
    user_id = st.session_state.get("user_id", "anonymous")
    
    # 准备文件数据
    files_data = []
    for file in uploaded_files:
        files_data.append((file.name, file.getvalue(), file.type))
    
    # 显示上传进度
    with st.status("正在上传...", expanded=True) as status:
        st.write(f"准备上传 {len(files_data)} 个文件...")
        
        # 调用上传 API
        result = upload_files(files_data, user_id)
        
        if result["success"]:
            status.update(label="上传完成!", state="complete", expanded=False)
            st.success("文件上传成功!")
            
            # 显示上传结果
            if "data" in result:
                st.json(result["data"])
        else:
            status.update(label="上传失败", state="error")
            st.error(f"上传失败: {result['error']}")
