import os
from dashvector import Client, Doc
from openai import OpenAI
from app.core.config import settings

# 初始化阿里云 DashScope Embedding 客户端
embedding_client = OpenAI(
    api_key=settings.EMBEDDING_API_KEY,
    base_url=settings.EMBEDDING_API_URL
)

def get_embedding(text: str) -> list:
    """获取文本的向量表示"""
    response = embedding_client.embeddings.create(
        model="text-embedding-v3",
        input=text,
        encoding_format="float"
    )
    return response.data[0].embedding

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
        
        vector = get_embedding(memory_text)
        print(f"[DashVector Debug] vector len: {len(vector)}, sample: {vector[:3]}")
        
        # 使用 Doc 对象插入
        ret = collection.insert(
            Doc(
                vector=vector,
                fields={"user_id": user_id, "session_id": session_id, "text": memory_text}
            )
        )
        if ret:
            print(f"[DashVector] 已为用户 {user_id} 存入长时记忆！")
        else:
            print(f"[DashVector] 存储失败: {ret}")
    except Exception as e:
        print(f"[DashVector] 存储失败: {e}")
        import traceback
        traceback.print_exc()

def search_long_term_memory(user_id: str, query: str, top_k: int = 2) -> str:
    """检索当前用户的专属长时记忆"""
    try:
        collection = dash_client.get(COLLECTION_NAME)
        if not collection:
            print(f"[DashVector] 找不到集合 {COLLECTION_NAME}")
            return ""
        
        vector = get_embedding(query)
        
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
