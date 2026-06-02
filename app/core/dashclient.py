import os
from dashvector import Client
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

# 初始化 OpenAI Embedding 模型 (用于把文本变成 1536 维的向量)
embeddings = OpenAIEmbeddings(
    model="tongyi-embedding-vision-flash-2026-03-06", 
    openai_api_key=settings.EMBEDDING_API_KEY,
    openai_api_base=settings.EMBEDDING_API_URL
)

# 初始化阿里云 DashVector 客户端
dash_client = Client(
    api_key=settings.DASHVECTOR_API_KEY,
    endpoint=settings.DASHVECTOR_ENDPOINT
)

COLLECTION_NAME = "edu_user_memory"

def save_long_term_memory(user_id: str, session_id: str, memory_text: str):
    """将一条记忆文本存入阿里云 DashVector 向量库"""
    try:
        collection = dash_client.get(COLLECTION_NAME)
        if not collection:
            print(f" [DashVector] 找不到集合 {COLLECTION_NAME}，请确保在控制台已创建！")
            return
            
        vector = embeddings.embed_query(memory_text)
        
        collection.insert({
            "vector": vector,
            "fields": {"user_id": user_id, "session_id": session_id, "text": memory_text}
        })
        print(f"[DashVector] 已为用户 {user_id} 存入长时记忆！")
    except Exception as e:
        print(f"[DashVector] 存储失败: {e}")

def search_long_term_memory(user_id: str, query: str, top_k: int = 2) -> str:
    """检索当前用户的专属长时记忆"""
    try:
        collection = dash_client.get(COLLECTION_NAME)
        vector = embeddings.embed_query(query)
        
        # 核心：过滤条件保证绝对不串号！
        docs = collection.query(
            vector=vector,
            filter=f"user_id = '{user_id}'",
            topk=top_k,
            output_fields=["text"]
        )
        memories = [doc.fields["text"] for doc in docs if doc.fields]
        return "\n".join(memories)
    except Exception as e:
        print(f"[DashVector] 检索失败: {e}")
        return ""
