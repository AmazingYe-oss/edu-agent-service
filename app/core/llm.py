from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm():
    """
    初始化并返回一个 OpenAI LLM 实例
    """
    llm = ChatOpenAI(
        model=settings.XIAOMI_MODEL,
        api_key=settings.XIAOMI_API_KEY,
        base_url=settings.XIAOMI_BASE_URL,
        temperature=0.1,
        max_tokens=2048
    )
    return llm

def get_chat_model():
    llm = ChatOpenAI(
        model=settings.XIAOMI_MODEL,
        api_key=settings.XIAOMI_API_KEY,
        base_url=settings.XIAOMI_BASE_URL,
        temperature=0.3,
        max_tokens=2048
    )
    return llm

llm = get_chat_model()