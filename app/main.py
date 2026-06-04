from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import chat, auth, session
import uvicorn

app = FastAPI(
    title="Edu Multi-Agent API",
    description="基于 LangGraph 的多智能体教育系统大脑",
    version="1.0.0"
)

# CORS 配置（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(session.router, prefix="/api/v1", tags=["Session"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to Edu Multi-Agent Service! 请访问 /docs 查看接口文档。"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
