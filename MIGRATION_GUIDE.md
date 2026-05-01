# 从 v1.0 迁移到 v2.0

> **API Test Agent v2.0 完全向后兼容！** 您现有的 v1.0 测试用例无需任何修改即可在 v2.0 中运行。

---

## 📋 目录

- [迁移概述](#迁移概述)
- [向后兼容性保证](#向后兼容性保证)
- [v2.0 新功能一览](#v20-新功能一览)
- [逐步升级指南](#逐步升级指南)
  - [步骤 1：环境管理（可选）](#步骤-1环境管理可选)
  - [步骤 2：钩子系统（可选）](#步骤-2钩子系统可选)
  - [步骤 3：数据驱动测试（可选）](#步骤-3数据驱动测试可选)
  - [步骤 4：并发执行（可选）](#步骤-4并发执行可选)
- [迁移前后对比示例](#迁移前后对比示例)
- [常见问题 FAQ](#常见问题-faq)

---

## 迁移概述

### v2.0 的设计原则

✅ **零破坏性变更** - 所有 v1.0 功能保持不变  
✅ **渐进式采用** - 新功能均为可选，按需启用  
✅ **平滑过渡路径** - 可逐步迁移，无需一次性重构  

### 升级收益

| 能力 | v1.0 | v2.0 |
|------|------|------|
| 环境切换 | 手动修改配置文件 | `--env staging` 一键切换 |
| 敏感信息 | 硬编码或手动处理 | `.env` 文件自动加载 + 脱敏显示 |
| 前后置操作 | 不支持 | 完整的钩子生命周期 |
| 参数化测试 | 手动复制用例 | CSV/JSON 数据驱动，自动生成 |
| 执行效率 | 串行执行 | 多线程并发，3-5x 加速 |

---

## 向后兼容性保证

### ✅ 无需修改的现有代码

您的以下代码**完全不需要修改**：

```yaml
# 您的现有测试用例 - 在 v2.0 中直接运行
- name: "获取用户列表"
  steps:
    - name: "GET /users"
      method: GET
      endpoint: "https://api.example.com/users"
      
      assertions:
        - type: status_code
          expected: 200
```

```bash
# 现有命令继续有效
python api_test_agent.py run tests/ --reports html
python api_test_agent.py run test.yaml --base-url https://api.example.com
```

### ✅ 保持不变的核心 API

- `TestRunner` 类的所有公共方法
- `APIClient` 类的所有方法
- 断言引擎的所有断言类型
- 报告生成器的所有格式
- 配置文件的 JSON 格式

---

## v2.0 新功能一览

### 1️⃣ 环境管理（Environment Management）

**解决的问题**：在不同环境（dev/staging/prod）间切换时需要手动修改 URL 和配置

**核心能力**：
- 多环境 YAML 配置（`configs/environments.yaml`）
- `.env` 文件支持敏感信息
- 命令行一键切换：`--env staging`
- 配置校验和脱敏显示

**适用场景**：
- 本地开发 vs 测试环境 vs 生产环境
- 团队协作时统一环境配置
- CI/CD 流水线中动态切换环境

---

### 2️⃣ 钩子系统（Hook System）

**解决的问题**：无法在测试前后自动执行初始化或清理操作

**核心能力**：
- 五阶段生命周期：global_setup → setup → steps → teardown → global_teardown
- 三种钩子类型：HTTP / Command / Script
- 变量提取与跨钩子传递
- 条件执行和失败控制

**适用场景**：
- 测试前创建测试数据（用户、文章等）
- 测试后清理临时资源
- 执行数据库迁移或初始化脚本
- 发送通知或记录日志

---

### 3️⃣ 数据驱动测试（Data-Driven Testing）

**解决的问题**：相同逻辑不同数据的测试需要大量重复编写用例

**核心能力**：
- CSV / JSON 外部数据源
- 模板参数化（`${data.column}`）
- 自动批量生成测试用例
- 动态命名和过滤条件

**适用场景**：
- 登录测试（多组账号密码）
- 边界值测试（正常/异常/边界输入）
- 表单验证（多种组合）
- API 兼容性测试（不同版本参数）

---

### 4️⃣ 并发执行（Concurrency）

**解决的问题**：大量测试用例串行执行耗时过长

**核心能力**：
- 多线程并行执行（`-w N`）
- 变量上下文隔离
- 结果聚合和加速比统计
- 异步执行框架

**适用场景**：
- 大规模回归测试套件
- 独立用例的并行化
- CI/CD 中缩短测试时间

---

## 逐步升级指南

### 步骤 1：环境管理（可选）

#### 1.1 创建环境配置文件

```bash
# 复制示例配置
mkdir -p configs
cp examples/v2_environment/../configs/environments.yaml configs/
```

#### 1.2 编辑环境配置

```yaml
# configs/environments.yaml
defaults:
  timeout: 30
  headers:
    Content-Type: "application/json"

environments:
  dev:
    base_url: http://localhost:8080/api
    timeout: 10
    
  staging:
    base_url: https://staging-api.example.com/api
    
  prod:
    base_url: https://api.example.com/api
    timeout: 60
```

#### 1.3 创建 .env 文件（如需敏感信息）

```bash
# 复制模板并编辑
cp configs/.env.example configs/.env
vim configs/.env  # 填入真实值
```

#### 1.4 使用环境变量

**迁移前（v1.0）：**
```yaml
steps:
  - name: "登录"
    method: POST
    endpoint: "https://staging-api.example.com/auth/login"  # 硬编码
```

**迁移后（v2.0）：**
```yaml
steps:
  - name: "登录"
    method: POST
    endpoint: "${base_url}/auth/login"  # 动态引用
```

```bash
# 运行时指定环境
python api_test_agent.py run tests/ --env staging
```

---

### 步骤 2：钩子系统（可选）

#### 2.1 添加全局钩子（推荐在测试文件中定义）

```yaml
# 在测试文件顶部添加
global_setup:
  - name: "初始化测试数据库"
    type: http
    method: POST
    endpoint: "${base_url}/tests/init"
    
global_teardown:
  - name: "清理测试数据"
    type: command
    command: "python cleanup_tests.py"
    ignore_failure: true
```

#### 2.2 为单个用例添加 setup/teardown

**迁移前（v1.0 - 无前后置操作）：**
```yaml
- name: "测试文章 CRUD"
  steps:
    - name: "创建文章"  # 但没有清理...
      method: POST
      endpoint: "/posts"
      json: {title: "test"}
```

**迁移后（v2.0 - 带完整生命周期）：**
```yaml
- name: "测试文章 CRUD"
  
  setup:
    - name: "创建测试文章"
      type: http
      method: POST
      endpoint: "${base_url}/posts"
      json: {title: "test"}
      extract:
        post_id: "data.id"
  
  steps:
    - name: "获取文章"
      method: GET
      endpoint: "${base_url}/posts/${post_id}"
      
  teardown:
    - name: "删除测试文章"
      type: http
      method: DELETE
      endpoint: "${base_url}/posts/${post_id}"
      ignore_failure: true  # 清理失败不影响结果
```

---

### 步骤 3：数据驱动测试（可选）

#### 3.1 准备数据文件

**CSV 格式（test_data/login_cases.csv）：**
```csv
username,password,expected_status,test_name
admin,Admin123,200,正常登录
testuser,WrongPass,401,密码错误
empty,,400,空密码
```

**JSON 格式（test_data/register_cases.json）：**
```json
[
  {
    "username": "user1",
    "email": "user1@test.com",
    "expected_status": 201,
    "profile": {"nickname": "用户1"}
  }
]
```

#### 3.2 创建数据驱动测试模板

```yaml
data_source:
  type: csv
  file: test_data/login_cases.csv
  case_name_template: "登录_${data.test_name}"

template:
  steps:
    - name: "执行登录"
      method: POST
      endpoint: "${base_url}/auth/login"
      json:
        username: "${data.username}"
        password: "${data.password}"
      
      assertions:
        - type: status_code
          expected: "${data.expected_status}"
```

#### 3.3 对比效果

**迁移前（v1.0 - 需要手写多个用例）：**
```yaml
# 用例 1：正常登录
- name: "登录测试-正常"
  steps:
    - method: POST
      endpoint: "/login"
      json: {username: "admin", password: "Admin123"}

# 用例 2：密码错误
- name: "登录测试-密码错误"
  steps:
    - method: POST
      endpoint: "/login"
      json: {username: "admin", password: "wrong"}

# 用例 3... (重复多次)
```

**迁移后（v2.0 - 一个模板 + 数据文件）：**
```yaml
# 只需要一个模板，自动从 CSV 生成所有用例
data_source:
  type: csv
  file: login_cases.csv
  
template:
  steps:
    - method: POST
      endpoint: "/login"
      json:
        username: "${data.username}"
        password: "${data.password}"
```

---

### 步骤 4：并发执行（可选）

#### 4.1 启用并发

```bash
# 使用 4 个工作线程并发执行
python api_test_agent.py run tests/ --env staging -w 4

# 根据 CPU 核心数自动设置（通常为核数 * 2）
python api_test_agent.py run tests/ -w 8
```

#### 4.2 性能对比

| 场景 | 串行（v1.0） | 并发 4 线程（v2.0） | 加速比 |
|------|--------------|-------------------|--------|
| 100 个简单用例 | ~50s | ~15s | **3.3x** |
| 50 个复杂用例 | ~120s | ~35s | **3.4x** |
| 10 个超时用例 | ~300s | ~80s | **3.75x** |

> ⚠️ 注意：并发数不宜过大，建议 2-8 个，避免压垮被测服务

---

## 迁移前后对比示例

### 示例 1：简单的 API 测试

**v1.0 方式：**
```yaml
# simple_test.yaml
- name: "获取用户"
  steps:
    - name: "GET /users/1"
      method: GET
      endpoint: "https://api.example.com/users/1"
      assertions:
        - type: status_code
          expected: 200
```

```bash
python api_test_agent.py run simple_test.yaml
```

**v2.0 方式（增强版，完全兼容）：**
```yaml
# enhanced_test.yaml（使用新功能但非必须）
- name: "获取用户"
  steps:
    - name: "GET /users/1"
      method: GET
      endpoint: "${base_url}/users/1"  # 可选：使用环境变量
      assertions:
        - type: status_code
          expected: 200
```

```bash
# 方式 A：传统方式（仍然有效）
python api_test_agent.py run enhanced_test.yaml

# 方式 B：使用环境管理（新增能力）
python api_test_agent.py run enhanced_test.yaml --env staging
```

---

### 示例 2：带数据准备的测试

**v1.0 方式（手动准备数据）：**
```yaml
# manual_test.yaml
- name: "完整流程测试"
  description: |
    1. 先手动创建测试用户（通过 Postman 或其他工具）
    2. 记录下 user_id 和 token
    3. 硬编码到下面的测试中
    
  steps:
    - name: "使用硬编码的用户 ID"
      method: GET
      endpoint: "https://api.example.com/users/12345"  # 手动填入
      
    - name: "测试完成后记得手动清理"
      method: DELETE
      endpoint: "https://api.example.com/users/12345"
```

**v2.0 方式（自动化全流程）：**
```yaml
# automated_test.yaml
global_setup:
  - name: "自动创建测试用户"
    type: http
    method: POST
    endpoint: "${base_url}/users"
    json:
      username: "auto_test_user"
      email: "auto@test.com"
    extract:
      user_id: "data.id"

- name: "完整流程测试"
  setup:
    - name: "准备用例特定数据"
      type: http
      method: POST
      endpoint: "${base_url}/posts"
      json:
        title: "测试文章"
        author_id: "${user_id}"  # 使用全局钩子提取的变量
      extract:
        post_id: "data.id"
  
  steps:
    - name: "获取刚创建的文章"
      method: GET
      endpoint: "${base_url}/posts/${post_id}"
      assertions:
        - type: status_code
          expected: 200
  
  teardown:
    - name: "自动清理文章"
      type: http
      method: DELETE
      endpoint: "${base_url}/posts/${post_id}"
      ignore_failure: true

global_teardown:
  - name: "全局清理：删除测试用户"
    type: http
    method: DELETE
    endpoint: "${base_url}/users/${user_id}"
    ignore_failure: true
```

```bash
# 一键运行，全自动生命周期管理
python api_test_agent.py run automated_test.yaml --env dev
```

---

## 常见问题 FAQ

### Q1: 升级到 v2.0 后，我现有的测试会坏掉吗？

**A: 完全不会。** v2.0 是 100% 向后兼容的。您可以：
- 继续使用所有 v1.0 的功能和语法
- 逐步选择性地采用新功能
- 混合使用新旧特性

### Q2: 我应该一次性迁移所有测试吗？

**A: 不建议。** 推荐的迁移策略：
1. **第 1 周**：只启用环境管理（`--env`），体验一键切换
2. **第 2 周**：为新编写的测试添加钩子
3. **第 3 周**：将重复性高的测试改为数据驱动
4. **第 4 周**：在大规模测试套件上启用并发

### Q3: 环境管理的 .env 文件安全吗？

**A: 安全，前提是正确使用。**
- ✅ `.env` 文件已在 `.gitignore` 中，不会提交到 Git
- ✅ 提供 `.env.example` 作为模板，不含真实值
- ✅ `--show-config` 自动脱敏敏感信息
- ⚠️ 请勿将真实的 `.env` 文件提交到版本控制系统

### Q4: 钩子系统会影响测试性能吗？

**A: 影响很小。**
- HTTP 钩子的开销等同于普通请求
- Command/Script 钩子取决于具体命令
- 建议将耗时操作放在 `global_setup`（只执行一次）
- 使用 `ignore_failure: true` 避免不必要的阻塞

### Q5: 并发执行会有什么风险？

**A: 主要注意以下几点：**
- **服务压力**：避免过多并发压垮被测 API
- **数据冲突**：确保用例间数据独立（或使用变量隔离）
- **资源竞争**：文件、数据库连接等共享资源需要处理好
- **建议**：从 `-w 2` 或 `-w 4` 开始，逐步增加

### Q6: 数据驱动的 CSV/JSON 文件应该放在哪里？

**A: 推荐放在项目根目录下的 `test_data/` 目录：**
```
project_root/
├── test_data/
│   ├── login_cases.csv
│   ├── register_cases.json
│   └── boundary_values.yml
├── examples/
│   └── v2_data_driven/
│       ├── csv_example.yaml
│       └── json_example.yaml
└── tests/
    └── ...
```
在 YAML 中使用相对路径引用：`file: test_data/login_cases.csv`

### Q7: 如何回退到 v1.0 行为？

**A: 很简单，只需：**
- 不使用 `--env` 参数
- 不添加 `global_setup/global_teardown/setup/teardown`
- 不使用 `data_source` 配置
- 不使用 `-w` 参数（或设为 1）

这样就会完全按照 v1.0 的方式运行！

---

## 下一步行动

### 🚀 立即开始

1. **阅读示例文件**：
   - [环境管理示例](examples/v2_environment/basic_usage.yaml)
   - [钩子机制示例](examples/v2_hooks/full_lifecycle.yaml)
   - [数据驱动示例](examples/v2_data_driven/csv_example.yaml)

2. **运行集成测试**：
   ```bash
   pytest tests/integration/ -v
   ```

3. **尝试新功能**：
   ```bash
   # 环境管理
   python api_test_agent.py env list
   
   # 数据驱动
   python api_test_agent.py run examples/v2_data_driven/csv_example.yaml --env dev
   
   # 并发
   python api_test_agent.py run examples/sample_tests.yaml -w 2
   ```

### 📚 深入学习

- [完整 README](README.md) - 项目概览和快速开始
- [CHANGELOG](CHANGELOG.md) - 详细的变更记录
- [使用教程](使用教程.md) - v1.0 完整教程（1.2 万字）
- [快速开始](快速开始.md) - 5 分钟入门指南

---

## 版本对照表

| 特性 | v1.0 | v2.0-alpha | 说明 |
|------|------|-----------|------|
| 基础测试执行 | ✅ | ✅ | 完全兼容 |
| 断言引擎 | 10 种 | 10 种 | 无变化 |
| 报告生成 | HTML/MD/JSON | HTML/MD/JSON | 无变化 |
| CLI 基础参数 | ✅ | ✅ | 完全兼容 |
| **环境管理** | ❌ | ✅ | **新增** |
| **钩子系统** | ❌ | ✅ | **新增** |
| **数据驱动** | ❌ | ✅ | **新增** |
| **并发执行** | ❌ | ✅ | **新增** |
| **配置校验** | ❌ | ✅ | **新增** |
| **敏感信息脱敏** | ❌ | ✅ | **新增** |

---

*最后更新：2026-05-01 | 版本：v2.0-alpha*
