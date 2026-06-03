from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from langgraph.graph.state import Runnable, RunnableConfig
from app.models.schemas import ChatRequest
from app.services.graph import edu_agent_app
import json
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    config = RunnableConfig(
        configurable={
            "user_id": request.user_id,
            "thread_id": request.session_id
        }
    )

    async def event_generator():
        print(f"\n[API] 收到 {request.user_id} 在窗口 {request.session_id} 的流式请求...")
        try:
            async for event in edu_agent_app.astream_events(
                {"user_message": request.message, "history": []},
                config=config,
                version="v2"
            ):
                kind = event["event"]

                # 1. 播报 Agent 切换状态
                if kind == "on_chain_start":
                    node_name = event.get("name", "")
                    if node_name in ["planner", "learner_node", "critic_node", "memory_node"]:
                        status_msg = f"\n\n[系统] 正在唤醒 {node_name}...\n"
                        yield f"data: {json.dumps({'text': status_msg}, ensure_ascii=False)}\n\n"
                        print(status_msg, end="", flush=True)

                # 2. 抓取所有大模型的思考与吐字
                elif kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
                        print(chunk, end="", flush=True)

        except Exception as e:
            print(f"\n[错误] 流式输出异常: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        print("\n[API] 流式输出完毕。")
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
