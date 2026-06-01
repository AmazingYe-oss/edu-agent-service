from fastapi import FastAPI
from app.api.v1 import chat

app = FastAPI(
    title="Edu Agent Service",
    description="基于 LangGraph 的教育智能代理服务",
    version="1.0.0"
)

# 注册路由
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Edu Agent Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
