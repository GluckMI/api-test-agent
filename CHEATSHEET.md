# ⚡ API 接口自动化测试 Agent - 速查卡片

## 📌 最常用命令

```bash
# 运行测试（CLI 模式）
python api_test_agent.py run <test.yaml|tests/> --reports html,json

# 启动 GUI 编辑器（v3.0 新增）
python api_test_agent.py gui start

# 示例
python api_test_agent.py run tests/my_test.yaml --reports html
```

---

## 🖥️ GUI 快速启动 (v3.0)

```bash
# 1. 安装依赖
pip install fastapi uvicorn websockets pydantic-settings
cd frontend && npm install && cd ..

# 2. 启动服务
python api_test_agent.py gui start

# 3. 访问地址
# 前端: http://localhost:3000
# API 文档: http://localhost:8000/docs
```

### GUI CLI 选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--host` | 服务器地址 | `0.0.0.0` |
| `--port` | 后端端口 | `8000` |
| `--reload` | 启用热重载 | 开发模式 |
| `--no-reload` | 禁用热重载 | 生产模式 |

### GUI 功能速查

| 功能 | 路径 | 说明 |
|------|------|------|
| Dashboard | `/` | 统计仪表盘 |
| 项目管理 | `/projects` | 项目 CRUD |
| 测试列表 | `/tests/:id` | 用例列表 |
| 测试编辑 | `/tests/:id/:testId/edit` | 可视化编辑器 |
| 执行控制台 | `/execution/:id` | 实时日志 |
| 报告中心 | `/reports` | 报告查看 |
| 环境管理 | `/environments` | 环境配置 |

---

## 📝 YAML 模板（复制即用）

### 简单 GET 请求
```yaml
name: "测试名称"
steps:
  - name: "步骤名"
    method: GET
    endpoint: "https://api.example.com/resource"
    
    assertions:
      - type: status_code
        expected: 200
      - type: response_time
        max: 5.0
```

### POST 请求（JSON）
```yaml
- name: "创建资源"
  method: POST
  endpoint: "/resource"
  
  json:
    field1: "value1"
    field2: "value2"
  
  assertions:
    - type: status_code
      expected: 201
    - type: contains_key
      key: "id"
      path: "$"
```

### 变量传递
```yaml
steps:
  - name: "登录"
    method: POST
    endpoint: "/login"
    json: { "username": "test", "password": "pass" }
    extract:
      token: "data.token"
  
  - name: "调用 API"
    method: GET
    endpoint: "/resource"
    headers:
      Authorization: "Bearer ${token}"
```

---

## 🔍 断言类型

| 类型 | 参数 | 用途 |
|------|------|------|
| `status_code` | expected | HTTP 状态码 |
| `equal` | path, expected | 值相等 |
| `contains_key` | key, path | 键存在性 |
| `type_check` | path, expected_type | 数据类型 |
| `length` | path, expected | 长度检查 |
| `response_time` | min/max | 响应时间 |
| `regex_match` | path, pattern | 正则匹配 |

---

## 🎯 CLI 选项

| 选项 | 简写 | 说明 |
|------|------|------|
| `--output DIR` | `-o` | 报告目录 |
| `--reports FORMATS` | `-r` | 报告格式 |
| `--base-url URL` | - | API 基础 URL |
| `--timeout SEC` | `-t` | 超时时间 |
| `--verbose` | `-v` | 详细输出 |

---

## 📊 报告格式

- **HTML**: `--reports html` (美观、交互式)
- **Markdown**: `--reports markdown` (轻量、文档化)
- **JSON**: `--reports json` (CI/CD 集成)

---

## 🐛 调试技巧

```bash
# 查看详细日志
python api_test_agent.py run test.yaml --verbose

# 查看日志文件
type api_test.log

# 只运行一个测试
python api_test_agent.py run specific_test.yaml
```

---

## 💡 Python API

```python
from test_runner import TestRunner
from report_generator import ReportGenerator

runner = TestRunner()
result = runner.execute_test_file("test.yaml")
ReportGenerator().generate_html_report(result)
runner.close()
```

---

## 📁 项目结构

```
api-test-agent/
├── src/api_test_agent/gui/   # GUI 后端 (v3.0)
│   ├── models/               # 数据模型
│   ├── routes/               # API 路由
│   ├── services/             # 业务逻辑
│   └── websocket/            # WebSocket 服务
├── frontend/                 # 前端界面 (v3.0)
│   ├── src/
│   │   ├── api/              # API 客户端
│   │   ├── pages/            # 页面组件
│   │   ├── layouts/          # 布局组件
│   │   └── types/            # TypeScript 类型
├── *.py                      # 核心代码
├── tests/                    # 你的测试用例
├── examples/                 # 示例测试
├── reports/                  # 生成的报告
└── README.md                 # 文档
```

---

## 🆘 常见问题

**Q: 测试失败了？**
→ 使用 `--verbose` 查看详细错误

**Q: 超时了？**
→ `--timeout 60` 增加超时时间

**Q: 怎么跳过某个测试？**
→ 分离到不同文件，只运行需要的

**Q: 敏感信息怎么处理？**
→ 使用环境变量 `${VARIABLE}`

---

## 🔗 相关文档

- `使用教程.md` - 完整教程（含 GUI 章节）
- `README.md` - 项目简介
- `CHANGELOG.md` - 版本变更记录
- `docs/Phase2_新功能使用指南.md` - Phase 2 功能指南

---

*最后更新：2026-05-01 (v3.0.0-alpha)*
