# 📘 API Test Agent v2.0 - Phase 2 新功能使用指南

> 本文档介绍 v2.1.0-alpha 新增的三大核心功能：性能测试、认证增强、断言增强。

---

## 目录

- [一、性能测试](#一性能测试)
  - [1.1 快速开始](#11-快速开始)
  - [1.2 CLI 参数说明](#12-cli-参数说明)
  - [1.3 两种测试模式](#13-两种测试模式)
  - [1.4 RPS 控制](#14-rps-控制)
  - [1.5 阈值告警](#15-阈值告警)
  - [1.6 性能报告](#16-性能报告)
  - [1.7 使用示例](#17-使用示例)
- [二、认证增强](#二认证增强)
  - [2.1 OAuth 2.0](#21-oauth-20)
  - [2.2 JWT 管理](#22-jwt-管理)
  - [2.3 API Key 认证](#23-api-key-认证)
  - [2.4 HMAC 签名认证](#24-hmac-签名认证)
  - [2.5 Basic Auth](#25-basic-auth)
  - [2.6 AuthManager 统一管理](#26-authmanager-统一管理)
- [三、断言增强](#三断言增强)
  - [3.1 JSON Schema 验证](#31-json-schema-验证)
  - [3.2 自定义断言](#32-自定义断言)
  - [3.3 数据库断言](#33-数据库断言)
  - [3.4 组合使用示例](#34-组合使用示例)

---

## 一、性能测试

API Test Agent v2.0 新增了完整的性能测试能力，可以对 API 进行负载测试、压力测试和性能基准测试。

### 1.1 快速开始

最简单的使用方式：

```bash
# 对 API 进行 30 秒的负载测试，使用 10 个并发用户
python api_test_agent.py perf /users \
  --base-url https://jsonplaceholder.typicode.com \
  -d 30 -c 10

# 固定次数模式：发送 100 次请求
python api_test_agent.py perf /users \
  --base-url https://jsonplaceholder.typicode.com \
  -i 100
```

### 1.2 CLI 参数说明

| 参数 | 短参数 | 说明 | 默认值 |
|------|--------|------|--------|
| `endpoint` | - | 要测试的 API 端点（必填） | - |
| `--method` | `-m` | HTTP 方法 | `GET` |
| `--duration` | `-d` | 测试持续时间（秒） | `60` |
| `--rps` | `-r` | 目标 RPS（每秒请求数） | `无限制` |
| `--concurrent` | `-c` | 并发用户数 | `10` |
| `--ramp-up` | - | 爬坡时间（秒） | `0` |
| `--iterations` | `-i` | 固定次数模式（与 --duration 互斥） | - |
| `--thresholds` | - | 阈值配置文件路径 | - |
| `--base-url` | - | API 基础 URL | - |
| `--output` | `-o` | 报告输出目录 | `reports/` |

### 1.3 两种测试模式

#### 模式 A：持续时间模式（默认）

```bash
# 持续 60 秒，50 个并发用户，不限速
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -d 60 -c 50

# 持续 30 秒，20 个并发用户，限制 RPS 为 100
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -d 30 -c 20 -r 100
```

#### 模式 B：固定次数模式

```bash
# 发送 1000 次 GET 请求
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -i 1000

# 发送 500 次 POST 请求（带 JSON body）
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -i 500 -m POST
```

### 1.4 RPS 控制

通过 `--rps` 参数可以精确控制每秒请求数：

```bash
# 控制 RPS 为 50（即每秒发送 50 个请求）
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -d 60 -r 50 -c 20
```

**工作原理**：内部使用 `RateLimiter` 实现令牌桶算法，确保请求间隔符合目标 RPS。

### 1.5 阈值告警

创建阈值配置文件 `thresholds.yaml`：

```yaml
# thresholds.yaml
thresholds:
  - name: "P95 响应时间"
    metric: "p95"
    operator: "<"
    value: 2.0  # 2 秒
    severity: "critical"

  - name: "P99 响应时间"
    metric: "p99"
    operator: "<"
    value: 5.0  # 5 秒
    severity: "warning"

  - name: "错误率"
    metric: "error_rate"
    operator: "<"
    value: 0.05  # 5%
    severity: "critical"

  - name: "最小 RPS"
    metric: "rps"
    operator: ">="
    value: 100.0
    severity: "warning"
```

运行测试时指定阈值文件：

```bash
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -d 60 -c 20 \
  --thresholds thresholds.yaml
```

**输出示例**：

```
======================================================================
性能测试报告
======================================================================

执行时间: 2026-05-01 15:30:00 - 2026-05-01 15:31:00
总耗时: 60.00s

请求统计:
  总请求数: 6000
  成功: 5950
  失败: 50
  错误率: 0.83%

响应时间分布:
  最小: 50.00ms
  平均: 120.50ms
  中位数 (P50): 110.00ms
  P90: 180.00ms
  P95: 220.00ms
  P99: 350.00ms
  最大: 800.00ms

吞吐量:
  RPS: 100.00
  吞吐量: 1250.00 KB/s

状态码分布:
  200: 5950
  500: 50

✅ 所有阈值检查通过
======================================================================
```

### 1.6 性能报告

测试完成后会自动生成 JSON 格式的性能报告：

```
reports/perf_report_20260501_153000.json
```

报告内容包括：
- 请求统计（总数、成功、失败、错误率）
- 响应时间分布（min/avg/median/P90/P95/P99/max）
- 吞吐量（RPS、bytes/s）
- 状态码分布
- 端点级性能分析
- 阈值违规记录

### 1.7 使用示例

#### 示例 1：基准测试

```bash
# 获取 API 的性能基线
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -i 1000 -c 10
```

#### 示例 2：负载测试

```bash
# 模拟 100 个用户同时访问
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -d 300 -c 100 -r 500 \
  --thresholds thresholds.yaml
```

#### 示例 3：爬坡测试

```bash
# 5 秒内逐渐增加到 50 个并发用户
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -d 120 -c 50 --ramp-up 5
```

#### 示例 4：POST 请求压测

```bash
# 持续发送 POST 请求测试写入性能
python api_test_agent.py perf /api/users \
  --base-url https://api.example.com \
  -m POST -d 60 -c 20
```

#### 示例 5：Python 代码调用

```python
from api_test_agent import LoadTester, LoadTestConfig

# 初始化负载测试器
tester = LoadTester(base_url="https://api.example.com")

# 配置负载测试
config = LoadTestConfig(
    endpoint="/api/users",
    method="GET",
    duration=60.0,
    rps=100.0,
    concurrent_users=20,
    thresholds=[
        {"metric": "p95", "operator": "<", "value": 2.0, "severity": "critical"}
    ]
)

# 执行测试
result = tester.run_load_test(config)

# 查看结果
print(f"总请求数: {result.total_requests}")
print(f"实际 RPS: {result.actual_rps}")
print(f"平均响应时间: {result.metrics.avg_response_time * 1000:.2f}ms")
print(f"P95 响应时间: {result.metrics.p95_response_time * 1000:.2f}ms")
```

---

## 二、认证增强

API Test Agent v2.0 新增了完整的认证管理能力，支持 OAuth 2.0、JWT、API Key、HMAC 等多种认证方式。

### 2.1 OAuth 2.0

#### Client Credentials 流程

```python
from api_test_agent import OAuth2Client, AuthManager

# 初始化认证管理器
auth_mgr = AuthManager()

# 使用 Client Credentials 流程获取 token
token_info = OAuth2Client.client_credentials_flow(
    token_url="https://auth.example.com/oauth/token",
    client_id="your_client_id",
    client_secret="your_client_secret",
    scope="read write",
    auth_manager=auth_mgr,
    token_name="my_oauth2"
)

# 获取认证头
headers = auth_mgr.get_auth_headers("my_oauth2")
# 输出: {"Authorization": "Bearer <access_token>"}
```

#### Resource Owner Password 流程

```python
from api_test_agent import OAuth2Client

token_info = OAuth2Client.password_flow(
    token_url="https://auth.example.com/oauth/token",
    client_id="your_client_id",
    client_secret="your_client_secret",
    username="user@example.com",
    password="user_password",
    scope="read",
    auth_manager=auth_mgr,
    token_name="my_oauth2"
)
```

#### 自动刷新 Token

```python
from api_test_agent import OAuth2Client, AuthManager

auth_mgr = AuthManager()

# 获取初始 token
token_info = OAuth2Client.password_flow(
    token_url="https://auth.example.com/oauth/token",
    client_id="client_id",
    client_secret="client_secret",
    username="user",
    password="password",
    auth_manager=auth_mgr,
    token_name="my_oauth2"
)

# 注册刷新回调
def refresh_oauth2_token():
    return OAuth2Client.refresh_token_flow(
        token_url="https://auth.example.com/oauth/token",
        client_id="client_id",
        client_secret="client_secret",
        refresh_token=token_info.refresh_token,
        auth_manager=auth_mgr,
        token_name="my_oauth2"
    )

auth_mgr.register_token("my_oauth2", token_info, refresh_callback=refresh_oauth2_token)

# 使用时自动检查过期并刷新
token = auth_mgr.get_token("my_oauth2")
```

### 2.2 JWT 管理

#### 创建 JWT Token

```python
from api_test_agent import JWTManager

# 创建 JWT
token = JWTManager.create_jwt(
    payload={
        "user_id": 12345,
        "role": "admin",
        "permissions": ["read", "write"]
    },
    secret_key="your_secret_key",
    algorithm="HS256",
    expires_in=3600,  # 1 小时
    issuer="api-test-agent",
    audience="api.example.com"
)

print(f"JWT Token: {token}")
```

#### 解码和验证 JWT

```python
from api_test_agent import JWTManager

# 解码 JWT（验证签名）
payload = JWTManager.decode_jwt(token, secret_key="your_secret_key")
print(f"User ID: {payload['user_id']}")
print(f"Role: {payload['role']}")

# 仅检查是否过期（无需密钥）
is_expired = JWTManager.is_expired(token)
print(f"Token 已过期: {is_expired}")

# 提取载荷（不验证签名）
payload = JWTManager.extract_payload(token)
print(f"载荷: {payload}")
```

### 2.3 API Key 认证

#### Header 模式（默认）

```yaml
# 在测试用例中配置
steps:
  - name: "使用 API Key 访问"
    method: "GET"
    endpoint: "/api/data"
    auth:
      type: "api_key"
      api_key: "your_api_key_here"
      key_name: "X-API-Key"
      key_location: "header"
```

#### Query 模式

```yaml
auth:
  type: "api_key"
  api_key: "your_api_key"
  key_name: "api_key"
  key_location: "query"
# 结果: GET /api/data?api_key=your_api_key
```

#### Cookie 模式

```yaml
auth:
  type: "api_key"
  api_key: "your_api_key"
  key_name: "session_id"
  key_location: "cookie"
# 结果: Cookie: session_id=your_api_key
```

### 2.4 HMAC 签名认证

```yaml
# 在测试用例中配置
steps:
  - name: "使用 HMAC 签名访问"
    method: "POST"
    endpoint: "/api/secure-endpoint"
    auth:
      type: "hmac"
      access_key: "your_access_key"
      secret_key: "your_secret_key"
```

**自动生成的请求头**：
- `X-HMAC-Signature`: SHA256 签名
- `X-HMAC-Timestamp`: 当前时间戳
- `X-HMAC-Access-Key`: Access Key

### 2.5 Basic Auth

```yaml
# 在测试用例中配置
steps:
  - name: "使用 Basic Auth 访问"
    method: "GET"
    endpoint: "/api/admin"
    auth:
      type: "basic"
      username: "admin"
      password: "password123"
```

### 2.6 AuthManager 统一管理

```python
from api_test_agent import AuthManager, TestRunner, APIClient

# 初始化认证管理器
auth_mgr = AuthManager()

# 注册多个 token
auth_mgr.register_token("oauth2", oauth2_token_info)
auth_mgr.register_token("jwt", jwt_token_info)
auth_mgr.register_token("api_key", api_key_token_info)

# 在测试中使用
client = APIClient(base_url="https://api.example.com")

# 自动应用认证
request_kwargs = {"endpoint": "/api/users", "method": "GET"}
auth_mgr.apply_auth(request_kwargs, {"type": "oauth2", "token_name": "oauth2"})

# 发送请求
response = client.get(**request_kwargs)
```

---

## 三、断言增强

API Test Agent v2.0 新增了 3 种高级断言类型，让您可以验证更复杂的场景。

### 3.1 JSON Schema 验证

#### 基本用法

```yaml
steps:
  - name: "获取用户列表"
    method: "GET"
    endpoint: "/users"
    assertions:
      - type: "status_code"
        expected: 200
      
      - type: "json_schema"
        name: "验证响应结构"
        schema:
          type: "object"
          required: ["users", "total", "page"]
          properties:
            users:
              type: "array"
              minItems: 1
              items:
                type: "object"
                required: ["id", "name", "email"]
                properties:
                  id:
                    type: "integer"
                    minimum: 1
                  name:
                    type: "string"
                    minLength: 1
                  email:
                    type: "string"
                    pattern: "^[\\w.-]+@[\\w.-]+\\.\\w+$"
            total:
              type: "integer"
              minimum: 0
            page:
              type: "integer"
              minimum: 1
```

#### 支持的 Schema 关键字

| 类别 | 关键字 | 说明 |
|------|--------|------|
| **类型** | `type` | string/number/integer/boolean/array/object/null |
| **对象** | `required` | 必填字段列表 |
| | `properties` | 字段定义 |
| **数组** | `items` | 数组元素定义 |
| | `minItems` / `maxItems` | 数组长度限制 |
| **字符串** | `minLength` / `maxLength` | 字符串长度 |
| | `pattern` | 正则表达式 |
| **数字** | `minimum` / `maximum` | 数值范围 |
| | `enum` | 枚举值 |

### 3.2 自定义断言

#### 基本用法

```yaml
steps:
  - name: "获取产品列表"
    method: "GET"
    endpoint: "/api/products"
    assertions:
      - type: "custom"
        name: "检查产品价格范围"
        script: |
          # 可用变量：response（整个响应体），value（提取的值）
          products = value.get("products", [])
          
          # 检查所有产品价格 > 0
          invalid = [p for p in products if p.get("price", 0) <= 0]
          
          if invalid:
              result = (False, f"发现 {len(invalid)} 个产品价格无效")
          else:
              result = (True, "所有产品价格均有效")
```

#### 布尔值返回

```yaml
      - type: "custom"
        name: "简单检查"
        script: |
          result = value.get("status") == "success"
```

### 3.3 数据库断言

> **注意**：数据库断言需要从外部注入查询结果，通常通过钩子或自定义代码执行 SQL 查询后传入。

```yaml
steps:
  - name: "创建用户并验证数据库"
    method: "POST"
    endpoint: "/users"
    json:
      name: "测试用户"
      email: "test@example.com"
    assertions:
      - type: "database"
        name: "验证用户已插入数据库"
        query_result: "[{'id': 1, 'name': '测试用户', 'email': 'test@example.com'}]"
        expected_rows: 1
        expected_value: "test@example.com"
        path: "$[0].email"
```

### 3.4 组合使用示例

```yaml
name: "完整验证用户创建"
steps:
  - name: "创建用户"
    method: "POST"
    endpoint: "/users"
    json:
      name: "张三"
      email: "zhangsan@example.com"
      age: 25
    assertions:
      # HTTP 层断言
      - type: "status_code"
        expected: 201
      
      - type: "response_time"
        max: 1.0
      
      # JSON Schema 验证
      - type: "json_schema"
        name: "验证响应结构"
        schema:
          type: "object"
          required: ["id", "name", "email"]
          properties:
            id:
              type: "integer"
            name:
              type: "string"
            email:
              type: "string"
      
      # 值断言
      - type: "equal"
        path: "name"
        expected: "张三"
      
      - type: "contains_key"
        key: "id"
      
      # 自定义断言
      - type: "custom"
        name: "验证 ID 为正数"
        path: "id"
        script: |
          result = value > 0
```

---

## 附录：Phase 2 新增模块清单

| 模块 | 文件 | 说明 |
|------|------|------|
| 性能指标收集 | `src/api_test_agent/perf_collector.py` | 收集、计算、导出性能指标 |
| 负载测试执行 | `src/api_test_agent/perf_tester.py` | 执行负载测试，支持 RPS 控制 |
| 认证管理 | `src/api_test_agent/auth_manager.py` | 统一管理各种认证方式 |
| JSON Schema 断言 | `src/api_test_agent/assertions.py` | 新增 json_schema 方法 |
| 自定义断言 | `src/api_test_agent/assertions.py` | 新增 custom 方法 |
| 数据库断言 | `src/api_test_agent/assertions.py` | 新增 database 方法 |

---

**API Test Agent v2.1.0-alpha** - 让 API 测试更强大！🚀
