# API 接口自动化测试 Agent 技能文档

## 🚀 概述

这是一个完整的 API 接口自动化测试框架，支持：

- ✅ 多种 HTTP 请求方法（GET, POST, PUT, DELETE, PATCH）
- ✅ 强大的断言引擎（状态码、响应内容、响应时间等）
- ✅ 灵活的测试用例定义（YAML/JSON 格式）
- ✅ 测试变量管理和传递
- ✅ 多格式报告生成（HTML, Markdown, JSON）
- ✅ 命令行和 Python API 双模式

## 📁 项目结构

```
api-test-agent/
├── api_test_agent.py     # 主程序（CLI + Python API）
├── config.py             # 配置管理
├── api_client.py         # API 客户端封装
├── assert_engine.py      # 断言引擎
├── test_runner.py        # 测试执行器
├── report_generator.py   # 报告生成器
├── utils.py              # 工具函数
├── requirements.txt      # Python 依赖
├── README.md            # 使用说明
├── SKILL.md             # 本文档
├── examples/
│   └── sample_tests.yaml # 示例测试用例
└── reports/             # 报告输出目录
```

## 🛠️ 安装

### 1. 安装依赖

```bash
cd D:\qwenpaw\workspaces\default\output\api-test-agent
pip install -r requirements.txt
```

### 2. 验证安装

```bash
python api_test_agent.py --help
```

## 💡 快速开始

### 方式一：使用命令行

#### 运行单个测试文件

```bash
python api_test_agent.py run tests/sample_test.yaml
```

#### 运行目录下所有测试

```bash
python api_test_agent.py run tests/
```

#### 指定报告格式

```bash
python api_test_agent.py run tests/ --reports html,json,markdown
```

#### 指定 API 基础 URL

```bash
python api_test_agent.py run tests/ --base-url https://api.example.com
```

### 方式二：Python API

```python
from test_runner import TestRunner
from report_generator import ReportGenerator

# 初始化测试 runner
runner = TestRunner(base_url="https://api.example.com")

# 执行测试文件
result = runner.execute_test_file("tests/sample_test.yaml")

# 生成报告
generator = ReportGenerator(output_dir="reports")
generator.generate_html_report(result)

# 关闭连接
runner.close()
```

## 📝 编写测试用例

### 基本结构

```yaml
name: "用户登录测试"
description: "测试用户登录功能"

variables:
  username: "test@example.com"
  password: "password123"

steps:
  # 步骤 1: 登录获取 token
  - name: "用户登录"
    method: POST
    endpoint: "/api/v1/login"
    json:
      email: "${username}"
      password: "${password}"
    
    assertions:
      - type: status_code
        expected: 200
        name: "状态码检查"
      
      - type: contains_key
        key: "token"
        path: "$"
        name: "返回 token"
    
    # 提取 token 供后续步骤使用
    extract:
      access_token:
        path: "token"

  # 步骤 2: 使用 token 访问受保护资源
  - name: "获取用户信息"
    method: GET
    endpoint: "/api/v1/users/me"
    headers:
      Authorization: "Bearer ${access_token}"
    
    assertions:
      - type: status_code
        expected: 200
      
      - type: contains_key
        key: "email"
        path: "$"
      
      - type: equal
        path: "email"
        expected: "${username}"
```

### 支持的断言类型

| 断言类型 | 说明 | 参数 |
|---------|------|------|
| status_code | HTTP 状态码检查 | expected |
| equal | 值相等检查 | path, expected |
| not_equal | 值不等检查 | path, expected |
| contains | 容器包含检查 | path, value |
| not_contains | 容器不包含检查 | path, value |
| contains_key | 字典键存在检查 | path, key |
| type_check | 类型检查 | path, expected_type |
| length | 长度检查 | path, expected |
| regex_match | 正则匹配 | path, pattern |
| response_time | 响应时间检查 | min, max |

### 环境变量引用

使用 `${variable_name}` 引用变量：

```yaml
steps:
  - name: "请求"
    endpoint: "${API_BASE_URL}/users/${user_id}"
    headers:
      Authorization: "Bearer ${AUTH_TOKEN}"
```

### 变量提取与传递

```yaml
steps:
  - name: "登录"
    ...
    extract:
      token:
        path: "data.token"
      user_id:
        path: "data.user.id"
  
  - name: "获取用户详情"
    endpoint: "/users/${user_id}"  # 使用上一步的变量
    headers:
      Authorization: "Bearer ${token}"
```

## 🔧 配置文件

### config.json 配置项

```json
{
  "base_url": "https://api.example.com",
  "timeout": 30,
  "retry_times": 3,
  "retry_delay": 1,
  "headers": {
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  "test_dir": "tests",
  "report_dir": "reports",
  "log_level": "INFO",
  "log_file": "api_test.log"
}
```

## 📊 报告格式

### HTML 报告
- 美观的可视化界面
- 交互式展开/折叠
- 实时进度条
- 适合演示和分享

### Markdown 报告
- 轻量级文本格式
- 易于阅读和版本控制
- 支持 GitHub/GitLab

### JSON 报告
- 结构化数据
- 便于集成到其他系统
- 支持 CI/CD 流水线

## 🧪 示例场景

### 1. REST API 测试

```yaml
name: "用户 CRUD 操作"
steps:
  # 创建用户
  - name: "创建用户"
    method: POST
    endpoint: "/api/users"
    json:
      name: "张三"
      email: "zhangsan@example.com"
    extract:
      user_id: "id"
    assertions:
      - type: status_code
        expected: 201
  
  # 查询用户
  - name: "获取用户详情"
    method: GET
    endpoint: "/api/users/${user_id}"
    assertions:
      - type: status_code
        expected: 200
      - type: equal
        path: "name"
        expected: "张三"
  
  # 更新用户
  - name: "更新用户"
    method: PUT
    endpoint: "/api/users/${user_id}"
    json:
      name: "李四"
    assertions:
      - type: status_code
        expected: 200
  
  # 删除用户
  - name: "删除用户"
    method: DELETE
    endpoint: "/api/users/${user_id}"
    assertions:
      - type: status_code
        expected: 204
```

### 2. 认证授权测试

```yaml
name: "JWT 认证流程"
steps:
  # 获取访问令牌
  - name: "获取 Access Token"
    method: POST
    endpoint: "/oauth/token"
    data:
      grant_type: "client_credentials"
      client_id: "${CLIENT_ID}"
      client_secret: "${CLIENT_SECRET}"
    extract:
      access_token: "access_token"
      expires_in: "expires_in"
    assertions:
      - type: status_code
        expected: 200
  
  # 调用受保护的 API
  - name: "调用受保护接口"
    method: GET
    endpoint: "/api/v1/profile"
    headers:
      Authorization: "Bearer ${access_token}"
    assertions:
      - type: status_code
        expected: 200
```

## 📖 CLI 命令参考

### 帮助
```bash
python api_test_agent.py --help
python api_test_agent.py run --help
```

### 初始化项目
```bash
python api_test_agent.py init -d my-api-tests
```

### 运行测试
```bash
# 基本用法
python api_test_agent.py run <path>

# 完整选项
python api_test_agent.py run tests/ \
  -o custom_reports \
  -r html,json \
  --base-url https://api.example.com \
  -t 60 \
  -v
```

### 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| path | - | 测试文件或目录路径 | (必填) |
| --output | -o | 报告输出目录 | reports |
| --reports | -r | 报告格式 | html,markdown,json |
| --verbose | -v | 显示详细信息 | False |
| --base-url | - | API 基础 URL | 配置文件 |
| --timeout | -t | 请求超时时间 | 30 |

## 🔐 安全建议

1. **不要将敏感信息提交到代码仓库**
   - 使用环境变量替代硬编码的密钥
   - 将 credentials 放在配置文件中并加入 .gitignore

2. **限制生产环境访问**
   - 测试环境使用独立账号
   - 避免在生产环境执行破坏性操作

3. **定期审查日志**
   - 确保不泄露敏感数据
   - 监控异常行为

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可证

MIT License
