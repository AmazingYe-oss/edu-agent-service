from fastapi import FastAPI
from app.api.v1 import chat
import uvicorn

app = FastAPI(
    title="Edu Multi-Agent API",
    description="基于 LangGraph 的多智能体教育系统大脑",
    version="1.0.0"
)

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to Edu Multi-Agent Service! 请访问 /docs 查看接口文档。"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
