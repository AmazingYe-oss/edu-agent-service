from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from app.models.schemas import ChatRequest, ChatResponse
from app.services.graph import edu_agent_app

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print(f"\n[API 收到新请求] User: {request.message}")
    
    initial_state = {
        "messages": [HumanMessage(content=request.message)]
    }
    final_state = edu_agent_app.invoke(initial_state)
    response_text = final_state.get("draft_response", "系统未能生成任何回复。")
    intent = final_state.get("user_intent", "unknown")
    agent = final_state.get("next_agent", "unknown")
    print(f"[API 返回结果] Agent: {agent} | Response: {response_text}\n")
    return ChatResponse(
        response=response_text if response_text else "系统未能生成任何回复。",
        intent=intent,
        agent_used=agent
    )
