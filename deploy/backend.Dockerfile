# ========================================
# 震颤卫士 (Tremor Guard) - 单容器部署 Dockerfile
# 前后端合一，只需部署一个服务
# 部署平台: Zeabur
# ========================================

# ============ 第一阶段：构建前端 ============
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund

# 复制前端源代码
COPY frontend ./

# 构建前端
# VITE_API_BASE_URL 留空，使前端请求使用相对路径 (e.g. /api/...)
# 这样前端静态文件由后端服务时，会自动请求同一域名的后端 API
ENV VITE_API_BASE_URL=""
RUN npm run build

# ============ 第二阶段：构建后端并整合前端 ============
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 安装系统依赖 (如果不包含 backend/app/main.py 需要的库，可以在这里添加)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend ./

# 从第一阶段复制前端构建产物到后端静态目录
# 这里将 dist 复制为 backend/app/static，因为 main.py 中定义 STATIC_DIR 为 ../static
# main.py 相对于 app 文件夹，所以 app/../static 就是 app 同级的 static 文件夹
# 我们直接复制到 /app/static 即可，因为 WORKDIR 是 /app
COPY --from=frontend-builder /app/frontend/dist ./static

# 环境变量
ENV APP_ENV=production \
    PORT=8080

EXPOSE 8080

# 启动 FastAPI
# 使用 python -m 启动，这样会使用 main.py 中的配置 (读取 PORT 环境变量)
CMD ["python", "-m", "app.main"]
