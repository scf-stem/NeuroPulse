# TremorGuard / 震颤卫士

> An end-to-end tremor monitoring prototype built with ESP32-C3, MPU6050, FastAPI, and Vue 3.<br>
> 基于 ESP32-C3、MPU6050、FastAPI 与 Vue 3 的端到端震颤监测原型。

[中文](#中文说明) · [English](#english) · [架构 / Architecture](#系统架构--architecture) · [快速开始 / Quick start](#快速开始) · [API](#api-概览)

TremorGuard（震颤卫士，原项目名 **NeuroPulse / Neuro Pulse**）将可穿戴传感器固件、异步后端服务和双语 Web 应用集中在一个仓库中。系统可采集 MPU6050 加速度数据，在设备端执行 FFT 分析，将监测结果上传至后端，并在前端提供趋势、报告、用药、康复和 AI 辅助功能。

> [!IMPORTANT]
> 本项目是健康监测与教学研究原型，不是医疗器械。设备端的 4–6 Hz 检测频段和软件输出不能用于诊断、治疗或替代专业医疗建议。任何临床使用都需要独立的医学验证、风险评估、合规审查和数据保护措施。

## 中文说明

### 已实现能力

#### 设备与固件

- 面向 Seeed Studio XIAO ESP32-C3 与 MPU6050，使用 I²C 读取加速度计和陀螺仪数据。
- 以 125 Hz 采样 256 点，频率分辨率约 0.488 Hz；默认分析 4–6 Hz 配置频段。
- 支持硬件自检、I²C 扫描、单次读取、连续数据流、FFT 分析、频谱与统计输出。
- 支持 Wi-Fi、HTTPS 上传、批量上传、心跳、断线缓存与重连后补传。
- 支持从后端拉取检测参数，以及将本地配置上传到后端。

#### FastAPI 后端

- 基于 FastAPI、SQLAlchemy 2 和 asyncpg 的异步 PostgreSQL 服务。
- 提供用户认证、设备管理、监测会话、数据上传、统计分析和趋势查询。
- 提供用药、康复训练、健康档案、报告导出及医生摘要相关接口。
- 通过 DashScope 兼容接口调用 Qwen；未设置 `DASHSCOPE_API_KEY` 时，相关 AI 请求会返回 `503`。
- 开发环境提供 Swagger UI、ReDoc 和设备测试接口；生产环境关闭测试路由并校验关键安全配置。

#### Vue Web 应用

- Vue 3 Composition API、TypeScript、Vite、Pinia 和 Vue Router。
- 包含仪表盘、实时监测、历史记录、趋势分析、设备、报告、用药、健康档案、康复训练、AI 助手和设置页面。
- 使用 Chart.js 展示监测数据，并提供中文/英文界面。
- 监测页支持显式模拟模式；该模式仅适合演示和前端开发。

## 系统架构 / Architecture

```mermaid
flowchart LR
    Sensor["MPU6050<br/>加速度与角速度"] --> Device["XIAO ESP32-C3<br/>125 Hz 采样与 FFT"]
    Device -->|"HTTPS / JSON"| API["FastAPI API"]
    API --> DB["PostgreSQL"]
    API -.-> Cache["Redis 配置预留"]
    API -->|"DashScope compatible API"| Qwen["Qwen"]
    Web["Vue 3 Web App"] <-->|"REST / JWT"| API
```

数据流程：设备采样并执行频域分析 → 结果通过设备密钥上传 → 后端持久化与聚合 → Web 应用展示监测、趋势和报告 → 需要时由 Qwen 辅助生成解释性内容。

## 技术栈

| 层 | 主要技术 |
| --- | --- |
| 固件 | Arduino / C++、ESP32-C3、MPU6050、ArduinoJson、arduinoFFT、Wi-Fi、HTTPS |
| 后端 | Python 3.12、FastAPI、Pydantic、SQLAlchemy 2、asyncpg、Alembic、JWT |
| 数据与报告 | PostgreSQL、NumPy、pandas、ReportLab、WeasyPrint |
| AI | DashScope 兼容 Chat Completions API、Qwen（默认 `qwen-plus`） |
| 前端 | Vue 3、TypeScript、Vite、Pinia、Vue Router、Axios、Chart.js、Tailwind CSS |
| 自动化 | GitHub Actions、Node.js 20、Python 3.12 |

## 仓库结构

```text
TremorGuard/
├── firmware/mpu6050_init/  # ESP32-C3 + MPU6050 主固件
├── backend/
│   ├── app/                # FastAPI 应用、模型、服务和路由
│   ├── api/                # 部署入口（使用前需核对平台路径）
│   ├── alembic/            # 数据库迁移
│   └── tests/              # 后端测试
├── frontend/src/           # Vue 3 应用
├── deploy/                 # 部署模板
├── docs/                   # 架构、安装和项目资料
└── .github/workflows/      # 后端、前端、固件和发布工作流
```

## 快速开始

### 前置条件

- Git
- Python 3.12
- PostgreSQL 14 或更高版本
- Node.js 20 与 npm
- 固件开发时：Arduino IDE 2.x、ESP32 开发板支持包、XIAO ESP32-C3、MPU6050

Redis 目前不是本地启动的硬性依赖；代码保留了 Redis 配置，以便后续缓存或实时能力使用。

### 1. 获取代码

```bash
git clone https://github.com/scf-stem/TremorGuard.git
cd TremorGuard
```

### 2. 启动后端

先创建 PostgreSQL 数据库，例如：

```bash
createdb tremor_guard
```

安装依赖：

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

仓库没有跟踪 `backend/.env.example`。请在 `backend/.env` 中手动写入本地配置；该文件已被 Git 忽略：

```dotenv
APP_NAME=TremorGuard
APP_ENV=development
DEBUG=true
AUTO_INIT_DB=true
DATABASE_URL=postgresql+asyncpg://postgres:replace-with-password@localhost:5432/tremor_guard
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=replace-with-a-long-random-value
SECRET_KEY=replace-with-another-long-random-value
DEVICE_API_KEY=replace-with-a-device-key
DASHSCOPE_API_KEY=
```

`AUTO_INIT_DB=true` 仅在非生产环境按 SQLAlchemy 元数据自动建表。需要使用版本化迁移时，改为运行：

```bash
alembic upgrade head
```

启动服务：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

开发环境入口：

- API 信息：<http://localhost:8000/api>
- 健康检查：<http://localhost:8000/health>
- Swagger UI：<http://localhost:8000/docs>
- ReDoc：<http://localhost:8000/redoc>

### 3. 启动前端

在另一个终端中运行：

```bash
cd frontend
cp .env.example .env.local
npm ci
npm run dev
```

默认后端地址是 `http://localhost:8000`。如需更改，请编辑 `.env.local`：

```dotenv
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_MONITOR_MOCK=false
```

Vite 默认开发地址通常为 <http://localhost:5173>。前端演示模式可通过监测页支持的显式配置启用；不要在生产环境依赖演示令牌或模拟数据。

### 4. 编译固件

1. 在 Arduino IDE 安装 Espressif ESP32 开发板支持、ArduinoJson 和 arduinoFFT。
2. 选择 Seeed Studio XIAO ESP32-C3 对应开发板与串口。
3. 打开 `firmware/mpu6050_init/mpu6050_init.ino`。
4. 复制 `network_secrets.example.h` 为 `network_secrets.h`，填入 Wi-Fi 信息；不要提交该文件。
5. 检查 `network_config.h` 中的服务器域名、HTTPS 设置、API 路径、设备 ID 和设备密钥，然后编译上传。

当前代码实际使用的 I²C 接线：

| XIAO ESP32-C3 | MPU6050 | 说明 |
| --- | --- | --- |
| D4 / GPIO6 | SDA | I²C 数据 |
| D5 / GPIO7 | SCL | I²C 时钟，默认 100 kHz |
| D3 / GPIO5 | INT | 可选中断 |
| 3V3 | VCC / VLOGIC | 供电 |
| GND | GND | 地 |

固件默认指向 `/api/test/*` 测试接口，而这些接口只在非生产环境注册。连接真实部署前，必须让固件路径与生产设备接口对齐，并确保 `DEVICE_API_KEY` 与服务端一致。

常用串口命令：

```text
test  scan  read  stream  reset
tremor  analyze  spectrum  stats
wifi  connect  disconnect  upload  flush
server  cfgup  update  config  help
```

## 配置与安全

### 关键后端变量

| 变量 | 用途 | 生产要求 |
| --- | --- | --- |
| `APP_ENV` | `development` 或 `production` | 生产设为 `production` |
| `DEBUG` | 文档与调试行为 | 生产必须为 `false` |
| `DATABASE_URL` | asyncpg PostgreSQL URL | 使用受保护的生产数据库 |
| `JWT_SECRET_KEY` | JWT 签名 | 必须替换默认值 |
| `SECRET_KEY` | 应用密钥 | 必须替换默认值 |
| `DEVICE_API_KEY` | 设备上传鉴权 | 生产不可为空；设备通过 `X-Device-Key` 发送 |
| `DASHSCOPE_API_KEY` | Qwen 调用凭据 | 仅启用 AI 功能时设置 |
| `DASHSCOPE_BASE_URL` | DashScope 兼容端点 | 默认官方兼容端点 |
| `DASHSCOPE_MODEL` | 模型名称 | 默认 `qwen-plus` |
| `CORS_ORIGINS` | 允许的 Web 来源 | 仅配置可信来源 |

应用启动时会拒绝以下生产配置：`DEBUG=true`、默认 `JWT_SECRET_KEY`、默认 `SECRET_KEY` 或空的 `DEVICE_API_KEY`。不要提交 `.env`、`network_secrets.h`、数据库凭据或第三方 API 密钥。安全问题请按 [SECURITY.md](SECURITY.md) 私下报告。

## API 概览

完整模式的 REST API 以 `/api` 为前缀：

| 分组 | 前缀 | 用途 |
| --- | --- | --- |
| 认证 | `/api/auth` | 注册、登录、令牌、密码与个人资料 |
| 设备 | `/api/device` | 注册、列表、心跳和状态 |
| 数据 | `/api/data` | 监测会话、单条/批量上传、历史与统计 |
| 分析 | `/api/analysis` | 日/周分析、严重度、小时分布与趋势 |
| AI | `/api/ai` | 对话、健康解释、康复计划和报告动作 |
| 报告 | `/api/report` | 报告生成、CSV/JSON 导出和医生摘要 |
| 用药 | `/api/medication` | 药物、服药记录与计划 |
| 康复 | `/api/rehabilitation` | 训练项目、计划、打卡与统计 |
| 健康档案 | `/api/health` | 档案、病历、家族史与就诊记录 |
| 配置 | `/api/config` | 设备检测参数上传、读取、保存与重置 |
| 测试 | `/api/test` | 仅非生产环境的设备联调接口 |

用户接口使用 Bearer JWT；设备上传接口使用 `X-Device-Key`。以运行时 `/docs` 生成的 OpenAPI 文档和当前路由代码为准。

## 验证与开发

```bash
# 后端
cd backend
python -m compileall .
pytest -q

# 前端（当前没有单独的测试脚本，类型检查包含在 build 中）
cd frontend
npm ci
npm run build
```

固件工作流目前只检查主草图和目录布局；实际硬件修改仍需在目标开发板上完成编译、烧录和传感器验证。贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## CI、发布与部署

- 后端 CI 使用 Python 3.12 安装依赖并运行编译检查。
- 前端 CI 使用 Node.js 20 执行 `npm ci` 和生产构建。
- 固件工作流验证预期主草图与项目布局。
- Release 工作流为标签和手动运行打包前后端产物；其中部分产物名仍保留 `neuropulse-*` 兼容标识。

`deploy/` 与 `backend/api/` 中的文件是历史部署模板，不代表已完成线上部署。部分模板仍含旧运行时版本或旧目录假设；部署前请按 Python 3.12、当前仓库目录和目标平台规则逐项复核。CI 只执行验证和打包，不会自动发布到线上环境。

## 命名兼容说明

仓库和对外项目名现为 **TremorGuard / 震颤卫士**。为避免破坏现有部署、包、演示账号和发布流程，代码中仍有 `NeuroPulse`、`Neuro Pulse`、`neuropulse-*` 等历史标识。它们是迁移期兼容内容，不表示另一个仓库；修改时不要进行未经验证的全局替换。

## 文档

- [架构说明](docs/architecture.md)
- [API 摘要](docs/api.md)
- [后端安装](docs/backend-setup.md)
- [前端安装](docs/frontend-setup.md)
- [固件安装](docs/firmware-setup.md)
- [后端部署说明](docs/backend-deploy.md)
- [开发指南](docs/development-guide.md)
- [项目介绍](docs/about.md)
- [中文项目资料](docs/帕金森震颤监测手环_AI增强版_项目招生介绍.md)

部分长篇资料包含早期设计设想；若文档与实现不一致，以当前源代码、配置和运行时 OpenAPI 为准。

## English

### Overview

TremorGuard, formerly named **NeuroPulse / Neuro Pulse**, is a monorepo for a wearable tremor-monitoring prototype. The firmware samples motion data and performs FFT-based analysis, the FastAPI service stores and aggregates observations, and the Vue application presents monitoring, trends, reports, medication, rehabilitation, and AI-assisted workflows.

This software is for monitoring, education, and research prototyping only. It is not a medical device and must not be used to diagnose or treat any condition. The configured 4–6 Hz band is an engineering parameter, not a standalone clinical criterion.

### Implemented components

- **Firmware:** Seeed Studio XIAO ESP32-C3 and MPU6050 support; 125 Hz sampling; 256-point FFT; hardware diagnostics; serial tools; Wi-Fi/HTTPS transport; batching, heartbeat, offline buffering, and runtime configuration sync.
- **Backend:** asynchronous FastAPI and PostgreSQL API for authentication, devices, monitoring sessions, uploads, analytics, medication, rehabilitation, health records, reports, and configuration.
- **AI:** Qwen through a DashScope-compatible Chat Completions endpoint. AI calls return `503 Service Unavailable` when `DASHSCOPE_API_KEY` is not configured.
- **Frontend:** bilingual Vue 3 and TypeScript application with dashboards, live monitoring, history, analytics, devices, reports, medication, health profile, rehabilitation, settings, and AI assistant views.

### Quick start

Requirements: Python 3.12, PostgreSQL, Node.js 20, npm, and—when building firmware—an Arduino-compatible ESP32 toolchain.

#### Backend

```bash
git clone https://github.com/scf-stem/TremorGuard.git
cd TremorGuard/backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a PostgreSQL database, then create `backend/.env` manually. The repository intentionally does not track a backend `.env.example`:

```dotenv
APP_NAME=TremorGuard
APP_ENV=development
DEBUG=true
AUTO_INIT_DB=true
DATABASE_URL=postgresql+asyncpg://postgres:replace-with-password@localhost:5432/tremor_guard
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=replace-with-a-long-random-value
SECRET_KEY=replace-with-another-long-random-value
DEVICE_API_KEY=replace-with-a-device-key
DASHSCOPE_API_KEY=
```

Start the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Use `AUTO_INIT_DB=true` only for non-production metadata initialization. For versioned schema management, run `alembic upgrade head`. Development API docs are available at <http://localhost:8000/docs>.

#### Frontend

```bash
cd TremorGuard/frontend
cp .env.example .env.local
npm ci
npm run dev
```

`VITE_API_BASE_URL` defaults to `http://localhost:8000`. Keep `VITE_ENABLE_MONITOR_MOCK=false` when connecting to a real backend.

#### Firmware

Open `firmware/mpu6050_init/mpu6050_init.ino`, copy `network_secrets.example.h` to the untracked `network_secrets.h`, and add local Wi-Fi credentials. Install ArduinoJson and arduinoFFT, select the XIAO ESP32-C3 board, and verify `network_config.h` before flashing.

The active pin definitions are GPIO6/D4 for SDA, GPIO7/D5 for SCL, and optional GPIO5/D3 for INT. The firmware defaults to development-only `/api/test/*` endpoints, so align the host, paths, device identity, and `DEVICE_API_KEY` with the target backend before deployment.

### Security and production

Production startup requires `DEBUG=false`, non-default `JWT_SECRET_KEY` and `SECRET_KEY` values, and a non-empty `DEVICE_API_KEY`. Store all credentials outside source control, restrict CORS to trusted origins, use managed TLS and PostgreSQL, and disable all demo or mock paths.

Files under `deploy/` and `backend/api/` are deployment templates with some legacy runtime or path assumptions. Review them against Python 3.12, the current repository layout, and the selected hosting platform. GitHub Actions validates and packages the project but does not perform a live deployment.

### Testing

```bash
cd backend
python -m compileall .
pytest -q

cd ../frontend
npm ci
npm run build
```

Frontend type checking runs as part of `npm run build`; no separate frontend test command is currently defined. Firmware changes require a real board compile and hardware validation in addition to the repository layout check.

### Documentation and naming

See the [architecture](docs/architecture.md), [API summary](docs/api.md), [backend setup](docs/backend-setup.md), [frontend setup](docs/frontend-setup.md), [firmware setup](docs/firmware-setup.md), and [deployment notes](docs/backend-deploy.md). Some longer documents retain historical design material; current source code, configuration, and generated OpenAPI are authoritative.

The public name is now **TremorGuard**. Legacy `NeuroPulse`, `Neuro Pulse`, and `neuropulse-*` identifiers remain where changing them could break compatibility. Migrate those identifiers deliberately rather than with an unverified global replacement.

## License

Copyright © 2026 SCF-STEM. All rights reserved. This is proprietary software, not an open-source distribution. See [LICENSE](LICENSE) for the applicable terms.
