from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.graph import run_graph

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话接口 - 接收用户消息并返回智能代理的响应
    """
    try:
        result = await run_graph(request.message, request.conversation_id)
        return ChatResponse(
            response=result["response"],
            conversation_id=result.get("conversation_id")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
