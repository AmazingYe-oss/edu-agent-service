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
│  Planner    │ → 教学总监：分析意图，决定路由
└─────────────┘
    ↓ (意图路由)
┌─────────────────────────────────────────────────────────────────┐
│                                                             │
↓        ↓        ↓        ↓        ↓                     │
┌──────┐┌──────┐┌──────┐┌──────┐┌──────────────┐             │
│Learner││Quiz- ││Score ││Explain││  Chitchat    │             │
│(私教) ││ler   ││r     ││er    ││ (闲聊)       │             │
│     ││(考官) ││(裁判) ││(辅导) ││ +联网搜索     │             │
└──────┘└──────┘└──────┘└──────┘└──────────────┘             │
│   ↓ (教学节点经过审查)                  ↓ (直接输出)           │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────┐
│  Critic     │ → 教导主任：质量检查（可打回重做）
└─────────────┘
    ↓
┌─────────────┐
│Summarizer   │ → 总结节点：生成最终回复
└─────────────┘
    ↓ (同步返回响应)
    ↓ (异步后台持久化)
┌─────────────────────────────────────────────────────────────────┐
│ BackgroundTasks → PostgreSQL + DashVector (异步数据沉淀)    │
└─────────────────────────────────────────────────────────────────┘
```

## Agent 角色

| Agent | 角色 | 职责 | 使用工具 |
|-------|------|------|----------|
| Planner | 教学总监 | 意图识别、任务路由 | 无 |
| Learner | 私人教师 | 知识讲解、概念解释 | RAG 检索、数据库 |
| Quizzler | 出题考官 | 智能出题、题目生成 | RAG 检索、数据库 |
| Scorer | 批改裁判 | 自动批改、评分反馈 | 数据库 |
| Explainer | 辅导教师 | 错题解析、知识点巩固 | RAG 检索、数据库 |
| Critic | 教导主任 | 内容质量审查 | 无 |
| Summarizer | 总结助手 | 生成最终教学回复 | 无 |
| Chitchat | 闲聊助手 | 通用对话、联网搜索 | 联网搜索（MCP） |

## 项目结构

```
edu-agent-service/
├── app/
│   ├── api/
│   │   └── chat.py                  # Chat API
│   ├── core/
│   │   ├── config.py                # 配置管理
│   │   ├── database.py              # 数据库连接
│   │   ├── dashclient.py            # DashVector 客户端
│   │   └── llm.py                   # LLM 初始化
│   ├── models/
│   │   ├── domain.py                # 数据库模型
│   │   └── schemas.py               # Pydantic 模型
│   ├── services/
│   │   ├── nodes/
│   │   │   ├── planner.py           # 意图识别与路由
│   │   │   ├── learner.py           # 知识讲解
│   │   │   ├── quizzler.py          # 智能出题
│   │   │   ├── scorer.py            # 自动批改
│   │   │   ├── explainer.py         # 错题解析
│   │   │   ├── critic.py            # 质量审查
│   │   │   ├── summarizer.py        # 总结回复
│   │   │   └── chitchat.py          # 闲聊对话 + 联网搜索
│   │   ├── async_persistence.py     # 异步持久化服务
│   │   ├── graph.py                 # LangGraph 工作流定义
│   │   └── state.py                 # 状态定义
│   ├── tools/
│   │   ├── database.py              # 数据库工具
│   │   ├── rag.py                   # RAG 工具
│   │   ├── rag_search.py            # RAG 搜索工具
│   │   └── web_search.py            # 联网搜索工具 (MCP)
│   └── main.py                      # 应用入口
├── frontend/
│   ├── pages/                       # Streamlit 页面
│   ├── utils/                       # 工具函数
│   └── app.py                       # 前端入口
├── .github/workflows/
│   └── main.yml                     # CI/CD 流水线
├── .env.example                     # 环境变量示例
├── Dockerfile                       # Docker 镜像构建
├── requirements.txt                 # 依赖列表
└── README.md                        # 项目文档
```

---

## 前置条件

### 本地开发

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.9+ | 运行环境 |
| PostgreSQL | 12+ | 对话历史、用户数据存储 |
| DashVector | - | 阿里云向量数据库（RAG 检索） |
| OpenAI 兼容 LLM | - | GPT-4 或其他兼容 API |
| 阿里云百炼 API | - | 联网搜索能力（可选） |

### CI/CD 与部署

| 依赖 | 说明 |
|------|------|
| GitHub 仓库 | 代码托管与 CI/CD 触发 |
| 阿里云容器镜像服务 (ACR) | 镜像存储 |
| Kubernetes 集群 | 应用运行环境 |
| ArgoCD | GitOps 持续部署 |
| GitOps 配置仓 | [edu-agent-service-gitops](https://github.com/AmazingYe-oss/edu-agent-service-gitops) |

---

## 快速开始（本地开发）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# LLM 配置
OPENAI_API_KEY=your-llm-api-key
OPENAI_API_BASE=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4-turbo

# RAG API 配置
RAG_API_BASE_URL=http://localhost:8000

# 数据库配置
POSTGRES_URL=postgresql://user:password@host:port/database

# Redis 配置
REDIS_URL=redis://:password@host:port/0

# 向量数据库配置
DASHVECTOR_API_KEY=your-api-key
DASHVECTOR_ENDPOINT=your-endpoint

# 阿里云百炼 MCP 联网搜索
DASHSCOPE_API_KEY=your-dashscope-api-key
```

### 3. 初始化数据库

```bash
python create_tables.py
```

### 4. 启动服务

```bash
# 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 启动前端（新终端）
cd frontend
streamlit run app.py
```

### 5. 访问服务

- 后端 API 文档：http://localhost:8080/docs
- 前端界面：http://localhost:8501

---

## 部署方式

本项目采用 **GitHub Actions + 阿里云 ACR + ArgoCD GitOps** 的自动化部署流水线。

### 整体流程

```
代码推送 (main)
    ↓
GitHub Actions 触发
    ↓
构建 Docker 镜像
    ↓
推送至阿里云 ACR
    ↓
更新 GitOps 仓库镜像 Tag
    ↓
ArgoCD 检测到变更
    ↓
自动同步至 Kubernetes 集群
```

### 详细部署步骤

#### 第一步：配置 GitHub Secrets

在仓库的 **Settings → Secrets and variables → Actions → Repository secrets** 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `ACR_USERNAME` | 阿里云 ACR 登录用户名 |
| `ACR_PASSWORD` | 阿里云 ACR 登录密码 |
| `GITOPS_TOKEN` | GitHub PAT（需要 `repo` 权限，用于跨仓库推送） |

> ACR_REGISTRY、ACR_NAMESPACE、ACR_REPO 已在工作流文件中硬编码，无需额外配置。

#### 第二步：推送代码触发 CI

```bash
git add .
git commit -m "your commit message"
git push origin main
```

GitHub Actions 会自动执行：
1. 拉取代码
2. 构建 Docker 镜像
3. 登录阿里云 ACR
4. 推送镜像（Tag 为 8 位 commit SHA + 分支名）
5. 更新 GitOps 仓库 `kustomization.yaml` 中的镜像 Tag

#### 第三步：部署 ArgoCD Application

在 Kubernetes 集群中应用 ArgoCD 配置：

```bash
kubectl apply -f https://raw.githubusercontent.com/AmazingYe-oss/edu-agent-service-gitops/main/argocd/application.yaml
```

ArgoCD 会自动：
- 监控 GitOps 仓库的 `base/` 目录
- 检测到镜像 Tag 变更后自动同步
- 创建命名空间 `edu-agent-service-dev`
- 部署 Deployment、Service、Ingress 等资源

#### 第四步：验证部署

```bash
# 查看 Pod 状态
kubectl get pods -n edu-agent-service-dev

# 查看 Service
kubectl get svc -n edu-agent-service-dev

# 查看 Ingress
kubectl get ingress -n edu-agent-service-dev

# 查看 ArgoCD 同步状态
argocd app get edu-agent-service
```

---

## CI/CD 配置说明

### GitHub Actions 工作流

文件位置：`.github/workflows/main.yml`

**触发条件：**
- 推送到 `main`、`master`、`release/*` 分支
- 手动触发（workflow_dispatch）

**镜像标签策略：**
- `<8位commit SHA>`：每次构建唯一标识
- `<分支名>`：分支级标识
- `latest`：仅 main/master 分支

**镜像地址格式：**
```
crpi-he7mqvhihpnvi08o.cn-shanghai.personal.cr.aliyuncs.com/edu-agent-project/edu-agent-service:<tag>
```

### GitOps 配置仓

配置仓地址：[edu-agent-service-gitops](https://github.com/AmazingYe-oss/edu-agent-service-gitops)

CI 流水线会自动更新 `base/kustomization.yaml` 中的镜像 Tag，ArgoCD 检测到变更后自动同步到集群。

---

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

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。
