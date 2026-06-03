"""
学习记录页面
"""

import streamlit as st


def render_records_page():
    """渲染学习记录页面"""
    st.title("学习记录")
    st.caption("查看你的学习历史和错题本")
    
    # 选项卡
    tab1, tab2, tab3 = st.tabs(["学习统计", "错题本", "知识图谱"])
    
    with tab1:
        show_learning_stats()
    
    with tab2:
        show_error_book()
    
    with tab3:
        show_knowledge_graph()


def show_learning_stats():
    """显示学习统计"""
    st.subheader("学习统计概览")
    
    # 模拟数据（实际应从后端获取）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("学习天数", "15", "+3")
    
    with col2:
        st.metric("对话轮次", "128", "+12")
    
    with col3:
        st.metric("掌握知识点", "42", "+5")
    
    with col4:
        st.metric("错题数量", "23", "-2")
    
    st.divider()
    
    # 学习趋势图（模拟）
    st.subheader("学习趋势")
    
    import pandas as pd
    import numpy as np
    
    # 生成模拟数据
    dates = pd.date_range(start="2024-01-01", periods=15, freq="D")
    data = pd.DataFrame({
        "日期": dates,
        "学习时长(分钟)": np.random.randint(30, 120, 15),
        "对话次数": np.random.randint(5, 20, 15)
    })
    
    st.line_chart(data.set_index("日期"))


def show_error_book():
    """显示错题本"""
    st.subheader("错题本")
    
    # 模拟错题数据
    errors = [
        {
            "知识点": "牛顿第二定律",
            "题目": "一个质量为2kg的物体受到10N的力，求加速度",
            "我的答案": "a = 10/2 = 5 m/s^2",
            "正确答案": "a = F/m = 10/2 = 5 m/s^2",
            "状态": "已掌握"
        },
        {
            "知识点": "化学平衡",
            "题目": "计算反应 N2 + 3H2 -> 2NH3 的平衡常数",
            "我的答案": "K = [NH3]^2 / ([N2][H2]^3)",
            "正确答案": "K = [NH3]^2 / ([N2][H2]^3)",
            "状态": "已掌握"
        },
        {
            "知识点": "导数应用",
            "题目": "求函数 f(x) = x^3 - 3x 的极值",
            "我的答案": "f'(x) = 3x^2 - 3，极值点 x = ±1",
            "正确答案": "f'(x) = 3x^2 - 3，极大值 f(-1) = 2，极小值 f(1) = -2",
            "状态": "待巩固"
        }
    ]
    
    for i, error in enumerate(errors):
        with st.expander(f"错题 {i+1}: {error['知识点']} - {error['状态']}"):
            st.markdown(f"**题目:** {error['题目']}")
            st.markdown(f"**我的答案:** {error['我的答案']}")
            st.markdown(f"**正确答案:** {error['正确答案']}")
            
            if error['状态'] == "待巩固":
                st.warning("这道题还需要巩固")
            else:
                st.success("已经掌握")


def show_knowledge_graph():
    """显示知识图谱"""
    st.subheader("知识图谱")
    
    st.info("知识图谱功能开发中...")
    
    # 模拟知识图谱
    st.markdown("""
    ```
    [数学]
        ├── 代数
        │   ├── 方程与不等式
        │   ├── 函数
        │   └── 数列
        ├── 几何
        │   ├── 平面几何
        │   └── 立体几何
        └── 微积分
            ├── 导数
            └── 积分
    
    [物理]
        ├── 力学
        │   ├── 运动学
        │   └── 动力学
        ├── 电磁学
        └── 光学
    
    [化学]
        ├── 无机化学
        ├── 有机化学
        └── 物理化学
    ```
    """)
