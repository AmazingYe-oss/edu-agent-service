import json
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
from app.core.database import SessionLocal
from app.models.domain import UserProfile, ErrorBook
from app.core.dashclient import search_long_term_memory

@tool
def get_user_profile_tool(config: RunnableConfig) -> str:
    """
    【技能：查阅学生画像】
    获取当前学生的知识点掌握情况(掌握度为0~1)和学习状态。
    在规划教学路线(Planner)或出题前，必须先调用此技能了解学生底子。
    注意：不需要传递任何参数，直接调用即可。
    """
    user_id = config.get("configurable", {}).get("user_id", "user_123")
    
    print(f"🔧 [Tool 触发] AI 正在翻阅学生 {user_id} 的用户画像档案...")
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile or not profile.knowledge_state:
            return "该学生是新用户，目前还没有足够的数据生成画像。"
        
        # 将 JSONB 对象转为字符串让大模型阅读
        return f"学生的知识点画像：{json.dumps(profile.knowledge_state, ensure_ascii=False)}"
    except Exception as e:
        return f"查询画像失败：{e}"
    finally:
        db.close()

@tool
def check_error_book_tool(knowledge_point: str, config: RunnableConfig) -> str:
    """
    【技能：查阅错题本】
    出题或辅导前，根据具体的“知识点”查阅该学生以前是否做错过相关题目。
    参数 knowledge_point: 必须是一个简短具体的知识点名称（如“牛顿第一定律”、“勾股定理”）。
    """
    user_id = config.get("configurable", {}).get("user_id", "user_123")
    print(f"🔧 [Tool 触发] AI 正在翻阅错题本，检索关键词: {knowledge_point}...")
    
    db = SessionLocal()
    try:
        # 使用 ilike 进行模糊匹配查询
        errors = db.query(ErrorBook).filter(
            ErrorBook.user_id == user_id,
            ErrorBook.knowledge_point.ilike(f"%{knowledge_point}%")
        ).order_by(ErrorBook.created_at.desc()).limit(3).all()

        if not errors:
            return f"错题本中没有找到关于【{knowledge_point}】的错题记录。学生可能还没学，或者已经完全掌握。"
        
        res = []
        for i, e in enumerate(errors):
            res.append(f"错题{i+1}: 题目内容=【{e.question_content}】 | 错误原因=【{e.ai_analysis}】")
        return "\n".join(res)
    except Exception as e:
        return f"查阅错题本失败：{e}"
    finally:
        db.close()

@tool
def search_user_memory_tool(query: str, config: RunnableConfig) -> str:
    """
    【技能：查阅长期记忆】
    当你不知道用户刚才暗示的历史事件、或者需要回顾用户过去的表现时，调用此向量库搜索工具。
    参数 query: 描述你想知道的信息（如“用户之前做错了什么题”、“用户说他喜欢什么”）。
    """
    user_id = config.get("configurable", {}).get("user_id", "user_123")
    print(f"🔧 [Tool 触发] AI 正在检索长时脑区 (DashVector)，意图: {query}...")
    
    # 调用我们在 dashclient.py 写好的方法
    memories = search_long_term_memory(user_id, query, top_k=2)
    if not memories:
        return "长期记忆库中没有找到相关的记录。"
    return f"找到以下历史记忆：\n{memories}"
