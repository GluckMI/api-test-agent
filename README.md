# 🚀 API 接口自动化测试 Agent

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.0.0--alpha-orange.svg)]()

一个让 **API 测试像写便签一样简单** 的 Python 框架

---

## ✨ v3.0 新功能亮点 🎉

> **v3.0.0-alpha** — 可视化 GUI 编辑器，零编码上手！

### 🔥 核心特性一览

| 特性 | 说明 | 状态 |
|------|------|------|
| **🖥️ 可视化 GUI** | React 19 + Ant Design 6 现代化界面 | ✅ 完成 |
| **📝 测试用例编辑器** | 表单式配置 + 实时 YAML 预览 | ✅ 完成 |
| **📊 Dashboard 仪表盘** | 项目统计、测试趋势、执行记录 | ✅ 完成 |
| **🔧 实时执行控制台** | WebSocket 实时日志流、进度展示 | ✅ 完成 |
| **🌐 环境管理器** | 多环境配置可视化管理与切换 | ✅ 完成 |
| **📋 报告中心** | 报告列表、详情查看、图表分析 | ✅ 完成 |
| **🎭 Mock 服务** | API Mock 配置与管理 | 🚧 开发中 |

---

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    浏览器 (单端口访问)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ React 19    │  │ Ant Design 6│  │   ECharts 图表      │  │
│  │ TypeScript  │  │ Zustand     │  │   实时数据可视化     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         └────────────────┼─────────────────────┘            │
│                          │ HTTP / WebSocket                 │
├──────────────────────────┼──────────────────────────────────┤
│              FastAPI 一体化服务 (单端口)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ REST API    │  │ 静态文件托管  │  │   Test Runner       │  │
│  │ /api/*      │  │ SPA 中间件   │  │   核心执行引擎      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ✅ 端口自动检测 - 冲突时自动切换                            │
│  ✅ SPA 路由支持 - 前端路由无缝工作                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置要求

- **Python** 3.8+
- **Node.js** 16+ (用于构建前端)

### 第一步：安装依赖

```bash
# 克隆项目
git clone https://github.com/GluckMI/api-test-agent.git
cd api-test-agent

# 安装 Python 后端依赖
pip install -r requirements.txt

# 安装 GUI 额外依赖
pip install fastapi uvicorn websockets pydantic-settings

# 安装前端依赖并构建
cd frontend
npm install
npm run build
cd ..
```

> ⚠️ **重要**：首次使用或前端代码更新后，必须执行 `npm run build`！

### 第二步：启动服务

```bash
# 启动 GUI 服务（一体化部署，前后端共用一个端口）
python api_test_agent.py gui start --no-reload

# 或指定端口
python api_test_agent.py gui start --port 8080 --no-reload
```

**启动成功示例：**
```
============================================================
  🌐 API Test Agent GUI
============================================================

⚠️ 端口 8000 已被占用，正在查找可用端口...
✅ 找到可用端口: 8003
============================================================
  API Test Agent GUI Server
============================================================
  Address: http://0.0.0.0:8003
  Docs:    http://0.0.0.0:8003/api/docs
  Reload:  Disabled
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
```

### 第三步：访问界面

打开浏览器访问：**http://localhost:8003** （或显示的实际端口）

| 服务 | 地址 | 说明 |
|------|------|------|
| **GUI 主界面** | http://localhost:8003 | 前端界面入口 |
| **API 文档** | http://localhost:8003/api/docs | Swagger 交互式文档 |
| **健康检查** | http://localhost:8003/health | 服务状态检查 |

> 💡 所有服务通过同一个端口访问，无需分别配置前后端地址！

---

## 📱 功能模块详解

### 1️⃣ Dashboard 仪表盘 (`/`)

- 📊 项目总数、测试用例数、今日执行次数统计
- 📈 最近 7 天测试趋势折线图
- 📋 最近执行的测试列表（可跳转详情）

### 2️⃣ 项目管理 (`/projects`)

- 创建/编辑/删除项目
- 项目下的测试用例统计
- 项目列表展示与搜索

### 3️⃣ 测试用例编辑器 (`/tests/new`, `/tests/:id`) ⭐

**核心功能！** 支持两种编辑模式：

#### 模式 A：表单式编辑（推荐新手）

| 字段 | 说明 | 示例 |
|------|------|------|
| 名称 | 测试用例名称 | "用户登录接口测试" |
| 描述 | 测试说明 | "验证登录接口的正常流程" |
| 所属项目 | 关联项目 | 从下拉列表选择 |
| 步骤配置 | HTTP 请求步骤 | 见下方 |

**步骤配置：**
- 步骤名称、HTTP 方法（GET/POST/PUT/DELETE/PATCH）、端点路径
- 支持添加多个步骤，动态增删

#### 模式 B：YAML 实时预览 🆕

- 📝 **实时同步**：表单修改即时反映到 YAML 预览
- 🎨 **代码高亮**：VS Code 风格深色主题
- 📋 **格式规范**：标准 YAML 格式，缩进对齐

```yaml
name: "用户登录测试"
description: ""
steps:
  - name: ""
    method: GET
    endpoint: ""
    params: {}
    headers: {}
    assertions: []
    extract: {}
```

### 4️⃣ 实时执行控制台 (`/execution/:id`)

- 📡 **WebSocket 实时通信** — 无刷新日志流
- 📊 **进度条显示** — 当前步骤/总步骤数
- 🟢🔴 **状态指示** — 运行中/通过/失败
- 📝 **分级日志** — INFO/WARN/ERROR 分类展示

### 5️⃣ 报告中心 (`/reports`, `/reports/:id`)

- 📋 报告列表（按时间倒序）
- 📊 报告详情（图表化展示）
- 🔍 执行历史查看

### 6️⃣ 环境管理器 (`/environments`)

- 多环境配置（dev/staging/prod）
- 环境变量可视化管理
- 一键切换环境

---

## 📡 RESTful API 参考

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{id}` | 获取项目详情 |
| PUT | `/api/projects/{id}` | 更新项目 |
| DELETE | `/api/projects/{id}` | 删除项目 |
| GET | `/api/tests?project_id=xxx` | 获取测试用例列表 |
| POST | `/api/tests` | 创建测试用例 |
| GET | `/api/tests/{id}` | 获取用例详情 |
| PUT | `/api/tests/{id}` | 更新用例 |
| DELETE | `/api/tests/{id}}` | 删除用例 |
| POST | `/api/execution/run` | 执行测试 |
| GET | `/api/execution/{id}` | 获取执行结果 |
| WS | `/ws/execution/{id}` | WebSocket 实时日志 |

完整 API 文档：启动后访问 `/api/docs`

---

## 🛠️ CLI 命令参考

```bash
# ===== GUI 编辑器 (v3.0) =====
python api_test_agent.py gui start               # 启动 GUI（默认端口 8000）
python api_test_agent.py gui start --port 9000   # 指定端口
python api_test_agent.py gui start --no-reload   # 生产模式（禁用热重载）

# ===== 运行测试 =====
python api_test_agent.py run test.yaml           # 运行单个测试
python api_test_agent.py run tests/              # 运行目录下所有测试
python api_test_agent.py run tests/ -r html,json # 指定报告格式

# ===== 环境管理 =====
python api_test_agent.py run tests/ --env staging # 使用环境配置
python api_test_agent.py env list                 # 列出所有可用环境
python api_test_agent.py env show dev             # 显示环境配置详情

# ===== 性能测试 (v2.1) =====
python api_test_agent.py perf /api/users -d 60 -c 20 -r 100

# ===== 项目初始化 =====
python api_test_agent.py init                     # 初始化项目结构
```

---

## 📂 项目结构

```
api-test-agent/
├── api_test_agent.py          # 入口脚本（向后兼容）
├── pyproject.toml             # 项目配置
├── requirements.txt           # Python 依赖
│
├── src/api_test_agent/        # 核心源码
│   ├── cli.py                 # CLI 命令行入口
│   ├── runner.py              # 测试运行器
│   ├── assertions.py          # 断言引擎
│   ├── environment.py         # 环境管理
│   ├── hooks.py               # 钩子系统
│   ├── data_driver.py         # 数据驱动
│   ├── concurrent_runner.py   # 并发执行
│   ├── perf_tester.py         # 性能测试
│   ├── auth_manager.py        # 认证管理
│   ├── reports.py             # 报告生成
│   │
│   ├── gui_server.py          # GUI 服务器启动脚本
│   └── gui/                   # FastAPI GUI 应用
│       ├── __init__.py        # 应用创建、SPA 中间件
│       ├── config.py          # 配置管理
│       ├── models/            # 数据模型
│       ├── routes/            # API 路由
│       │   ├── projects.py
│       │   ├── tests.py
│       │   ├── execution.py
│       │   ├── environments.py
│       │   └── reports.py
│       ├── services/          # 业务逻辑
│       └── websocket/         # WebSocket 管理
│
├── frontend/                  # React 前端
│   ├── src/
│   │   ├── api/               # API 客户端
│   │   ├── pages/             # 页面组件
│   │   ├── layouts/           # 布局组件
│   │   ├── types/             # 类型定义
│   │   └── App.tsx            # 路由配置
│   ├── package.json
│   └── vite.config.ts
│
├── configs/                   # 配置文件示例
├── examples/                  # 示例代码
├── tests/                     # 测试用例
├── docs/                      # 文档
└── reports/                   # 生成的报告（gitignore）
```

---

## 🐳 Docker 部署（可选）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn websockets pydantic-settings

# 安装 Node.js 并构建前端
COPY --from=node:18-alpine /usr/local/bin/node /usr/local/bin/node
COPY --from=node:18-alpine /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY frontend/ ./frontend/
RUN cd frontend && npm install && npm run build && rm -rf node_modules

# 复制后端代码
COPY . .

EXPOSE 8000

CMD ["python", "api_test_agent.py", "gui", "start", "--no-reload"]
```

```bash
# 构建并运行
docker build -t api-test-agent .
docker run -d -p 8000:8000 api-test-agent
```

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [使用教程.md](使用教程.md) | 完整交互式教程（含 GUI 使用指南） |
| [Phase 2 新功能使用指南](docs/Phase2_新功能使用指南.md) | 性能测试 / 认证增强 / 断言增强 |
| [CHEATSHEET.md](CHEATSHEET.md) | 速查卡片 |
| [CHANGELOG.md](CHANGELOG.md) | 版本变更记录 |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | v1.0 → v2.0 迁移指南 |

### 示例代码

| 目录 | 说明 |
|------|------|
| [examples/v2_environment/](examples/v2_environment/) | 多环境配置最佳实践 |
| [examples/v2_hooks/](examples/v2_hooks/) | 生命周期和钩子使用 |
| [examples/v2_data_driven/](examples/v2_data_driven/) | CSV/JSON 参数化测试 |
| [examples/v2_performance/](examples/v2_performance/) | 负载测试配置 |
| [examples/v2_authentication/](examples/v2_authentication/) | 认证方式示例 |
| [examples/v2_assertions/](examples/v2_assertions/) | 断言类型示例 |

---

## 🔧 开发指南

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 代码格式化
black src/ tests/
flake8 src/ tests/

# 前端开发模式（需要两个终端）
# 终端 1: 后端
python api_test_agent.py gui start --port 8000

# 终端 2: 前端
cd frontend && npm run dev
```

---

## 🤝 贡献指南

欢迎提交 PR！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

### 开发流程

```bash
# 1. Fork 仓库并 Clone
git clone https://github.com/<your-username>/api-test-agent.git

# 2. 创建功能分支
git checkout -b feature/new-feature

# 3. 开发并提交
git add .
git commit -m "feat: 添加新功能"

# 4. Push 并创建 Pull Request
git push origin feature/new-feature
```

---

## 📋 版本计划

| 版本 | 状态 | 主要功能 |
|------|------|---------|
| v1.0 | ✅ 已发布 | 核心功能完成 |
| v2.0 | ✅ 已发布 | 环境管理 + 钩子 + 数据驱动 + 并发 |
| v2.1 | ✅ 已发布 | 性能测试 + 认证增强 + 断言增强 |
| **v3.0** | **🆕 alpha** | **GUI 编辑器 + 实时控制台 + 报告中心** |
| v3.1 | 📋 规划中 | Mock 服务完善 + CI/CD 集成增强 |

---

## 🆘 问题反馈

遇到问题？请：

1. 搜索 [Issues](https://github.com/GluckMI/api-test-agent/issues) 是否有类似问题
2. 新建 Issue 时提供详细信息：
   - 复现步骤
   - 错误日志
   - 环境（OS、Python 版本）
3. 包含截图会更好哦 😊

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## ⭐ Star History

感谢给本项目点个 Star 的支持！

[![Star History Chart](https://api.star-history.com/svg?repos=GluckMI/api-test-agent&type=Date)](https://star-history.com/#GluckMI/api-test-agent&Date)

---

Made with ❤️ by API Test Agent Team