# Edu Multi-Agent Service

基于 **LangGraph** 的多智能体教育系统，通过多个专业 AI Agent 协作，为学生提供个性化的智能辅导服务。

## 核心特性

- **多智能体协作架构**：7 个专业 Agent 各司其职，协同完成教学任务
- **智能意图识别**：自动分析学生需求，路由到最合适的教学节点
- **RAG 检索增强**：集成向量数据库，确保知识讲解基于权威教材
- **个性化学习**：学生画像、错题本、知识掌握度追踪
- **质量保证机制**：教导主任 Agent 审查内容，确保输出质量
- **长期记忆系统**：Redis + PostgreSQL + DashVector 三层存储架构
- **异步持久化**：使用 FastAPI BackgroundTasks 实现数据异步写入，提升响应速度

## 系统架构

```
用户输入
    ↓
┌─────────────┐
│  Planner    │  ← 教学总监：分析意图，决定路由
└─────────────┘
    ↓ (意图路由)
┌─────────────────────────────────────────────────────┐
│                                                     │
↓         ↓         ↓         ↓                       │
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                  │
│Learner│ │Quiz- │ │Score │ │Explain│                 │
│(私教) │ │zler  │ │r     │ │er    │                  │
│      │ │(考官) │ │(裁判) │ │(辅导) │                  │
└──────┘ └──────┘ └──────┘ └──────┘                  │
│                                                     │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────┐
│   Critic    │  ← 教导主任：质量审查（可打回重做）
└─────────────┘
    ↓ (同步返回响应)
    ↓ (异步后台持久化)
┌─────────────────────────────────────┐
│  BackgroundTasks → PostgreSQL +     │
│  DashVector (异步数据沉淀)           │
└─────────────────────────────────────┘
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

## 技术栈

- **Web 框架**：FastAPI + Uvicorn
- **AI 框架**：LangChain + LangGraph
- **大语言模型**：支持 OpenAI 兼容 API（可切换为国产模型）
- **向量数据库**：DashVector（阿里云）
- **关系型数据库**：PostgreSQL（阿里云 RDS）
- **缓存/状态存储**：Redis（阿里云）
- **ORM**：SQLAlchemy 2.0

## 项目结构

```
edu-agent-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── chat.py          # API 路由定义
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
│   │   │   └── critic.py        # 质量审查
│   │   ├── async_persistence.py # 异步持久化服务
│   │   ├── graph.py             # LangGraph 工作流定义
│   │   └── state.py             # 状态定义
│   ├── tools/
│   │   ├── database.py          # 数据库工具
│   │   ├── rag.py               # RAG 工具
│   │   └── rag_search.py        # RAG 搜索工具
│   └── main.py                  # 应用入口
├── .env.example                 # 环境变量示例
├── requirements.txt             # 依赖列表
└── README.md                    # 项目文档
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.9+，并准备好以下服务：
- PostgreSQL 数据库
- Redis 服务
- DashVector 向量数据库（阿里云）
- OpenAI 兼容的 LLM API

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
OPENAI_API_KEY="your-llm-api-key"
OPENAI_API_BASE="https://api.openai.com/v1"
LLM_MODEL_NAME="gpt-4-turbo"

# RAG API 配置
RAG_API_BASE_URL="http://localhost:8000"

# 数据库配置
POSTGRES_URL="postgresql://user:password@host:port/database"
REDIS_URL="redis://:password@host:port/db"

# 向量数据库配置
DASHVECTOR_API_KEY="your-api-key"
DASHVECTOR_ENDPOINT="your-endpoint"
```

### 4. 启动服务

```bash
# 开发模式（自动重载）
python -m app.main

# 或者使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 5. 访问 API 文档

启动后访问：http://localhost:8080/docs

## API 接口

### 聊天接口

**POST** `/api/v1/chat`

请求体：
```json
{
  "message": "请帮我讲解一下牛顿第二定律",
  "session_id": "optional-session-id"
}
```

响应：
```json
{
  "response": "牛顿第二定律是...",
  "intent": "learn",
  "agent_used": "learner_node"
}
```

## 工作流程

1. **意图识别**：Planner Agent 分析用户输入，识别意图（学习/出题/批改/解析）
2. **路由分发**：根据意图将请求路由到对应的 Agent
3. **任务执行**：目标 Agent 执行具体任务，可能调用 RAG 或数据库工具
4. **质量审查**：Critic Agent 审查输出质量，不合格可打回重做（最多 2 次）
5. **异步持久化**：响应返回后，BackgroundTasks 异步将学习数据保存到 PostgreSQL 和 DashVector

## 数据模型

### 用户画像 (UserProfile)
- `user_id`: 用户唯一标识
- `knowledge_state`: JSONB 格式的知识点掌握度
- `learning_style`: 学习风格

### 错题本 (ErrorBook)
- `user_id`: 用户 ID
- `knowledge_point`: 知识点
- `question_content`: 题目内容
- `user_answer`: 用户答案
- `ai_analysis`: AI 分析

## 配置说明

所有配置通过环境变量管理，详见 `app/core/config.py`：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | LLM API 密钥 | `sk-xxx` |
| `OPENAI_API_BASE` | LLM API 地址 | `https://api.openai.com/v1` |
| `LLM_MODEL_NAME` | 模型名称 | `gpt-4-turbo` |
| `RAG_API_BASE_URL` | RAG 服务地址 | `http://localhost:8000` |
| `POSTGRES_URL` | PostgreSQL 连接串 | `postgresql://...` |
| `REDIS_URL` | Redis 连接串 | `redis://...` |
| `DASHVECTOR_API_KEY` | DashVector API 密钥 | - |
| `DASHVECTOR_ENDPOINT` | DashVector 端点 | - |

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。
