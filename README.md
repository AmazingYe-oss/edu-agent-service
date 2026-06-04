# Edu Multi-Agent Service

基于 **LangGraph** 的多智能体教育系统，通过多个专业 AI Agent 协作，为学生提供个性化的智能辅导服务。

## 核心特性

- **多智能体协作架构**：8 个专业 Agent 各司其职，协同完成教学任务
- **智能意图识别**：自动分析学生需求，路由到最合适的教学节点
- **RAG 检索增强**：集成向量数据库，确保知识讲解基于权威教材
- **个性化学习**：学生画像、错题本、知识掌握度追踪
- **质量保证机制**：教导主任 Agent 审查内容，确保输出质量
- **双层记忆系统**：
  - 短时记忆：PostgreSQL Checkpointer 自动保存对话历史
  - 长时记忆：DashVector 向量库存储用户画像和学习记录
- **异步持久化**：使用 FastAPI BackgroundTasks 实现数据异步写入，提升响应速度
- **通用闲聊模式**：支持非学习场景的自然对话，直接输出不经过审查
- **联网搜索**：集成阿里云百炼 MCP 联网搜索，支持实时信息查询

## 系统架构

```
用户输入
    ↓
┌─────────────┐
│  Planner    │  ← 教学总监：分析意图，决定路由
└─────────────┘
    ↓ (意图路由)
┌──────────────────────────────────────────────────────────────┐
│                                                              │
↓         ↓         ↓         ↓         ↓                      │
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐              │
│Learner│ │Quiz- │ │Score │ │Explain│ │ Chitchat │              │
│(私教) │ │zler  │ │r     │ │er    │ │ (闲聊)   │              │
│      │ │(考官) │ │(裁判) │ │(辅导) │ │ +联网搜索│              │
└──────┘ └──────┘ └──────┘ └──────┘ └──────────┘              │
│    ↓ (教学节点经过审查)                  ↓ (直接输出)           │
└──────────────────────────────────────────────────────────────┘
    ↓
┌─────────────┐
│   Critic    │  ← 教导主任：质量审查（可打回重做）
└─────────────┘
    ↓
┌─────────────┐
│ Summarizer  │  ← 总结节点：生成最终回复
└─────────────┘
    ↓ (同步返回响应)
    ↓ (异步后台持久化)
┌─────────────────────────────────────────────────────────────┐
│  BackgroundTasks → PostgreSQL + DashVector (异步数据沉淀)    │
└─────────────────────────────────────────────────────────────┘
```

## Agent 角色说明

| Agent | 角色 | 职责 | 使用工具 |
|-------|------|------|----------|
| **Planner** | 教学总监 | 分析用户意图，决定路由策略 | `get_user_profile_tool`, `search_user_memory_tool` |
| **Learner** | 金牌私教 | 讲解知识点，提供学习指导 | `search_knowledge_base` |
| **Quizzler** | 出题官 | 根据学生弱点智能出题 | `check_error_book_tool` |
| **Scorer** | 阅卷裁判 | 批改作业，判定对错 | `search_knowledge_base` |
| **Explainer** | 特级辅导老师 | 深入解析错题，提供解题思路 | `search_knowledge_base`, `check_error_book_tool` |
| **Critic** | 教导主任 | 审查内容质量，可打回重做 | 结构化输出 |
| **Summarizer** | 总结官 | 整合审查结果，生成最终回复 | 无 |
| **Chitchat** | 闲聊伙伴 | 通用对话，支持联网搜索 | `web_search` (阿里云百炼 MCP) |

## 记忆系统

### 短时记忆 (PostgreSQL Checkpointer)
- 使用 LangGraph 的 `AsyncPostgresSaver` 自动保存对话历史
- 基于 `thread_id`（即 `session_id`）自动恢复上下文
- 支持多轮对话的连贯性

### 长时记忆 (DashVector)
- 用户画像：学习偏好、知识水平
- 学习记录：已学知识点、错题记录
- 闲聊记忆：用户个人信息（如姓名、兴趣）

### 记忆保存流程
```
对话结束
    ↓
异步持久化服务 (BackgroundTasks)
    ↓
┌─────────────────────────────────────┐
│ 1. 噪音过滤：拦截无价值对话          │
│ 2. LLM 提炼：提取事实性记忆          │
│ 3. 向量化：text-embedding-v3 (1024维)│
│ 4. 存储：DashVector 向量库           │
└─────────────────────────────────────┘
```

## 联网搜索

集成阿里云百炼 MCP 联网搜索服务，支持实时信息查询：

- **天气查询**：今天上海天气怎么样？
- **新闻资讯**：最新的科技新闻
- **实时信息**：股票价格、比赛结果等

### 配置

在 `.env` 中添加：
```env
DASHSCOPE_API_KEY=your-dashscope-api-key
```

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| AI 框架 | LangChain + LangGraph |
| 大语言模型 | OpenAI 兼容 API |
| 向量数据库 | DashVector (阿里云) |
| 关系型数据库 | PostgreSQL (阿里云 RDS) |
| 短时记忆 | PostgreSQL Checkpointer |
| 联网搜索 | 阿里云百炼 MCP WebSearch |
| Embedding | text-embedding-v3 (1024维) |
| ORM | SQLAlchemy 2.0 |
| 前端 | Streamlit |

## 项目结构

```
edu-agent-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # 用户认证 API
│   │       └── chat.py          # 聊天 API
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── dashclient.py        # DashVector 客户端
│   │   └── llm.py               # LLM 初始化
│   ├── models/
│   │   ├── domain.py            # 数据库模型
│   │   └── schemas.py           # Pydantic 模型
│   ├── services/
│   │   ├── nodes/
│   │   │   ├── planner.py       # 意图识别与路由
│   │   │   ├── learner.py       # 知识讲解
│   │   │   ├── quizzler.py      # 智能出题
│   │   │   ├── scorer.py        # 自动批改
│   │   │   ├── explainer.py     # 错题解析
│   │   │   ├── critic.py        # 质量审查
│   │   │   ├── summarizer.py    # 总结回复
│   │   │   └── chitchat.py      # 闲聊对话 + 联网搜索
│   │   ├── async_persistence.py # 异步持久化服务
│   │   ├── graph.py             # LangGraph 工作流定义
│   │   └── state.py             # 状态定义
│   ├── tools/
│   │   ├── database.py          # 数据库工具
│   │   ├── rag.py               # RAG 工具
│   │   ├── rag_search.py        # RAG 搜索工具
│   │   └── web_search.py        # 联网搜索工具 (MCP)
│   └── main.py                  # 应用入口
├── frontend/
│   ├── pages/                   # Streamlit 页面
│   ├── utils/                   # 工具函数
│   └── app.py                   # 前端入口
├── .env.example                 # 环境变量示例
├── requirements.txt             # 依赖列表
└── README.md                    # 项目文档
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.9+，并准备好以下服务：
- PostgreSQL 数据库
- DashVector 向量数据库（阿里云）
- OpenAI 兼容的 LLM API
- 阿里云百炼 API Key（用于联网搜索）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境变量示例文件并填入实际配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下内容：

```env
# LLM 配置
XIAOMI_API_KEY=your-llm-api-key
XIAOMI_BASE_URL=https://api.openai.com/v1
XIAOMI_MODEL=gpt-4-turbo

# RAG API 配置
RAG_API_BASE_URL=http://localhost:8000

# 数据库配置
POSTGRES_URL=postgresql://user:password@host:port/database

# 向量数据库配置
DASHVECTOR_API_KEY=your-api-key
DASHVECTOR_ENDPOINT=your-endpoint
EMBEDDING_API_KEY=your-embedding-api-key
EMBEDDING_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 阿里云百炼 MCP 联网搜索
DASHSCOPE_API_KEY=your-dashscope-api-key
```

### 4. 初始化数据库

```bash
python create_tables.py
```

### 5. 启动服务

```bash
# 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 启动前端（新终端）
cd frontend
streamlit run app.py
```

### 6. 访问服务

- 后端 API 文档：http://localhost:8080/docs
- 前端界面：http://localhost:8501

## API 接口

### 聊天接口

**POST** `/api/v1/chat`

请求体：
```json
{
  "message": "请帮我讲解一下牛顿第二定律",
  "user_id": "user_123",
  "session_id": "sess_456"
}
```

响应：SSE 流式输出

### 会话管理

**GET** `/api/v1/sessions?user_id=user_123`

获取用户的会话列表

## 工作流程

1. **意图识别**：Planner Agent 分析用户输入，识别意图（学习/出题/批改/解析/闲聊）
2. **路由分发**：根据意图将请求路由到对应的 Agent
3. **任务执行**：
   - 教学类意图（learn/quiz/score/explain）→ 经过 Critic 审查 → Summarizer 总结
   - 闲聊类意图（chitchat）→ 直接输出，不经过审查，支持联网搜索
4. **质量审查**：Critic Agent 审查教学类内容质量，不合格可打回重做（最多 2 次）
5. **异步持久化**：响应返回后，BackgroundTasks 异步将学习数据保存到 PostgreSQL 和 DashVector

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。
