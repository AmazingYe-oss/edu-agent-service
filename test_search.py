import sys
sys.path.insert(0, '.')

from app.tools.web_search import web_search

print("测试联网搜索...")
result = web_search.invoke({"query": "上海今天天气"})
print(f"搜索结果: {result}")
