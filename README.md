# Bug Tracker - Bug 追踪系统

> 基于 FastAPI + Vue 3 + MySQL 的前后端分离 Bug 追踪平台，支持看板管理、Bug 追踪、团队协作、严重程度分级与数据看板。

---

## 项目简介

Bug Tracker 是一个轻量级的 Bug 追踪系统，类似简化版的 Jira。用户可以通过项目看板的方式管理 Bug，支持 Bug 的创建、分配、状态流转、评论沟通、关联 Bug，以及团队成员管理。

**核心特性：**
- 多项目管理，每个项目独立看板
- 四列看板视图（待办 / 进行中 / 审核中 / 已完成），支持拖拽排序
- Bug 字段：标题、描述、复现步骤、环境信息、优先级、严重程度（P1-P4）、关联 Commit
- Bug 双向关联：关联同一项目中的相关 Bug
- 搜索/筛选：支持按关键词、优先级、严重程度、负责人过滤
- Bug 评论区，支持团队讨论
- 附件上传/下载（支持图片/PDF/Word/ZIP，最大 10MB）
- 站内通知：Bug 被分配/评论/状态变更时自动通知相关人员
- 成员搜索与邀请
- 操作审计日志，记录关键变更
- 数据看板：状态/严重程度/优先级图表 + 成员工作量统计
- JWT 认证保护所有接口
- WebSocket 实时推送（可扩展）
- 自动生成的 OpenAPI 文档

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端框架** | FastAPI | 高性能异步 API 框架 |
| **ORM** | SQLAlchemy 2.0 | Python 最流行的 ORM |
| **数据库** | MySQL 8.0+ | 关系型数据存储 |
| **缓存** | Redis 6+ | 缓存 / 会话 / 实时推送 |
| **认证** | python-jose (JWT) | 无状态 Token 认证 |
| **实时通信** | WebSocket | 项目内实时消息广播 |
| **前端框架** | Vue 3 (Composition API) | 响应式 UI 框架 |
| **构建工具** | Vite 5 | 极速前端构建 |
| **状态管理** | Pinia | Vue 官方推荐状态管理 |
| **UI 组件库** | Element Plus | 企业级组件库 |
| **HTTP 客户端** | Axios | 请求拦截器 + 自动鉴权 |
| **图表库** | ECharts 5 | 数据可视化 |
| **拖拽库** | vuedraggable | 看板拖拽排序 |

---

## 项目结构

```
task-collab-platform/
├── backend/                          # FastAPI 后端
│   ├── main.py                       # 应用入口，CORS 配置，路由挂载
│   ├── config.py                     # Pydantic Settings，环境变量读取
│   ├── database.py                   # SQLAlchemy 引擎 + Session 工厂
│   ├── models.py                     # ORM 模型（10 张表）
│   ├── schemas.py                    # Pydantic 请求/响应模型
│   ├── auth.py                       # 密码哈希 + JWT 令牌生成/解析
│   ├── crud.py                       # 全部数据库操作（40+ 函数）
│   ├── dependencies.py               # FastAPI 依赖注入
│   ├── requirements.txt              # Python 依赖列表
│   ├── .env.example                  # 环境变量模板
│   ├── migrate.py                    # 数据库迁移脚本
│   ├── conftest.py                   # pytest 测试配置
│   ├── pytest.ini                    # pytest 配置文件
│   ├── tests/                        # 单元测试
│   │   ├── test_auth.py              # 认证测试
│   │   └── test_crud.py              # CRUD 测试
│   └── routers/                      # API 路由模块
│       ├── auth.py                   # 认证模块（注册/登录/搜索）
│       ├── projects.py               # 项目管理 + 成员管理
│       ├── tasks.py                  # Bug CRUD + 关联 + 我的 Bug
│       ├── comments.py               # 评论管理
│       ├── tags.py                   # 标签管理
│       ├── attachments.py            # 附件上传/下载
│       ├── dashboard.py              # 数据看板 + 审计日志 + 通知
│       └── websocket.py              # WebSocket 实时推送
│
├── frontend/                         # Vue 3 前端
│   ├── index.html                    # 入口 HTML
│   ├── package.json                  # Node.js 依赖
│   ├── vite.config.js                # Vite 配置（代理到后端）
│   └── src/
│       ├── main.js                   # Vue 应用初始化
│       ├── App.vue                   # 根组件
│       ├── api/index.js              # Axios 实例 + 拦截器
│       ├── router/index.js           # Vue Router + 登录守卫
│       ├── stores/
│       │   ├── auth.js               # 认证状态
│       │   └── project.js            # 项目/Bug/评论/通知/附件
│       └── views/
│           ├── Login.vue             # 登录页
│           ├── Register.vue          # 注册页
│           ├── Layout.vue            # 主布局（侧边栏 + 通知铃铛）
│           ├── Dashboard.vue         # 项目列表 + 新建项目
│           ├── ProjectBoard.vue      # 看板视图 + 搜索/筛选 + Bug 详情
│           └── ProjectDashboard.vue  # 数据看板（ECharts 图表）
│
├── database/
│   └── init.sql                      # MySQL 建表脚本（10 张表）
│
└── README.md                         # 本文档
```

---

## 数据库设计

### 表结构总览

| 表名 | 说明 |
|------|------|
| `users` | 用户表 |
| `projects` | 项目表 |
| `project_members` | 项目成员表 |
| `tasks` | Bug 表（含复现步骤/环境/严重程度/关联 Commit/关联 Bug ID） |
| `comments` | 评论表 |
| `tags` | 标签表 |
| `task_tags` | Bug-标签关联表 |
| `attachments` | 附件表 |
| `audit_logs` | 审计日志表 |
| `notifications` | 通知表 |

---

## 快速开始

### 环境要求

| 软件 | 最低版本 | 推荐版本 |
|------|----------|----------|
| Python | 3.10 | 3.12+ |
| Node.js | 18 | 20+ |
| MySQL | 8.0 | 8.0+ |
| Redis | 6.0 | 7.0+ |

### 第一步：初始化数据库

```bash
mysql -u root -p < database/init.sql
```

### 第二步：启动 Redis

```bash
redis-server
```

### 第三步：启动后端

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，修改数据库连接信息
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

### 第四步：启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

---

## API 接口一览

### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录，返回 Token |
| GET | `/api/auth/me` | 获取当前用户信息 |
| GET | `/api/auth/search` | 搜索用户 |

### 项目模块 `/api/projects`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects` | 获取我的项目列表 |
| GET | `/api/projects/{id}` | 获取项目详情 |
| PUT | `/api/projects/{id}` | 更新项目 |
| DELETE | `/api/projects/{id}` | 删除项目 |
| GET | `/api/projects/{id}/members` | 获取项目成员 |
| POST | `/api/projects/{id}/members/{user_id}` | 添加成员 |
| DELETE | `/api/projects/{id}/members/{user_id}` | 移除成员 |
| GET | `/api/projects/{id}/dashboard` | 数据看板 |
| GET | `/api/projects/{id}/audit` | 审计日志 |

### Bug 模块 `/api/tasks`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/project/{id}` | 获取项目下所有 Bug |
| GET | `/api/tasks/mine` | 获取分配给我的 Bug |
| POST | `/api/tasks` | 创建 Bug |
| GET | `/api/tasks/{id}` | 获取 Bug 详情 |
| PUT | `/api/tasks/{id}` | 更新 Bug |
| DELETE | `/api/tasks/{id}` | 删除 Bug |
| GET | `/api/tasks/{id}/related` | 获取关联 Bug |
| POST | `/api/tasks/{id}/link` | 关联两个 Bug（双向） |
| DELETE | `/api/tasks/{id}/link/{target_id}` | 解除关联 |

### 评论模块 `/api/comments`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/comments/task/{id}` | 获取评论列表 |
| POST | `/api/comments` | 发表评论 |
| DELETE | `/api/comments/{id}` | 删除评论 |

### 标签模块 `/api/tags`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tags/project/{id}` | 获取项目标签 |
| POST | `/api/tags/project/{id}` | 创建标签 |
| POST | `/api/tags/{task_id}/{tag_id}` | 给 Bug 打标签 |
| DELETE | `/api/tags/{task_id}/{tag_id}` | 移除标签 |

### 附件模块 `/api/attachments`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/attachments/task/{id}` | 上传附件 |
| GET | `/api/attachments/task/{id}` | 获取附件列表 |
| DELETE | `/api/attachments/{id}` | 删除附件 |
| GET | `/api/attachments/files/{filename}` | 下载附件 |

### 通知模块 `/api/notifications`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/notifications` | 获取通知列表 |
| GET | `/api/notifications/unread` | 获取未读计数 |
| POST | `/api/notifications/{id}/read` | 标记已读 |
| POST | `/api/notifications/read-all` | 全部标记已读 |

### WebSocket

| 路径 | 说明 |
|------|------|
| `WS /ws/{project_id}` | 加入项目 WebSocket 频道 |

---

## 后续扩展方向

- [ ] **子任务拆分** — 复杂 Bug 可拆为多个子步骤
- [ ] **邮件/钉钉通知** — 重要 Bug 变更时推送
- [ ] **Git 集成** — 自动关联 commit/PR，自动更新状态
- [ ] **搜索/全文检索** — 支持按描述内容搜索
- [ ] **自定义工作流** — 项目可自定义状态列
- [ ] **数据导出** — Excel/CSV 导出 Bug 列表
- [ ] **多语言** — 国际化支持

---

## License

MIT
