"""
异步持久化服务模块
将数据持久化操作从主响应链路中解耦，使用 FastAPI BackgroundTasks 异步执行
"""

from app.core.database import SessionLocal
from app.models.domain import ErrorBook, UserProfile
from app.core.dashclient import save_long_term_memory
from app.core.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.dialects.postgresql import insert
from typing import Optional
import logging
import re

logger = logging.getLogger(__name__)

# 记忆价值判断关键词
MEANINGFUL_KEYWORDS = [
    "是", "叫", "名字", "喜欢", "想学", "学习", "目标", "基础", "小白",
    "专业", "年级", "大学", "高中", "初中", "擅长", "薄弱", "困难",
    "考试", "考研", "高考", "竞赛", "编程", "数学", "物理", "英语"
]

# 噪音对话模式
NOISE_PATTERNS = [
    r"^[嗯啊哦呃嘿哈嘻呀]+$",  # 纯语气词
    r"^(好的|好吧|行|可以|没问题|知道了|明白|了解)$",  # 简单确认
    r"^(再见|拜拜|下次见|晚安|早安)$",  # 告别语
    r"^(谢谢|感谢|多谢|thanks)$",  # 简单感谢
    r"^[\U0001F600-\U0001F64F]+$",  # 纯表情
]


def is_meaningful_message(user_message: str, ai_response: str) -> bool:
    """
    使用轻量规则判断对话是否包含有价值的记忆信息
    """
    user_msg = user_message.strip()
    
    # 过短的消息通常是噪音
    if len(user_msg) < 3:
        return False
    
    # 检查是否匹配噪音模式
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, user_msg, re.IGNORECASE):
            logger.debug(f"[过滤] 噪音对话: {user_msg}")
            return False
    
    # 检查是否包含有意义的关键词
    for keyword in MEANINGFUL_KEYWORDS:
        if keyword in user_msg:
            return True
    
    # 如果用户消息较长，可能包含有价值的信息
    if len(user_msg) > 15:
        return True
    
    return False


async def extract_memory_with_llm(user_message: str, ai_response: str) -> Optional[str]:
    """
    使用 LLM 从对话中提炼出有价值的记忆事实
    """
    try:
        llm = get_llm()
        
        prompt = f"""请从以下对话中提取一条简短的事实性记忆（用于AI记住用户的信息）。

对话内容：
用户：{user_message[:100]}
AI：{ai_response[:100]}

提取规则：
1. 只提取用户的个人信息、学习偏好、知识水平等事实
2. 如果没有值得记住的信息，回复“无”
3. 提取的记忆要简短（不超过50字）
4. 示例：“用户是编程小白”、“用户想学微积分”、“用户是大三学生”

请直接输出提炼后的记忆，不要添加任何解释："""
        
        result = await llm.ainvoke([HumanMessage(content=prompt)])
        memory = result.content.strip()
        
        if memory and memory != "无" and len(memory) > 2:
            return memory
        return None
        
    except Exception as e:
        logger.error(f"[LLM记忆提炼] 失败: {e}")
        return None


async def persist_memory_async(
    user_id: str,
    session_id: str,
    intent: str,
    user_message: str,
    draft_response: str,
    knowledge_point: Optional[str] = None
):
    """
    异步持久化学习数据到 PostgreSQL 和 DashVector
    
    Args:
        user_id: 用户ID
        session_id: 会话ID
        intent: 用户意图 (learn/quiz/score/explain)
        user_message: 用户原始消息
        draft_response: AI生成的回复内容
        knowledge_point: 知识点 (可选)
    """
    logger.info(f"[Async Persistence] 开始异步持久化用户 {user_id} 的学习数据，意图: {intent}")
    
    db = SessionLocal()
    try:
        # 1. 错题落盘逻辑 (Scorer Agent 产生的错题)
        if intent == "score":
            if "错误" in draft_response or "不对" in draft_response or "部分正确" in draft_response:
                new_error = ErrorBook(
                    user_id=user_id,
                    session_id=session_id,
                    knowledge_point=knowledge_point or "未知知识点",
                    question_content=user_message,
                    ai_analysis=draft_response
                )
                db.add(new_error)
                db.commit()
                logger.info("[PG 数据库] 发现错题，已存入 error_books 表！")
                
                # 错题记忆保存到向量库
                save_long_term_memory(
                    user_id, 
                    session_id, 
                    f"用户在解答【{knowledge_point or '未知知识点'}】时做错了，题目：{user_message[:30]}"
                )

        # 2. 用户画像逻辑 (Learn Agent 产生的学习记录)
        elif intent == "learn":
            # PostgreSQL 的 UPSERT：如果无记录就插入，有记录就追加 JSONB
            stmt = insert(UserProfile).values(
                user_id=user_id,
                knowledge_state={knowledge_point or "通用知识": {"mastery": 0.5, "status": "learning"}}
            ).on_conflict_do_update(
                index_elements=['user_id'],
                set_={'knowledge_state': UserProfile.knowledge_state.concat(
                    {knowledge_point or "通用知识": {"mastery": 0.5, "status": "learning"}}
                )}
            )
            db.execute(stmt)
            db.commit()
            logger.info("[PG 数据库] 用户知识点画像已更新！")
            
            # 学习记忆保存到向量库
            save_long_term_memory(
                user_id, 
                session_id, 
                f"用户学习了知识点：{knowledge_point or '通用知识'}，问题：{user_message[:30]}"
            )
        
        # 3. 通用对话记忆（所有意图）
        # 使用轻量规则过滤噪音
        if is_meaningful_message(user_message, draft_response):
            # 使用 LLM 提炼记忆
            extracted_memory = await extract_memory_with_llm(user_message, draft_response)
            if extracted_memory:
                save_long_term_memory(user_id, session_id, extracted_memory)
                logger.info(f"[DashVector] 已保存提炼后的记忆: {extracted_memory}")
            else:
                logger.debug("[DashVector] LLM判断无有价值记忆")
        else:
            logger.debug(f"[DashVector] 噪音对话已过滤: {user_message[:20]}")
            
    except Exception as e:
        logger.error(f"[Async Persistence] 数据库沉淀失败: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()
        
    logger.info(f"[Async Persistence] 用户 {user_id} 的数据持久化完成")
