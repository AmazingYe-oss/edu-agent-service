from fastapi import APIRouter, BackgroundTasks
from langchain_core.messages import HumanMessage
from langgraph.graph.state import Runnable, RunnableConfig
from app.models.schemas import ChatRequest
from app.services.graph import edu_agent_app
from app.services.async_persistence import persist_memory_async
import json
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    config = RunnableConfig(
        configurable={
            "user_id": request.user_id,
            "thread_id": request.session_id
        }
    )

    async def event_generator():
        print(f"\n[API] 收到 {request.user_id} 在窗口 {request.session_id} 的流式请求...")
        try:
            # 收集最终状态用于异步持久化
            final_state = {}
            
            async for event in edu_agent_app.astream_events(
                {"user_message": request.message, "history": []},
                config=config,
                version="v2"
            ):
                kind = event["event"]

                # 只抓取大模型的输出，跳过状态播报
                if kind == "on_chat_model_stream":
                    node_name = event.get("name", "")
                    # 过滤 critic_node 的流式输出
                    if node_name != "critic_node":
                        chunk = event["data"]["chunk"].content
                        if chunk:
                            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
                            print(chunk, end="", flush=True)
                
                # 收集最终状态
                elif kind == "on_chain_end":
                    node_name = event.get("name", "")
                    if node_name == "critic_node":
                        # critic_node 结束时，收集状态
                        output = event.get("data", {}).get("output", {})
                        if isinstance(output, dict):
                            final_state.update(output)

        except Exception as e:
            print(f"\n[错误] 流式输出异常: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        print("\n[API] 流式输出完毕。")
        
        # 流式输出完成后，触发异步持久化
        intent = final_state.get("user_intent", "unknown")
        knowledge_point = final_state.get("current_knowledge_point", None)
        
        # 只有 learn 和 score 意图需要持久化
        if intent in ["learn", "score"]:
            background_tasks.add_task(
                persist_memory_async,
                user_id=request.user_id,
                session_id=request.session_id,
                intent=intent,
                user_message=request.message,
                draft_response=final_state.get("draft_response", ""),
                knowledge_point=knowledge_point
            )
            print(f"[API] 已添加异步持久化任务: intent={intent}")
        
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
