from fastapi import APIRouter, BackgroundTasks, Depends
from langchain_core.messages import HumanMessage
from langgraph.graph.state import Runnable, RunnableConfig
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.domain import Session as SessionModel, Message
from app.models.schemas import ChatRequest
import app.services.graph as graph_module
from app.services.async_persistence import persist_memory_async
import json
import uuid
import traceback
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    print(f"\n[DEBUG] chat_endpoint 被调用，message={request.message}, session_id={request.session_id}")
    
    # 检查 graph 是否已初始化（从模块获取最新值）
    edu_agent_app = graph_module.edu_agent_app
    if edu_agent_app is None:
        print("[ERROR] edu_agent_app 为 None，graph 未初始化！")
        return {"error": "服务正在初始化，请稍后重试"}
    
    # 自动创建会话（如果不存在）
    session = db.query(SessionModel).filter(SessionModel.session_id == request.session_id).first()
    if not session:
        session = SessionModel(
            session_id=request.session_id,
            user_id=request.user_id,
            title="新对话"
        )
        db.add(session)
        db.commit()
    
    # 保存用户消息
    user_message = Message(
        session_id=request.session_id,
        user_id=request.user_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    # LangGraph config：使用 session_id 作为 thread_id，自动管理短期记忆
    config = RunnableConfig(
        configurable={
            "user_id": request.user_id,
            "thread_id": request.session_id  # AsyncPostgresSaver 会根据 thread_id 自动恢复历史
        }
    )

    # 收集 AI 回复
    ai_response = ""

    async def event_generator():
        nonlocal ai_response
        # 从模块获取最新的 graph 实例
        current_graph = graph_module.edu_agent_app
        print(f"\n[API] 收到 {request.user_id} 在窗口 {request.session_id} 的流式请求...")
        try:
            # 收集最终状态用于异步持久化
            final_state = {}
            
            # AsyncPostgresSaver 会自动加载该 thread_id 的历史上下文
            async for event in current_graph.astream_events(
                {"user_message": request.message},
                config=config,
                version="v2"
            ):
                kind = event["event"]

                # 只抓取总结节点的输出，跳过其他节点
                if kind == "on_chat_model_stream":
                    node_name = event.get("name", "")
                    tags = event.get("tags", [])
                    metadata = event.get("metadata", {})
                    # 只输出 summarizer_node 的内容（通过final_output tag判断）
                    if "final_output" in tags:
                        chunk = event["data"]["chunk"].content
                        if chunk:
                            ai_response += chunk  # 收集 AI 回复
                            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
                            print(chunk, end="", flush=True)
                
                # 收集最终状态
                elif kind == "on_chain_end":
                    node_name = event.get("name", "")
                    # 收集所有节点的状态（包括 chitchat_node）
                    if node_name in ["planner", "learner_node", "quizzler_node", "scorer_node", "explainer_node", "critic_node", "chitchat_node"]:
                        output = event.get("data", {}).get("output", {})
                        if isinstance(output, dict):
                            final_state.update(output)

        except Exception as e:
            error_detail = traceback.format_exc()
            print(f"\n[错误] 流式输出异常: {e}")
            print(f"[错误详情] {error_detail}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        print("\n[API] 流式输出完毕。")
        
        # 保存 AI 消息到数据库
        if ai_response:
            ai_message = Message(
                session_id=request.session_id,
                user_id=request.user_id,
                role="assistant",
                content=ai_response,
                intent=final_state.get("user_intent", "unknown")
            )
            db.add(ai_message)
            db.commit()
            
            # 更新会话标题（如果是新会话且第一条消息）
            session_title = session.title
            if session_title == "新对话":
                # 用用户消息的前20个字符作为标题
                title = request.message[:20] + ("..." if len(request.message) > 20 else "")
                session.title = title
                db.commit()
        
        # 流式输出完成后，触发异步持久化（所有意图都触发，由持久化层决定是否保存）
        intent = final_state.get("user_intent", "unknown")
        knowledge_point = final_state.get("current_knowledge_point", None)
        
        background_tasks.add_task(
            persist_memory_async,
            user_id=request.user_id,
            session_id=request.session_id,
            intent=intent,
            user_message=request.message,
            draft_response=final_state.get("draft_response", ai_response),
            knowledge_point=knowledge_point
        )
        print(f"[API] 已添加异步持久化任务: intent={intent}")
        
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
