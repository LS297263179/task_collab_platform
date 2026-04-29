# Task Collab - 任务协作平台

> 基于 FastAPI + Vue 3 + MySQL + Redis 的前后端分离任务管理平台，支持多项目看板、实时协作、任务分配与评论。

---

## 项目简介

Task Collab 是一个轻量级的任务协作平台，类似简化版的 Jira/Trello。用户可以通过项目看板的方式管理任务，支持任务的创建、分配、状态流转、评论沟通，以及团队成员管理。

**核心特性：**
- 多项目管理，每个项目独立看板
- 四列看板视图（待办 / 进行中 / 审核中 / 已完成）
- 任务优先级（低/中/高/紧急）与截止日期
- 任务评论区，支持团队讨论
- 成员搜索与邀请
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

---

## 项目结构

```
task-collab-platform/
├── backend/                          # FastAPI 后端
│   ├── main.py                       # 应用入口，CORS 配置，路由挂载
│   ├── config.py                     # Pydantic Settings，环境变量读取
│   ├── database.py                   # SQLAlchemy 引擎 + Session 工厂
│   ├── models.py                     # 6 个 ORM 模型
│   ├── schemas.py                    # Pydantic 请求/响应模型
│   ├── auth.py                       # 密码哈希 + JWT 令牌生成/解析
│   ├── crud.py                       # 全部数据库操作（30+ 函数）
│   ├── dependencies.py               # FastAPI 依赖注入（当前用户获取）
│   ├── requirements.txt              # Python 依赖列表
│   ├── .env.example                  # 环境变量模板
│   └── routers/                      # API 路由模块
│       ├── auth.py                   # POST /api/auth/register
│       │                             # POST /api/auth/login
│       │                             # GET  /api/auth/me
│       │                             # GET  /api/auth/search
│       ├── projects.py               # CRUD /api/projects
│       │                             # 成员管理 /api/projects/{id}/members
│       ├── tasks.py                  # CRUD /api/tasks
│       │                             # 我的任务 GET /api/tasks/mine
│       ├── comments.py               # CRUD /api/comments
│       ├── tags.py                   # 标签 CRUD + 任务关联
│       └── websocket.py              # WS /ws/{project_id}
│
├── frontend/                         # Vue 3 前端
│   ├── index.html                    # 入口 HTML
│   ├── package.json                  # Node.js 依赖
│   ├── vite.config.js                # Vite 配置（代理到后端）
│   └── src/
│       ├── main.js                   # Vue 应用初始化，注册 Pinia/Router/ElementPlus
│       ├── App.vue                   # 根组件
│       ├── api/index.js              # Axios 实例 + 请求/响应拦截器
│       ├── router/index.js           # Vue Router 路由配置 + 登录守卫
│       ├── stores/
│       │   ├── auth.js               # 认证状态（登录/注册/登出）
│       │   └── project.js            # 项目/任务/评论/成员全部操作
│       └── views/
│           ├── Login.vue             # 登录页
│           ├── Register.vue          # 注册页
│           ├── Layout.vue            # 主布局（侧边栏 + 顶栏 + 内容区）
│           ├── Dashboard.vue         # 项目列表 + 新建项目
│           └── ProjectBoard.vue      # 看板视图 + 任务详情 + 评论 + 成员管理
│
├── database/
│   └── init.sql                      # MySQL 建表脚本（6 张表 + 索引 + 外键）
│
└── README.md                         # 本文档
```

---

## 数据库设计

### ER 关系图

```
User 1 ────< ProjectMember >──── 1 Project 1 ────< Task >──── 1 User (creator)
                      │                              │
                      │                              ├────< Comment >──── 1 User
                      │                              │
                      │                              └────< TaskTag >──── Tag
                      │
                      └── 所有任务通过 project_id 关联
```

### 表结构详情

#### users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| username | VARCHAR(50) UNIQUE | 用户名 |
| email | VARCHAR(100) UNIQUE | 邮箱 |
| hashed_password | VARCHAR(255) | bcrypt 哈希密码 |
| avatar | VARCHAR(255) | 头像 URL |
| is_active | BOOLEAN | 账号状态 |
| created_at | DATETIME | 注册时间 |

#### projects（项目表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| name | VARCHAR(100) | 项目名称 |
| description | TEXT | 项目描述 |
| cover_color | VARCHAR(7) | 封面颜色（默认 #4A90D9） |
| owner_id | INT FK → users | 创建者 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### project_members（项目成员表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| project_id | INT FK → projects | 项目 ID |
| user_id | INT FK → users | 用户 ID |
| role | ENUM | owner / admin / member |
| joined_at | DATETIME | 加入时间 |

#### tasks（任务表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| title | VARCHAR(200) | 任务标题 |
| description | TEXT | 任务描述 |
| status | ENUM | todo / in_progress / review / done |
| priority | ENUM | low / medium / high / urgent |
| position | INT | 排序位置 |
| creator_id | INT FK → users | 创建者 |
| assignee_id | INT FK → users | 负责人（可为空） |
| project_id | INT FK → projects | 所属项目 |
| due_date | DATETIME | 截止日期 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### comments（评论表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| content | TEXT | 评论内容 |
| user_id | INT FK → users | 评论者 |
| task_id | INT FK → tasks | 关联任务 |
| created_at | DATETIME | 评论时间 |

#### tags（标签表） + task_tags（任务标签关联表）

| 字段 | 类型 | 说明 |
|------|------|------|
| tags.id | INT PK | 标签主键 |
| tags.name | VARCHAR(50) | 标签名 |
| tags.color | VARCHAR(7) | 标签颜色 |
| tags.project_id | INT FK → projects | 所属项目 |
| task_tags.task_id | INT FK → tasks | 任务 ID |
| task_tags.tag_id | INT FK → tags | 标签 ID |

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

确保 MySQL 已安装并运行，然后执行建表脚本：

```bash
mysql -u root -p < database/init.sql
```

如果你使用图形化工具（如 Navicat / DBeaver），也可以直接打开 `database/init.sql` 文件执行。

### 第二步：启动 Redis

**Windows:**
```bash
# 使用 WSL 或下载 Windows 版 Redis
redis-server
```

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

**验证 Redis 是否运行：**
```bash
redis-cli ping
# 应返回: PONG
```

### 第三步：配置并启动后端

```bash
# 进入后端目录
cd backend

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，修改数据库连接信息
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

`.env` 文件内容示例：

```ini
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的数据库密码
DB_NAME=task_collab

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT 密钥（生产环境请修改为随机字符串）
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload --port 8000
```

启动成功后会看到：
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

访问 http://localhost:8000/docs 查看自动生成的 Swagger API 文档。

### 第四步：启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

启动成功后访问：http://localhost:3000

### 第五步：注册并登录

1. 打开 http://localhost:3000，自动跳转到登录页
2. 点击「立即注册」创建账号
3. 注册成功后返回登录页登录
4. 进入首页，点击「+ 新建项目」开始使用

---

## API 接口一览

### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 | 需要登录 |
|------|------|------|----------|
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 用户登录，返回 Token | 否 |
| GET | `/api/auth/me` | 获取当前用户信息 | 是 |
| GET | `/api/auth/search` | 搜索用户（邀请成员用） | 是 |

### 项目模块 `/api/projects`

| 方法 | 路径 | 说明 | 需要登录 |
|------|------|------|----------|
| POST | `/api/projects` | 创建项目 | 是 |
| GET | `/api/projects` | 获取我的项目列表 | 是 |
| GET | `/api/projects/{id}` | 获取项目详情 | 是 |
| PUT | `/api/projects/{id}` | 更新项目（仅创建者） | 是 |
| DELETE | `/api/projects/{id}` | 删除项目（仅创建者） | 是 |
| GET | `/api/projects/{id}/members` | 获取项目成员列表 | 是 |
| POST | `/api/projects/{id}/members` | 添加成员（仅创建者） | 是 |
| DELETE | `/api/projects/{id}/members/{user_id}` | 移除成员（仅创建者） | 是 |

### 任务模块 `/api/tasks`

| 方法 | 路径 | 说明 | 需要登录 |
|------|------|------|----------|
| POST | `/api/tasks` | 创建任务 | 是 |
| GET | `/api/tasks/project/{id}` | 获取项目下所有任务 | 否 |
| GET | `/api/tasks/mine` | 获取分配给我的任务 | 是 |
| GET | `/api/tasks/{id}` | 获取任务详情 | 否 |
| PUT | `/api/tasks/{id}` | 更新任务 | 是 |
| DELETE | `/api/tasks/{id}` | 删除任务（仅创建者） | 是 |

### 评论模块 `/api/comments`

| 方法 | 路径 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/api/comments/task/{id}` | 获取任务评论列表 | 否 |
| POST | `/api/comments` | 发表评论 | 是 |
| DELETE | `/api/comments/{id}` | 删除评论（仅评论者） | 是 |

### 标签模块 `/api/tags`

| 方法 | 路径 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/api/tags/project/{id}` | 获取项目标签 | 是 |
| POST | `/api/tags/project/{id}` | 创建标签 | 是 |
| POST | `/api/tags/{task_id}/{tag_id}` | 给任务打标签 | 是 |
| DELETE | `/api/tags/{task_id}/{tag_id}` | 移除任务标签 | 是 |

### WebSocket

| 路径 | 说明 |
|------|------|
| `WS /ws/{project_id}` | 加入项目 WebSocket 频道，接收实时消息广播 |

---

## 使用流程

### 1. 创建项目

登录后进入首页，点击「+ 新建项目」，填写名称、描述和选择封面颜色。

### 2. 添加成员

进入项目看板页，点击「成员管理」，搜索用户名或邮箱，点击添加。

### 3. 创建任务

点击「+ 新建任务」，填写标题、描述、选择优先级、状态、负责人和截止日期。

### 4. 管理看板

任务按状态分列显示。点击任务卡片可以：
- 查看详细信息
- 发表评论与团队成员讨论
- 编辑任务修改属性

### 5. 查看我的任务

API 提供 `GET /api/tasks/mine` 接口，可查看所有分配给自己的任务。

---

## 生产部署建议

### Docker Compose 一键部署

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: task_collab
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
    environment:
      DB_HOST: mysql
      REDIS_HOST: redis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

### 后端部署

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 前端部署

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

---

## 后续扩展方向

- [ ] **Celery 异步任务** — 邮件通知、定时提醒、逾期任务提醒
- [ ] **文件上传** — 任务附件、截图上传（对接 MinIO / AWS S3）
- [ ] **拖拽排序** — 看板列间拖拽切换状态，列内拖拽排序（对接 vuedraggable）
- [ ] **操作审计日志** — 记录谁在什么时候修改了什么
- [ ] **数据看板** — 任务统计图表、燃尽图、成员工作量统计
- [ ] **通知中心** — 站内通知 + 邮件/Webhook 推送
- [ ] **多语言** — 国际化支持（i18n）
- [ ] **单元测试** — pytest 覆盖核心 CRUD 和认证逻辑

---

## 常见问题

**Q: 启动后端时报错 `Can't connect to MySQL`**

A: 确认 MySQL 服务已启动，并检查 `.env` 中的 `DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD` 是否正确。

**Q: 前端登录成功后立即跳转回登录页**

A: 检查后端 `SECRET_KEY` 是否与前端预期一致，以及系统时间是否准确（JWT Token 对时间敏感）。

**Q: 前端请求报 401 错误**

A: Token 可能已过期。退出登录后重新登录即可。可通过修改 `.env` 中的 `ACCESS_TOKEN_EXPIRE_MINUTES` 延长有效期。

**Q: 修改数据库结构后不生效**

A: 如果使用 `models.py` 自动建表，需要先删除旧表或修改 `models.py` 后重启服务。生产环境建议使用 Alembic 做数据库迁移。

---

## License

MIT
