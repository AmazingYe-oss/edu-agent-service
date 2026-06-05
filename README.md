# Edu Multi-Agent Service — 多智能体教育辅导系统

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi_Agent-000000?logo=langchain)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue?logo=kubernetes)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-对话历史-336791?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-会话缓存-dc382d?logo=redis)
![DashVector](https://img.shields.io/badge/DashVector-向量检索-00c4b4)
![CI/CD](https://img.shields.io/badge/CI-GitHub_Actions-green?logo=github-actions)
![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-orange?logo=argo)

## 项目简介

本项目是一个面向教育场景的 **多智能体（Multi-Agent）智能辅导系统**，基于 **LangGraph** 构建多 Agent 协作工作流，通过 8 个专业 AI Agent 协同工作，为学生提供个性化的智能辅导服务。

系统采用 **FastAPI** 微服务后端 + **Streamlit** 交互式前端，集成 **DashVector** 向量检索实现 RAG 增强，使用 **PostgreSQL** 持久化对话历史与用户画像，**Redis** 提供会话缓存与限流，通过 **Docker + Kubernetes + GitHub Actions + ArgoCD GitOps** 实现云原生交付。

> 核心定位：将传统教育中的知识讲解、出题测试、批改评分、错题解析等环节，交由多个专业 AI Agent 协作完成，实现真正意义上的个性化智能教学。

---

## 系统架构

```mermaid
flowchart TD
    User["用户输入"]
    Planner["Planner Agent<br/>教学总监：意图识别 & 路由"]
    Learner["Learner Agent<br/>私人教师：知识讲解"]
    Quizzler["Quizzler Agent<br/>出题考官：智能出题"]
    Scorer["Scorer Agent<br/>批改裁判：自动评分"]
    Explainer["Explainer Agent<br/>辅导教师：错题解析"]
    Chitchat["Chitchat Agent<br/>闲聊助手 + 联网搜索"]
    Critic["Critic Agent<br/>教导主任：质量审查"]
    Summarizer["Summarizer Agent<br/>总结节点：生成最终回复"]
    Response["返回用户"]
    Persist["异步持久化"]
    DB["PostgreSQL + DashVector"]

    User --> Planner
    Planner -->|"学习/出题/批改/解析"| Learner
    Planner -->|"出题"| Quizzler
    Planner -->|"批改"| Scorer
    Planner -->|"错题解析"| Explainer
    Planner -->|"闲聊"| Chitchat
    Learner --> Critic
    Quizzler --> Critic
    Scorer --> Critic
    Explainer --> Critic
    Critic -->|"通过"| Summarizer
    Critic -->|"打回重做"| Learner
    Chitchat -->|"直接输出"| Response
    Summarizer --> Response
    Summarizer -.->|"BackgroundTasks"| Persist
    Persist -.-> DB
```

### 核心数据流

1. 用户在 Streamlit 前端输入问题
2. FastAPI 后端接收请求，**Planner Agent** 分析意图并路由到对应 Agent
3. 教学类请求（学习/出题/批改/解析）经过专业 Agent 处理后，由 **Critic Agent** 审查质量
4. 审查通过后 **Summarizer Agent** 生成最终回复，通过 **SSE 流式输出** 返回用户
5. 闲聊类请求直接输出，支持 **阿里云百炼 MCP 联网搜索**
6. 响应返回后，**BackgroundTasks** 异步将学习数据写入 PostgreSQL 和 DashVector

### RESTful API 架构

系统采用 RESTful API 设计，路由模块化：
- `app/api/chat.py` — 聊天接口（SSE 流式输出）
- `app/services/nodes/` — 各 Agent 节点实现
- `app/services/graph.py` — LangGraph 工作流定义
- `app/models/` — Pydantic 请求/响应模型

---

## 核心特性

### 多智能体协作架构
- **LangGraph** 编排框架：Planner → 专业 Agent → Critic → Summarizer 的完整工作流
- **8 个专业 Agent**：Planner、Learner、Quizzler、Scorer、Explainer、Critic、Summarizer、Chitchat
- **智能意图识别**：自动分析学生需求，路由到最合适的教学节点
- **质量保证机制**：Critic Agent 审查教学内容，不合格可打回重做（最多 2 次）

### RAG 检索增强
- **DashVector** 向量数据库：基于阿里云 DashVector 实现语义检索
- **DashScope Embedding**（text-embedding-v3）：将知识片段转化为向量
- 确保知识讲解基于权威教材，而非模型幻觉

### 双层记忆系统
- **短时记忆**：PostgreSQL Checkpointer 自动保存对话历史
- **长时记忆**：DashVector 向量库存储用户画像和学习记录
- **异步持久化**：FastAPI BackgroundTasks 实现数据异步写入，不阻塞响应

### SSE 流式输出
- 基于 `astream_events` 实现逐字打字机效果
- 前端通过 SSE 实时渲染，体验流畅

### 通用闲聊 + 联网搜索
- 非学习场景的自然对话，直接输出不经过 Critic 审查
- 集成 **阿里云百炼 MCP WebSearch**，支持实时信息查询

---

## 项目结构

```
edu-agent-service/
├── app/
│   ├── api/
│   │   └── chat.py                  # Chat API (SSE 流式)
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
│   │   │   └── chitchat.py          # 闲聊 + 联网搜索
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
│   ├── components/                  # 页面组件
│   ├── pages/                       # Streamlit 页面
│   ├── utils/
│   │   ├── auth.py                  # 认证工具
│   │   └── api.py                   # API 调用工具
│   └── app.py                       # 前端入口
├── .github/workflows/
│   └── main.yml                     # CI/CD 流水线
├── Dockerfile                       # Docker 镜像构建
├── docker-compose.yml               # 本地容器编排
├── requirements.txt                 # Python 依赖清单
├── .env.example                     # 环境变量模板
└── .env                             # 实际环境变量（不入 Git）
```

> Kubernetes GitOps 配置（Deployment、Ingress、Service 等）维护在独立仓库 [edu-agent-service-gitops](https://github.com/AmazingYe-oss/edu-agent-service-gitops)。

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/AmazingYe-oss/edu-agent-service.git
cd edu-agent-service
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际配置：

```env
# LLM 配置
XIAOMI_API_KEY=your-llm-api-key
XIAOMI_BASE_URL=https://api.openai.com/v1
XIAOMI_MODEL=mimo-v2.5-pro

# RAG API 配置
RAG_API_BASE_URL=http://localhost:8000

# PostgreSQL 配置
POSTGRES_URL=postgresql://user:password@host:port/database

# Redis 配置
REDIS_URL=redis://:password@host:port/0

# DashVector 向量库配置
DASHVECTOR_API_KEY=your-api-key
DASHVECTOR_ENDPOINT=your-endpoint

# Embedding 配置
EMBEDDING_API_KEY=your-embedding-key
EMBEDDING_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 阿里云百炼 MCP 联网搜索
DASHSCOPE_API_KEY=your-dashscope-key
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python create_tables.py
```

### 5. 启动服务

```bash
# 启动后端（终端 1）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 启动前端（终端 2）
cd frontend
streamlit run app.py
```

### 6. 访问服务

- 前端界面：http://localhost:8501
- 后端 API 文档：http://localhost:8080/docs

---

## Docker Compose 本地部署

```bash
# 一键启动后端 + 前端
docker compose up --build -d

# 查看日志
docker logs edu_backend
docker logs edu_frontend
```

服务地址：
- 前端：http://localhost:8501
- 后端：http://localhost:8080/docs

---

## 云原生交付链路 (Cloud Native Delivery Workflow)

项目采用双仓 GitOps 架构，将业务代码仓与 Kubernetes 配置仓彻底解耦。

```mermaid
flowchart LR
    Dev["Developer Push Code"]
    CI["GitHub Actions"]
    Build["Docker Build"]
    ACR["Aliyun ACR"]
    GitOps["GitOps Config Repo"]
    ArgoCD["ArgoCD"]
    K8s["Kubernetes Cluster"]
    Pod["Agent Service Pods"]

    Dev --> CI
    CI --> Build
    Build --> ACR
    CI --> GitOps
    GitOps --> ArgoCD
    ArgoCD --> K8s
    K8s --> Pod
```

交付流程如下：

1. 开发者向业务代码仓库 Push 代码（main 分支）。
2. GitHub Actions 自动触发 CI 流水线。
3. CI 执行 Docker 镜像构建。
4. 镜像推送至阿里云 ACR（同时打 latest 和 commit SHA 标签）。
5. CI 自动修改 GitOps 配置仓库中的镜像 Tag。
6. ArgoCD 监听 GitOps 仓库变更。
7. ArgoCD 将期望状态同步到 Kubernetes 集群。
8. Kubernetes 执行滚动更新，完成服务发布。

### 详细部署步骤

#### 第零步：创建 Kubernetes 集群

**方式一：Docker Desktop（推荐本地开发）**

1. 打开 Docker Desktop → **Settings** → **Kubernetes**
2. 勾选 **Enable Kubernetes** → **Apply & Restart**
3. 验证：

```bash
kubectl cluster-info
kubectl get nodes
```

**方式二：minikube**

```bash
minikube start
kubectl cluster-info
```

**方式三：云厂商托管集群（生产环境）**

- 阿里云 ACK：https://www.aliyun.com/product/kubernetes
- 腾讯云 TKE：https://cloud.tencent.com/product/tke
- 华为云 CCE：https://www.huaweicloud.com/product/cce.html

#### 第一步：安装 ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s
```

#### 第二步：配置 GitHub Secrets

在仓库的 **Settings → Secrets and variables → Actions → Repository secrets** 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `ACR_USERNAME` | 阿里云 ACR 登录用户名 |
| `ACR_PASSWORD` | 阿里云 ACR 登录密码 |
| `GITOPS_TOKEN` | GitHub PAT（需要 `repo` 权限，用于跨仓库推送） |

#### 第三步：推送代码触发 CI

```bash
git add .
git commit -m "your commit message"
git push origin main
```

#### 第四步：创建 K8s Secret 和 ConfigMap

```bash
# 从 .env 文件创建 Secret
kubectl create secret generic edu-agent-service-secret \
  --from-env-file=.env \
  -n edu-agent-service-dev

# 创建 ACR 镜像拉取凭证
kubectl create secret docker-registry acr-credentials \
  --docker-server=crpi-he7mqvhihpnvi08o.cn-shanghai.personal.cr.aliyuncs.com \
  --docker-username=你的ACR用户名 \
  --docker-password=你的ACR密码 \
  -n edu-agent-service-dev
```

#### 第五步：部署 ArgoCD Application

```bash
kubectl apply -f https://raw.githubusercontent.com/AmazingYe-oss/edu-agent-service-gitops/main/argocd/application.yaml
```

#### 第六步：验证部署

```bash
kubectl get pods -n edu-agent-service-dev
kubectl get svc -n edu-agent-service-dev
kubectl get ingress -n edu-agent-service-dev
```

#### 第七步：访问服务

```bash
kubectl port-forward svc/edu-agent-service 8080:80 -n edu-agent-service-dev
# 访问 http://localhost:8080/docs
```

---

## Agent 角色说明

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

---

## 常见问题

**Q: 后端启动报 `DASHVECTOR_API_KEY` 未配置？**
A: 确保 `.env` 文件或 K8s Secret 中已正确配置 `DASHVECTOR_API_KEY` 和 `DASHVECTOR_ENDPOINT`。

**Q: PostgreSQL 连接失败？**
A: 检查 `POSTGRES_URL` 格式是否正确：`postgresql://用户名:密码@地址:端口/数据库名`。

**Q: Redis 连接失败？**
A: 检查 `REDIS_URL` 格式是否正确。本地开发可启动一个 Redis 容器：`docker run -d -p 6379:6379 redis`。

**Q: 后端 Pod 状态为 `ErrImagePull`？**
A: 需要创建 ACR 镜像拉取凭证，参考部署步骤第四步。

**Q: 后端 Pod 状态为 `CreateContainerConfigError`？**
A: 通常是 Secret 名称不是 `edu-agent-service-secret` 或缺少必要的环境变量。使用 `kubectl describe pod` 查看 Events。

**Q: Critic Agent 审查报 JSON 解析错误？**
A: LLM 返回的 JSON 包含非法转义字符，系统已内置容错处理，会自动降级通过。

---

## 适用场景

- **个性化智能教学辅导**（多 Agent 协作，覆盖学、练、测、评全链路）
- **智能出题与自动批改**（基于 RAG 检索的知识点精准出题）
- **错题解析与知识巩固**（针对性分析薄弱环节）
- **联网搜索增强的通用问答**（支持实时信息查询）
- **云原生 AI 应用工程化实践**
- **AI 应用 CI/CD 与 GitOps 交付演示**

---

## 作者

**朱伟业 (AmazingYe)**
- 2027 届 数据科学与大数据技术
- AWS Certified Solutions Architect - Professional
- 阿里云大模型 ACP 认证
- 寻求云计算 / 云原生 / DevOps / SRE / AI 工程化相关实习机会，欢迎联系交流！
