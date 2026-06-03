# Streamlit 前端应用

## 启动方式

```bash
# 进入 frontend 目录
cd frontend

# 启动 Streamlit 应用
streamlit run app.py
```

默认访问地址: http://localhost:8501

## 功能说明

### 1. 登录/注册
- 用户名至少 3 位
- 密码至少 6 位
- 简单的本地验证（实际项目应连接后端 API）

### 2. 智能对话
- 类似 ChatGPT 的聊天界面
- 支持流式输出
- 自动识别意图（学习/出题/批改/解析）

### 3. 文件上传
- 支持批量上传
- 支持格式：PDF、Word、TXT、Markdown
- 调用后端 `/api/v1/documents/batch` 接口

### 4. 学习记录
- 学习统计概览
- 错题本查看
- 知识图谱（开发中）

## 目录结构

```
frontend/
├── app.py              # 主应用入口
├── pages/
│   ├── __init__.py
│   ├── chat.py         # 聊天页面
│   ├── upload.py       # 文件上传页面
│   └── records.py      # 学习记录页面
├── utils/
│   ├── __init__.py
│   ├── api.py          # API 调用工具
│   └── auth.py         # 认证工具
└── README.md           # 本文件
```

## 配置说明

API 基础地址在 `utils/api.py` 中配置：

```python
API_BASE_URL = "http://localhost:8080"
```

## 注意事项

1. 确保后端服务已启动（默认 8080 端口）
2. 文件上传功能需要后端实现 `/api/v1/documents/batch` 接口
3. 登录/注册功能目前为简单验证，生产环境应连接数据库
