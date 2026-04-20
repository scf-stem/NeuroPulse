# Zeabur 部署指南 - Neuro Pulse

## 部署方式

本项目使用 **单容器部署**（推荐）：前端构建后放入后端的静态目录，由 FastAPI 统一服务。

```
┌─────────────────────────────────────────┐
│           单容器 (Single Container)      │
│  ┌─────────────────────────────────────┐│
│  │  FastAPI Backend                    ││
│  │  ├── /api/*  → API 接口             ││
│  │  ├── /       → 前端 index.html      ││
│  │  └── /*      → 前端静态资源          ││
│  └─────────────────────────────────────┘│
│              Port: 8000                  │
└─────────────────────────────────────────┘
```

## 项目结构

```
web/
├── Dockerfile         # 单容器部署配置 (前后端合一) ⭐
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py   # 包含静态文件服务
│   │   └── ...
│   └── requirements.txt
├── frontend/          # Vue 前端
│   ├── src/
│   └── package.json
└── ZEABUR_DEPLOY.md   # 本文档
```

## 部署步骤

### 1. 创建 Zeabur 项目

1. 登录 [Zeabur Dashboard](https://dash.zeabur.com)
2. 点击 **创建项目**
3. 选择部署区域 (建议亚洲节点)

### 2. 部署 PostgreSQL 数据库

1. 在项目中点击 **部署新服务**
2. 选择 **Marketplace** → **PostgreSQL**
3. 等待数据库启动完成

### 3. 部署应用 (单容器，前后端合一)

1. 点击 **部署新服务** → **Git**
2. 选择你的 GitHub 仓库
3. **重要**: 设置 Root Directory 为 `web`
4. Zeabur 会自动检测根目录的 `Dockerfile` 并构建

### 4. 配置环境变量

在服务的 **环境变量** 页面添加：

| 变量名 | 值 | 必需 | 说明 |
|--------|-----|------|------|
| `APP_ENV` | `production` | ✓ | 生产环境 |
| `DEBUG` | `false` | ✓ | 关闭调试模式 |
| `SECRET_KEY` | `<随机字符串>` | ✓ | 应用密钥 |
| `JWT_SECRET_KEY` | `<随机字符串>` | ✓ | JWT 密钥 |
| `ANTHROPIC_API_KEY` | `<API Key>` | ✗ | Claude API (AI功能) |
| `DEVICE_API_KEY` | `<设备密钥>` | ✓ | ESP32 设备认证 |

**数据库变量** - Zeabur 会自动注入：
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_USERNAME`
- `POSTGRES_PASSWORD`
- `POSTGRES_DATABASE`

### 5. 绑定域名

1. 在服务页面点击 **域名**
2. 添加 Zeabur 自动域名 (如 `tremor-guard.zeabur.app`)
3. 或绑定自定义域名
4. Zeabur 自动签发 SSL 证书

## 服务架构

```
                    Internet
                       │
                       ▼
            ┌─────────────────────┐
            │    Neuro Pulse      │
            │   (单容器部署)       │
            │                     │
            │  ┌───────────────┐  │
            │  │   FastAPI     │  │
            │  │  + Vue SPA    │  │
            │  │   Port: 8000  │  │
            │  └───────┬───────┘  │
            └──────────┼──────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
     ┌───────────┐         ┌───────────┐
     │PostgreSQL │         │   Redis   │
     │ Port:5432 │         │ Port:6379 │
     └───────────┘         └───────────┘
```

## ESP32 设备配置

部署完成后，更新 ESP32 的 `network_config.h`：

```cpp
// 服务器配置
#define SERVER_HOST         "tremor-guard.zeabur.app"  // 你的域名
#define SERVER_PORT         443                         // HTTPS
#define SERVER_USE_HTTPS    true

// API 路径
#define API_BATCH_PATH      "/api/data/upload/batch"
#define API_HEARTBEAT_PATH  "/api/device/heartbeat"

// 设备认证 (与后端 DEVICE_API_KEY 一致)
#define DEVICE_API_KEY      "your-device-api-key"
```

## Dockerfile 说明

```dockerfile
# 第一阶段：构建前端
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
ENV VITE_API_BASE_URL=/api
RUN npm run build

# 第二阶段：后端 + 前端静态文件
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./
# 复制前端构建产物到 static 目录
COPY --from=frontend-builder /app/frontend/dist ./static
# 启动 FastAPI (同时服务 API 和静态文件)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## 路由说明

| 路径 | 处理方式 |
|------|----------|
| `/api/*` | FastAPI API 路由 |
| `/health` | 健康检查接口 |
| `/assets/*` | 静态资源 (js, css, images) |
| `/*` | Vue SPA 路由 (返回 index.html) |

## 本地测试

```bash
# 在 web 目录下构建
docker build -t tremor-guard .

# 运行
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  -e SECRET_KEY="test-secret" \
  -e JWT_SECRET_KEY="test-jwt-secret" \
  tremor-guard

# 访问
# 前端: http://localhost:8000/
# API:  http://localhost:8000/api
# 文档: http://localhost:8000/docs (DEBUG=true时)
```

## 常见问题

### Q: 前端页面空白？
检查前端构建是否成功。查看 Zeabur 构建日志中的 `npm run build` 输出。

### Q: API 返回 404？
确保 API 路径以 `/api/` 开头。FastAPI 路由优先于静态文件服务。

### Q: 数据库连接失败？
1. 确保 PostgreSQL 服务已启动
2. 在 Zeabur 中将 PostgreSQL 与应用服务绑定
3. 检查环境变量是否正确注入

### Q: CORS 错误？
单容器部署时前后端同源，不应该有 CORS 问题。如有问题检查请求路径。

### Q: 如何查看日志？
在 Zeabur Dashboard 中点击服务，选择 **日志** 标签页。

## 费用估算

Zeabur Developer Plan: $5/月
- 应用服务: ~$3-5/月
- PostgreSQL: ~$3-5/月
- 总计: ~$6-10/月

## 参考链接

- [Zeabur 官方文档](https://zeabur.com/docs)
- [Dockerfile 部署](https://zeabur.com/docs/zh-CN/deploy/dockerfile)
- [环境变量配置](https://zeabur.com/docs/zh-CN/environment-variables)
