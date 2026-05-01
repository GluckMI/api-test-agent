# 🚀 API 接口自动化测试 Agent

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen.svg)]()

一个让 **API 测试像写便签一样简单** 的 Python 框架

---

## ✨ 特性

- ✅ **声明式配置** - YAML 编写，10 分钟上手
- ✅ **强大断言** - 10 种内置断言类型
- ✅ **智能传递** - 跨步骤变量自动共享
- ✅ **多格式报告** - HTML/Markdown/JSON自动生成
- ✅ **双模式运行** - CLI + Python API
- ✅ **CI/CD 集成** - 原生支持自动化流水线

---

## 📦 快速安装

```bash
git clone https://github.com/qwenpaw/api-test-agent.git
cd api-test-agent
pip install -r requirements.txt
```

---

## 🏃 5 分钟上手

### 创建你的第一个测试

新建 `tests/my_first_test.yaml`:

```yaml
name: "Hello World API 测试"

steps:
  - name: "获取用户信息"
    method: GET
    endpoint: "https://jsonplaceholder.typicode.com/users/1"
    
    assertions:
      - type: status_code
        expected: 200
      
      - type: response_time
        max: 5.0
      
      - type: contains_key
        key: "name"
        path: "$"
      
      - type: equal
        path: "id"
        expected: 1
```

### 运行测试

```bash
python api_test_agent.py run tests/my_first_test.yaml --reports html
```

### 查看报告

生成的 HTML 报告在 `reports/` 目录下，双击即可打开。

---

## 🎯 核心功能

### 1. 多种 HTTP 方法

```yaml
- name: "POST 请求"
  method: POST
  endpoint: "/users"
  json:
    name: "张三"
    email: "zhang@example.com"
  
  assertions:
    - type: status_code
      expected: 201
```

### 2. 变量提取与传递

```yaml
steps:
  # 登录并提取 Token
  - name: "登录"
    method: POST
    endpoint: "/login"
    json: { "username": "test", "password": "pass" }
    extract:
      token: "data.token"
  
  # 使用 Token 调用受保护接口
  - name: "获取资源"
    method: GET
    endpoint: "/resource"
    headers:
      Authorization: "Bearer ${token}"
```

### 3. 丰富的断言类型

| 断言类型 | 说明 | 参数 |
|---------|------|------|
| `status_code` | HTTP 状态码检查 | `expected: 200` |
| `equal` | 值相等性 | `path: "id", expected: 1` |
| `contains_key` | 键存在性 | `key: "token"` |
| `type_check` | 数据类型 | `expected_type: str` |
| `length` | 长度检查 | `expected: 10` |
| `response_time` | 响应时间 | `max: 3.0` |
| `regex_match` | 正则匹配 | `pattern: "^\d+$"` |

完整文档参考 [`SKILL.md`](SKILL.md)

---

## ️ 命令行工具

```bash
# 运行单个测试文件
python api_test_agent.py run test.yaml

# 运行目录下所有测试
python api_test_agent.py run tests/

# 指定报告格式
python api_test_agent.py run tests/ --reports html,json

# 指定 API 基础 URL
python api_test_agent.py run tests/ --base-url https://api.example.com

# 查看详细日志
python api_test_agent.py run tests/ --verbose --timeout 60
```

---

## 🐍 Python API

```python
from test_runner import TestRunner
from report_generator import ReportGenerator

# 初始化 runner
runner = TestRunner(base_url="https://api.example.com")

# 执行测试
result = runner.execute_test_file("tests/test.yaml")

# 生成报告
ReportGenerator().generate_html_report(result)

# 关闭连接
runner.close()
```

---

## 📊 测试报告

生成三种格式的测试报告：

- **HTML** - 美观的交互式报告（推荐）
- **Markdown** - 轻量级文本报告
- **JSON** - 结构化数据报告

---

## 🔧 CI/CD 集成

### GitHub Actions

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python api_test_agent.py run tests/ --reports junit
      - uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: reports/
```

---

## 📚 完整文档

| 文档 | 说明 |
|------|------|
| [快速开始.md](快速开始.md) | 5 分钟入门指南 |
| [使用教程.md](使用教程.md) | 完整交互式教程（1.2 万字） |
| [SKILL.md](SKILL.md) | 详细技能文档 |
| [CHEATSHEET.md](CHEATSHEET.md) | 速查卡片 |
| [使用说明.md](使用说明.md) | 中文使用手册 |

---

## 🤝 贡献指南

欢迎提交 PR！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

### 开发流程

```bash
# 1. Fork 仓库
# 2. Clone 到本地
git clone https://github.com/YOUR_USERNAME/api-test-agent.git

# 3. 创建功能分支
git checkout -b feature/new-feature

# 4. 开发并提交
git add .
git commit -m "feat: 添加新功能"

# 5. Push 到 GitHub 并创建 Pull Request
git push origin feature/new-feature
```

---

## 📋 版本计划

| 版本 | 预计时间 | 主要功能 |
|------|---------|---------|
| v1.0 | ✅ 已发布 | 核心功能完成 |
| v1.1 | 2026-06 | 新增断言类型、前后置钩子 |
| v1.2 | 2026-08 | 并发执行、数据驱动测试 |
| v1.5 | 2026-09 | GUI 编辑器 |
| v2.0 | 2026-11 | GraphQL/WebSocket支持 |

详情参考 [`docs-management/项目计划.md`](docs-management/项目计划.md)

---

## 🆘 问题反馈

遇到问题？请：

1. 搜索 [Issues](https://github.com/qwenpaw/api-test-agent/issues) 是否有类似问题
2. 新建 Issue 时提供详细信息
3. 包含复现步骤和错误日志

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## ⭐ Star History

感谢给本项目点个 Star 的支持！

[![Star History Chart](https://api.star-history.com/svg?repos=qwenpaw/api-test-agent&type=Date)](https://star-history.com/#qwenpaw/api-test-agent&Date)

---

Made with ❤️ by QwenPaw Team
