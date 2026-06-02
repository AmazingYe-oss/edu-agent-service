from app.services.state import AgentState
from app.core.database import SessionLocal
from app.models.domain import ErrorBook, UserProfile
from app.core.dashclient import save_long_term_memory
from sqlalchemy.dialects.postgresql import insert

def memory_node(state: AgentState, config: dict) -> dict:
    """注意新版本支持传入 config，我们可以从中提取 session_id"""
    print("💾 [Memory Agent] 正在连接阿里云，沉淀业务数据...")
    
    intent = state.get("next_agent")
    draft = state.get("draft_response", "")
    user_intent = state.get("user_intent", "未知知识点")
    
    # 从 config 中提取 metadata (API 层传进来的)
    configurable = config.get("configurable", {})
    session_id = configurable.get("thread_id", "default_session")
    user_id = configurable.get("user_id", "user_123")  # API 层会传这个
    
    # 获取用户最后一次说的内容
    user_msgs = [m for m in state.get("messages", []) if m.type == "human"]
    user_msg_content = user_msgs[-1].content if user_msgs else ""
    
    db = SessionLocal()
    try:
        if intent == "score":
            if "错误" in draft or "不对" in draft or "部分正确" in draft:
                new_error = ErrorBook(
                    user_id=user_id,
                    session_id=session_id,
                    knowledge_point=user_intent,
                    question_content=user_msg_content,
                    ai_analysis=draft
                )
                db.add(new_error)
                db.commit()
                print(f"📓 【PG 数据库】发现错题，已存入 error_books 表！")
                save_long_term_memory(user_id, session_id, f"用户在解答【{user_msg_content[:20]}】时做错了，原因是：{draft[:30]}")

        # 2. 用户画像逻辑 (Learn Agent)
        elif intent == "learn":
            # PostgreSQL 的 UPSERT：如果无记录就插入，有记录就追加 JSONB
            stmt = insert(UserProfile).values(
                user_id=user_id,
                knowledge_state={user_intent: {"mastery": 0.5, "status": "learning"}}
            ).on_conflict_do_update(
                index_elements=['user_id'],
                set_={'knowledge_state': UserProfile.knowledge_state.concat({user_intent: {"mastery": 0.5, "status": "learning"}})}
            )
            db.execute(stmt)
            db.commit()
            print("📈 【PG 数据库】用户知识点画像已更新！")
            save_long_term_memory(user_id, session_id, f"用户学习了新知识点：{user_intent}")
            
    except Exception as e:
        print(f" 数据库沉淀失败: {e}")
        db.rollback()
    finally:
        db.close()
        
    return {}
