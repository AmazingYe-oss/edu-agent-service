"""
异步持久化服务模块
将数据持久化操作从主响应链路中解耦，使用 FastAPI BackgroundTasks 异步执行
"""

from app.core.database import SessionLocal
from app.models.domain import ErrorBook, UserProfile
from app.core.dashclient import save_long_term_memory
from sqlalchemy.dialects.postgresql import insert
from typing import Optional
import logging

logger = logging.getLogger(__name__)


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
    logger.info(f"[Async Persistence] 开始异步持久化用户 {user_id} 的学习数据...")
    
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
                
                # 异步写入 DashVector 长期记忆
                save_long_term_memory(
                    user_id, 
                    session_id, 
                    f"用户在解答【{user_message[:20]}】时做错了，原因是：{draft_response[:30]}"
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
            
            # 异步写入 DashVector 长期记忆
            save_long_term_memory(
                user_id, 
                session_id, 
                f"用户学习了新知识点：{knowledge_point or '通用知识'}"
            )
        
        else:
            logger.debug(f"[Async Persistence] 意图 {intent} 无需持久化处理")
            
    except Exception as e:
        logger.error(f"❌ [Async Persistence] 数据库沉淀失败: {e}")
        db.rollback()
    finally:
        db.close()
        
    logger.info(f"✅ [Async Persistence] 用户 {user_id} 的数据持久化完成")
