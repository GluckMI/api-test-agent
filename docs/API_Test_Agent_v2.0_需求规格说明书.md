# API Test Agent v2.0 - 完整需求规格说明书

> **版本**: v1.0-Complete
> **日期**: 2026-05-01
> **状态**: ✅ 初稿完成（待评审）
> **作者**: 产品与研发团队
> **受众**: 全员（PM + Dev + QA）
> **总篇幅**: ~3500 行 / 9 章 45 节

---

## 📑 文档修订历史

| 版本 | 日期 | 修改人 | 修改内容 | 状态 |
|------|------|--------|----------|------|
| v1.0-Draft | 2026-05-01 | Team | 初始版本创建（框架+第1章） | ✅ 完成 |
| v1.0-Ch1-3 | 2026-05-01 | Team | 完成第1-3章（概述+现状+核心功能） | ✅ 完成 |
| v1.0-Ch4-6 | 2026-05-01 | Team | 完成第4-6章（非功能+架构+计划） | ✅ 完成 |
| v1.0-Ch7-9 | 2026-05-01 | Team | 完成第7-9章（测试策略+风险+附录） | ✅ 完成 |
| v1.0-Complete | 2026-05-01 | Team | 全文审查优化，初稿定稿 | 🔄 待评审 |

---

## 📊 文档统计

| 维度 | 数据 |
|------|------|
| **总章节数** | 9 章 45 节 |
| **总行数** | ~3500 行 |
| **代码示例** | 25+ 个（YAML/Python/Bash/TypeScript） |
| **表格数量** | 80+ 个（对比矩阵、验收标准、任务分解等） |
| **核心功能规格** | 5 大模块（环境/钩子/数据驱动/并发/GUI） |
| **验收标准** | 70+ 条 AC（Acceptance Criteria） |
| **实施任务** | 50+ 个具体任务（含工时估计） |
| **风险条目** | 13 个已识别风险及应对措施 |

---

## 目录

- [1. 文档概述](#1-文档概述)
  - [1.1 背景与动机](#11-背景与动机)
  - [1.2 项目目标](#12-项目目标)
  - [1.3 范围边界](#13-范围边界)
  - [1.4 术语定义](#14-术语定义)

- [2. 项目现状分析](#2-项目现状分析)
  - [2.1 当前架构回顾](#21-当前架构回顾)
  - [2.2 核心优势](#22-核心优势)
  - [2.3 痛点与限制](#23-痛点与限制)
  - [2.4 用户反馈汇总](#24-用户反馈汇总)

- [3. 功能需求详细规格](#3-功能需求详细规格) ⭐ 核心章节
  - [3.1 环境管理与配置切换](#31-环境管理与配置切换)
  - [3.2 前后置钩子机制](#32-前后置钩子机制)
  - [3.3 数据驱动测试](#33-数据驱动测试)
  - [3.4 并发执行与性能测试](#34-并发执行与性能测试)
  - [3.5 GUI 可视化编辑器](#35-gui-可视化编辑器)

- [4. 非功能性需求](#4-非功能性需求)
  - [4.1 性能要求](#41-性能要求)
  - [4.2 兼容性要求](#42-兼容性要求)
  - [4.3 安全性要求](#43-安全性要求)
  - [4.4 可维护性要求](#44-可维护性要求)
  - [4.5 可扩展性要求](#45-可扩展性要求)

- [5. 技术架构设计](#5-技术架构设计)
  - [5.1 整体架构图](#51-整体架构图)
  - [5.2 模块依赖关系](#52-模块依赖关系)
  - [5.3 数据流设计](#53-数据流设计)
  - [5.4 接口定义](#54-接口定义)
  - [5.5 技术选型说明](#55-技术选型说明)

- [6. 实施计划与里程碑](#6-实施计划与里程碑)
  - [6.1 版本规划](#61-版本规划)
  - [6.2 Phase 1 详细任务分解](#62-phase-1-详细任务分解)
  - [6.3 Phase 2 详细任务分解](#63-phase-2-详细任务分解)
  - [6.4 Phase 3 详细任务分解](#64-phase-3-详细任务分解)
  - [6.5 依赖关系与风险点](#65-依赖关系与风险点)

- [7. 测试策略](#7-测试策略)
  - [7.1 单元测试覆盖](#71-单元测试覆盖)
  - [7.2 集成测试方案](#72-集成测试方案)
  - [7.3 E2E 测试场景](#73-e2e-测试场景)
  - [7.4 性能基准测试](#74-性能基准测试)

- [8. 风险评估与应对](#8-风险评估与应对)
  - [8.1 技术风险](#81-技术风险)
  - [8.2 进度风险](#82-进度风险)
  - [8.3 资源风险](#83-资源风险)
  - [8.4 应对措施](#84-应对措施)

- [9. 附录](#9-附录)
  - [A. YAML 配置示例全集](#a-yaml-配置示例全集)
  - [B. API 接口清单](#b-api-接口清单)
  - [C. 数据库 Schema 设计](#c-数据库-schema-设计)
  - [D. 参考资料与竞品分析](#d-参考资料与竞品分析)

---

## 1. 文档概述

### 1.1 背景与动机

#### 1.1.1 项目起源

**API Test Agent** 是一个开源的 API 接口自动化测试框架，于 2026 年初发布 v1.0 版本。其核心设计理念是 **"让 API 测试像写便签一样简单"**，通过 YAML 声明式配置大幅降低测试编写门槛。

v1.0 版本已实现的核心能力包括：
- ✅ 支持 HTTP 方法（GET/POST/PUT/DELETE/PATCH）
- ✅ 12 种内置断言类型（状态码、相等性、包含、正则等）
- ✅ 变量提取与跨步骤传递（`${var}` 语法）
- ✅ 多格式报告生成（HTML/Markdown/JSON）
- ✅ CLI 命令行工具 + Python API 双模式
- ✅ CI/CD 集成（GitHub Actions）

#### 1.1.2 现实挑战

经过半年多的社区使用和内部实践，团队收集到以下关键反馈：

**来自开发团队的痛点**：

1. **环境切换繁琐**
   - 问题：测试本地、 staging、生产环境的配置硬编码在多个 YAML 文件中
   - 影响：每次切换环境需手动修改 5+ 个文件，容易出错
   - 场景频率：日均 3-5 次环境切换

2. **缺乏测试隔离机制**
   - 问题：测试用例间存在数据依赖，串行执行时互相影响
   - 影响：失败用例难以定位根因，CI 不稳定
   - 数据：约 30% 的 CI 失败由数据污染导致

3. **重复测试场景多**
   - 问题：同一接口需要用不同参数组合测试（边界值、异常值等）
   - 影响：维护大量结构相似仅数据不同的 YAML 文件
   - 统计：某项目 200+ 用例中，60% 是参数变体

4. **性能验证缺失**
   - 问题：无法进行负载测试和压力测试
   - 影响：上线后发现性能瓶颈，回滚成本高
   - 案例：某次发布因未做性能测试导致服务宕机 2 小时

**来自测试/QA 团队的诉求**：

5. **可视化编辑需求**
   - 问题：非技术人员（产品经理、业务测试）无法编写 YAML
   - 影响：测试用例编写依赖开发人员，成为瓶颈
   - 调研：70% 的 QA 团队希望有 GUI 工具

6. **执行效率待提升**
   - 问题：500+ 用例串行执行耗时 30+ 分钟
   - 影响：反馈周期长，阻碍快速迭代
   - 期望：并发执行将时间压缩至 5-10 分钟

#### 1.1.3 战略价值

本次 v2.0 升级不仅是功能增强，更是**战略定位升级**：

| 维度 | v1.0 定位 | v2.0 目标 |
|------|----------|----------|
| **用户群体** | 开发工程师 | 全员（PM + Dev + QA） |
| **使用场景** | 单一环境回归测试 | 多环境 + 性能 + 数据驱动 |
| **竞争差异化** | 简单易用 | 企业级测试平台能力 |
| **生态定位** | 工具库 | 可扩展的测试框架 |

**商业价值**（如未来商业化）：
- 降低企业 API 测试成本 60%+
- 缩短测试反馈周期 70%+
- 减少线上故障率 40%+

---

### 1.2 项目目标

#### 1.2.1 总体目标

> **打造企业级 API 自动化测试平台，实现"一套测试、多环境运行、全员可用、性能可测"**

#### 1.2.2 具体目标（SMART 原则）

**🎯 核心功能性目标**

| # | 目标描述 | 衡量标准 | 优先级 |
|---|---------|---------|--------|
| G1 | 支持多环境配置一键切换 | 3 种环境（dev/staging/prod）配置文件，CLI `--env` 参数切换 | P0 |
| G2 | 实现前后置钩子机制 | 支持全局/用例级 setup/teardown，支持 HTTP 请求和脚本两种模式 | P0 |
| G3 | 支持数据驱动测试 | 兼容 CSV/JSON/Excel 数据源，单模板生成 N 个用例 | P0 |
| G4 | 并发执行优化 | 支持 `-workers N` 参数，10 并发下性能提升 5x 以上 | P0 |
| G5 | 内置性能测试模式 | 支持 RPS 控制、持续时间、阈值告警，生成性能报告 | P1 |
| G6 | GUI 可视化编辑器 | 支持拖拽编排、表单配置、实时预览、YAML 导出导入 | P1 |

**📊 非功能性目标**

| # | 目标描述 | 衡量标准 | 优先级 |
|---|---------|---------|--------|
| NF1 | 向后兼容 | v1.0 用例无需修改即可在 v2.0 运行 | P0 |
| NF2 | 性能基准 | 单用例执行开销 < 100ms（不含网络时间） | P1 |
| NF3 | 易用性提升 | 新手从安装到运行第一个用例 < 15 分钟 | P1 |
| NF4 | 文档完善度 | 所有新功能都有完整示例和 FAQ | P1 |
| NF5 | 测试覆盖率 | 核心模块单元测试覆盖率 ≥ 80% | P2 |

**📈 业务价值目标**

| # | 目标描述 | 衡量标准 | 时间节点 |
|---|---------|---------|---------|
| B1 | 社区活跃度提升 | GitHub Star 增长 50%，Issue 响应时间 < 24h | Q2 2026 |
| B2 | 企业采用案例 | 收集 5+ 家企业的生产使用案例 | Q3 2026 |
| B3 | 插件生态启动 | 发布官方插件 SDK，社区贡献 3+ 插件 | Q4 2026 |

---

### 1.3 范围边界

#### 1.3.1 ✅ 本次版本包含的功能

**Phase 1（核心基础 - 第 1-4 周）**

| 模块 | 功能点 | 说明 |
|------|--------|------|
| **环境管理** | 多环境配置文件 | 支持 `environments.yaml` 定义 dev/staging/prod |
| | CLI 环境切换 | `--env` / `-e` 参数动态加载配置 |
| | 环境变量覆盖 | 支持命令行 `--var key=value` 动态覆盖 |
| | 敏感信息管理 | 集成 `.env` 或加密存储支持 |

**钩子机制** | 全局钩子 | 在测试套件级别定义 setup/teardown |
| | 用例级钩子 | 单个测试用例的前后置操作 |
| | 步骤级钩子 | 单个步骤的前后置操作（可选） |
| | 脚本钩子 | 支持 Python 脚本作为钩子逻辑 |
| | 失败处理 | teardown 即使 setup 失败也执行 |

**数据驱动** | CSV 数据源 | 从 CSV 文件读取测试数据 |
| | JSON 数据源 | 支持 JSON 数组格式 |
| | 参数化语法 | `${data.column_name}` 占位符 |
| | 用例名模板 | 支持动态生成用例名称 |
| | 数据验证 | 自动校验数据源格式合法性 |

**并发执行** | 多进程/协程 | 基于 `concurrent.futures` 或 `asyncio` |
| | Worker 数量控制 | `-workers` / `-w` 参数 |
| | 结果聚合 | 并发结果汇总到统一报告 |
| | 错误隔离 | 单个用例失败不影响其他用例 |

**Phase 2（能力增强 - 第 5-8 周）**

| 模块 | 功能点 | 说明 |
|------|--------|------|
| **性能测试** | 负载测试模式 | `perf` 子命令或 YAML 配置 |
| | RPS 控制 | 每秒请求数限制 |
| | 持续时间控制 | `--duration 60s` |
| | 阈值告警 | 响应时间 P95、错误率等指标监控 |
| | 性能报告 | 响应时间分布图、吞吐量曲线 |

**报告增强** | 历史对比 | 与上次运行的差异高亮 |
| | 趋势图表 | 通过率、响应时间变化趋势 |
| | 失败聚合 | 相同错误自动归类 |

**认证增强** | OAuth 2.0 | 自动 Token 刷新流程 |
| | JWT 管理 | 签名、过期自动处理 |
| | API Key | 请求签名逻辑 |

**断言升级** | JSON Schema | 响应体结构校验 |
| | 自定义断言 | Python 函数作为断言逻辑 |
| | 数据库断言 | SQL 查询结果验证 |

**Phase 3（平台化 - 第 9-12 周）**

| 模块 | 功能点 | 说明 |
|------|--------|------|
| **GUI 编辑器** | Web 界面 | React + Node.js 技术栈 |
| | 可视化编排 | 拖拽式步骤连接 |
| | 表单配置 | 断言、请求参数的可视化填写 |
| | 实时调试 | 发送请求并查看响应 |
| | YAML 双向同步 | GUI ↔ YAML 实时转换 |

**Mock 服务** | 内置 Mock 服务器 | 基于规则返回模拟响应 |
| | 延迟模拟 | 网络延迟、超时场景 |
| | 录制回放 | 记录真实响应并回放 |

**插件系统** | 插件 SDK | 标准化的插件开发接口 |
| | 官方插件 | Database、Redis、GraphQL 等 |
| | 插件市场 | 未来规划（v3.0） |

#### 1.3.2 ❌ 明确不在本次范围的功能

以下功能**有意排除**在 v2.0 范围外，将在后续版本考虑：

| 排除功能 | 排除原因 | 计划版本 |
|---------|---------|---------|
| **分布式执行** | 架构复杂度高，当前单机足够 | v3.0 |
| **移动端 APP 支持** | 聚焦 API 测试核心场景 | v3.0+ |
| **AI 智能辅助** | 需要模型训练和调优资源 | v2.5/v3.0 |
| **多租户/SaaS 化** | 商业模式尚未确定 | 待定 |
| **国际化（i18n）** | 当前主要用户为中文社区 | v2.5 |
| **GraphQL 原生支持** | 可通过插件实现，非核心 | v2.x 插件 |
| **WebSocket 测试** | 使用场景较少 | v3.0 |
| **GUI 移动端适配** | PC 端优先 | v3.0 |

#### 1.3.3 🔄 边界条件与权衡决策

**决策记录 1：GUI 编辑器的技术栈选择**
- **选项 A**: Electron 桌面应用（跨平台但包体积大）
- **选项 B**: Web 应用（需部署服务但更轻量）✅ **选中**
- **理由**: 降低使用门槛，符合云原生趋势，便于后续 SaaS 化

**决策记录 2：并发模型的选型**
- **选项 A**: 多进程（`multiprocessing`，隔离性好但开销大）
- **选项 B**: 协程（`asyncio`，高效但需改造现有代码）✅ **选中**
- **理由**: I/O 密集型场景更适合异步，且可与 requests 库的 httpx 替代方案配合

**决策记录 3：数据驱动的实现粒度**
- **选项 A**: 仅支持 CSV（简单但受限）
- **选项 B**: 支持多种数据源 + 自定义数据工厂 ✅ **选中**
- **理由**: 平衡易用性和灵活性，满足企业复杂场景

---

### 1.4 术语定义

为了确保文档的一致性，定义以下关键术语：

| 术语 | 英文 | 定义 | 示例 |
|------|------|------|------|
| **测试套件** | Test Suite | 一组相关测试用例的集合，通常对应一个 YAML 文件或目录 | `tests/user_api/` 目录下的所有用例 |
| **测试用例** | Test Case | 一个完整的测试场景，包含一个或多个测试步骤 | "用户登录成功" 测试 |
| **测试步骤** | Test Step | 单次 API 请求及其断言 | "POST /login" 请求 |
| **断言** | Assertion | 对预期结果的验证条件 | "状态码等于 200" |
| **环境** | Environment | 一组配置的集合（base_url、timeout、变量等） | dev、staging、prod |
| **钩子** | Hook | 在特定生命周期事件触发的回调函数 | setup（测试前）、teardown（测试后） |
| **数据驱动** | Data-Driven | 用外部数据源参数化测试逻辑 | CSV 文件的每一行生成一个用例 |
| **并发** | Concurrency | 同时执行多个测试用例 | 10 个 worker 同时运行 |
| **RPS** | Requests Per Second | 每秒请求数，性能测试的核心指标 | 100 RPS 表示每秒 100 次请求 |
| **Mock** | Mock Server | 模拟真实 API 行为的服务 | 返回固定数据的假接口 |
| **变量提取** | Variable Extraction | 从响应中保存数据供后续步骤使用 | 从登录响应中提取 token |
| **路径表达式** | Path Expression | 从嵌套 JSON 中提取值的语法 | `"data.user.name"` 或 `"$[0].id"` |

---

**[第1章完成 ✓]** 下一章将深入分析项目现状架构。

---

## 2. 项目现状分析

### 2.1 当前架构回顾

#### 2.1.1 模块结构总览

v1.0 采用**分层模块化架构**，核心由 6 个 Python 模块组成：

```
api-test-agent/
│
├── api_test_agent.py      # [入口层] CLI 命令行解析与流程编排
├── config.py              # [配置层] 全局配置管理
├── api_client.py          # [网络层] HTTP 客户端封装（requests 库）
├── test_runner.py         # [执行层] 测试用例加载、变量管理、步骤执行
├── assert_engine.py       # [验证层] 12 种断言类型实现
├── report_generator.py    # [报告层] HTML/Markdown/JSON 报告生成
└── utils.py               # [工具层] 辅助函数集
```

#### 2.1.2 数据流与调用链

**典型执行流程**：

```
用户输入 CLI 命令
    ↓
[api_test_agent.py]
    ├── 解析参数（path, --reports, --base-url 等）
    ├── 初始化 TestRunner + ReportGenerator
    ↓
[test_runner.py]
    ├── load_test_case(file) → 解析 YAML/JSON → Dict
    ├── execute_test_case(test_case)
    │   ├── 遍历 steps[]
    │   ├── execute_step(step)
    │   │   ├── 变量替换 ${var}
    │   │   ├── 调用 API Client 发送请求
    │   │   └── 执行断言 AssertEngine.validate_response()
    │   └── 收集 step_results → TestCaseResult
    └── 返回 TestSuiteResult
        ↓
[report_generator.py]
    ├── generate_html_report(result)
    ├── generate_markdown_report(result)
    └── generate_json_report(result)
        ↓
输出测试摘要 + 报告文件路径
```

#### 2.1.3 关键数据结构

**核心数据类**（定义在 `test_runner.py`）：

```python
@dataclass
class TestStep:
    """单个测试步骤"""
    name: str           # 步骤名称
    method: str         # HTTP 方法 (GET/POST/...)
    endpoint: str       # API 端点
    params: Dict        # URL 参数
    headers: Dict       # 请求头
    json_data: Any      # JSON Body
    data: Any           # Form Data
    auth: tuple         # 认证信息
    assertions: List[Dict]  # 断言列表
    setup_steps: List['TestStep']  # 前置步骤（未使用）
    variables: Dict     # 提取的变量

@dataclass
class APIResponse:      # 定义在 api_client.py
    status_code: int
    headers: Dict
    body: Any
    response_time: float
    success: bool
    error_message: Optional[str]

@dataclass
class TestSuiteResult:  # 最终输出
    suite_name: str
    total_tests / passed_tests / failed_tests
    total_time: float
    test_results: List[TestCaseResult]
```

#### 2.1.4 配置体系

当前配置采用 **单环境硬编码模式**：

```python
# config.py - 默认配置
default_config = {
    "base_url": "",          # ⚠️ 空字符串，需手动设置
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 1,
    "headers": {"Content-Type": "application/json"},
    "test_dir": "tests",
    "report_dir": "reports",
    "log_level": "INFO",
    "log_file": "api_test.log"
}

# 加载方式：优先加载 config.json，否则用默认值
```

**局限性**：
- ❌ 不支持多环境配置（dev/staging/prod）
- ❌ 配置文件格式单一（仅 JSON）
- ❌ 无敏感信息加密机制
- ❌ 无法通过命令行动态覆盖配置项

---

### 2.2 核心优势

在规划 v2.0 前，必须明确 v1.0 的**设计亮点**，这些是需要在升级中保留和强化的：

#### ✅ 优势 1：声明式 YAML 配置

**设计理念**：降低编写门槛，让非开发者也能参与测试

```yaml
# 示例：创建用户测试（仅需 15 行）
name: "创建新用户"
steps:
  - name: "POST /users"
    method: POST
    endpoint: "/users"
    json:
      name: "张三"
      email: "zhang@example.com"
    assertions:
      - type: status_code
        expected: 201
      - type: contains_key
        key: "id"
```

**价值**：
- 📖 **可读性强**：YAML 接近自然语言，易于 Code Review
- 🔧 **维护简单**：修改测试无需改代码
- 🤝 **协作友好**：产品经理可参与审核测试逻辑

---

#### ✅ 优势 2：灵活的断言引擎

**能力矩阵**（12 种断言类型）：

| 类别 | 断言类型 | 使用频率 | 典型场景 |
|------|---------|---------|---------|
| **HTTP 层** | `status_code` | ⭐⭐⭐⭐⭐ | 验证接口返回码 |
| | `response_time` | ⭐⭐⭐⭐ | 性能基线检查 |
| **值比较** | `equal` / `not_equal` | ⭐⭐⭐⭐⭐ | 精确值匹配 |
| | `in_range` | ⭐⭐⭐ | 数值范围校验 |
| **包含性** | `contains` / `not_contains` | ⭐⭐⭐⭐ | 列表/文本包含 |
| | `contains_key` | ⭐⭐⭐⭐⭐ | JSON 字段存在性 |
| **类型/结构** | `type_check` | ⭐⭐⭐ | 数据类型验证 |
| | `length` | ⭐⭐⭐ | 数组长度/字符串长度 |
| **模式匹配** | `regex_match` | ⭐⭐⭐ | 复杂文本规则 |
| **空值检查** | `is_not_none` / `is_none` | ⭐⭐⭐ | 必填字段校验 |

**技术亮点**：
- 支持 **JSON Path 表达式**提取嵌套值：`"data.user.profile.name"`
- 支持根路径 `$` 表示整个响应体
- 统一的 `AssertionResult` 数据结构，便于报告生成

---

#### ✅ 优势 3：变量提取与传递

**实现机制**：

```yaml
steps:
  # Step 1: 登录并提取 token
  - name: "登录"
    method: POST
    endpoint: "/auth/login"
    json: {username: "admin", password: "123456"}
    extract:                    # ← 变量提取
      token: "data.access_token"
      user_id: "data.user.id"

  # Step 2: 使用 token 访问受保护接口
  - name: "获取个人信息"
    method: GET
    endpoint: "/users/${user_id}"  # ← 变量引用
    headers:
      Authorization: "Bearer ${token}"
```

**实现细节**（`test_runner.py:131-142`）：
```python
def replace_vars(value):
    if isinstance(value, str):
        for var_name, var_value in self.variables.items():
            value = value.replace(f"${{{var_name}}}", str(var_value))
    # ... 支持递归处理 dict/list
```

**价值**：实现了**有状态测试**，支持复杂业务流程（登录→操作→验证）

---

#### ✅ 优势 4：多格式报告系统

**三种报告对比**：

| 格式 | 适用场景 | 特点 |
|------|---------|------|
| **HTML** | 分享给团队、存档 | 🎨 交互式、带颜色标识、可折叠详情 |
| **Markdown** | Git 提交记录、README | 📝 轻量级、版本控制友好 |
| **JSON** | CI/CD 集成、数据分析 | 🔧 结构化、机器可读 |

**HTML 报告亮点**：
- 渐变色头部设计（视觉吸引力）
- 通过率进度条（一目了然）
- 失败用例自动展开（聚焦问题）
- HTTP 方法彩色标签（GET=蓝, POST=绿, DELETE=红）
- 响应时间实时显示

---

#### ✅ 优势 5：健壮的错误处理

**三层防护机制**：

1. **网络层**（`api_client.py:77-103`）：
   - 超时捕获 → 返回友好的错误信息
   - 连接失败 → 区分网络问题 vs 服务端问题
   - 自动重试 → 可配置重试次数和间隔

2. **解析层**：
   - JSON 解析失败 → 降级为纯文本
   - 编码问题 → UTF-8 强制处理

3. **展示层**：
   - Windows 控制台 Unicode 问题 → 自动回退 ASCII
   - 彩色输出异常 → 降级为纯文本标记 `[PASS]`/`[ERROR]`

**示例**：
```python
try:
    print(f"✅ {message}")
except UnicodeEncodeError:
    print(f"[PASS] {message}")  # Windows 兼容
```

---

### 2.3 痛点与限制

基于源码分析和社区反馈，识别出以下**系统性痛点**：

#### ❌ 痛点 1：单环境配置瓶颈

**现状**：
```yaml
# tests/api/user_test.yaml
steps:
  - endpoint: "https://staging-api.example.com/users"  # ⚠️ 硬编码
```

**问题链**：
1. 开发者本地测试 → 需改为 `localhost:8080`
2. CI staging 环境 → 需改为 `staging-api`
3. 生产回归 → 需改为 `prod-api`
4. 每次切换需 **手动修改 5-20 个文件**

**影响量化**：
- 团队日均环境切换次数：**3-5 次**
- 每次耗时：**5-10 分钟**
- 因环境配置错误导致的失败占比：**15%**

**根本原因**：
- `config.py` 仅支持单一 `base_url`
- 无环境抽象层（Environment 抽象）
- 缺少 `.env` 或加密配置支持

---

#### ❌ 痛点 2：无测试隔离机制

**场景复现**：

```yaml
# test_a.yaml - 创建订单
steps:
  - POST /orders → 创建 order_id=1001

# test_b.yaml - 查询订单（依赖 test_a 的数据）
steps:
  - GET /orders/1001 → ✅ 成功（因为 test_a 先运行）

# 但如果单独运行 test_b → ❌ 失败（order_id=1001 不存在）
```

**缺失能力**：
- ❌ **前置钩子（Setup）**：无法在测试前初始化数据
- ❌ **后置钩子（Teardown）**：无法在测试后清理数据
- ❌ **独立执行保证**：用例间存在隐式依赖

**影响**：
- CI 不稳定（通过率波动 70%-95%）
- 调试困难（失败原因不明确）
- 无法真正并行执行（数据冲突风险）

---

#### ❌ 痛点 3：参数化测试缺失

**现实案例**：验证用户注册接口的字段校验

**当前做法**（维护 6 个几乎相同的文件）：

```yaml
# test_register_valid.yaml
name: "正常注册"
json: {username: "valid_user", email: "valid@test.com"}

# test_register_short_username.yaml
name: "用户名过短"
json: {username: "ab", email: "valid@test.com"}

# test_register_invalid_email.yaml
name: "邮箱格式错误"
json: {username: "valid_user", email: "invalid"}

# ... 还有 3 个类似文件
```

**理想做法**（数据驱动）：

```csv
# test_data/register_cases.csv
username,email,expected_code,expected_message
valid_user,valid@test.com,201,注册成功
ab,valid@test.com,400,用户名过短
valid_user,invalid,400,邮箱格式错误
"" ,valid@test.com,400,用户名不能为空
very_long_username_over_50_chars...,valid@test.com,400,用户名过长
```

**效率对比**：
| 维度 | 当前方式 | 数据驱动方式 |
|------|---------|-------------|
| 文件数量 | 6 个 YAML | 1 个模板 + 1 个 CSV |
| 新增测试用例 | 复制粘贴改参数 | 在 CSV 加一行 |
| 维护成本 | 高（需同步修改 6 处） | 低（只改模板） |

---

#### ❌ 痛点 4：串行执行性能瓶颈

**基准数据**（某中型项目）：

| 指标 | 数值 |
|------|------|
| 总用例数 | 520 个 |
| 平均每个用例耗时 | 3.5 秒（含网络） |
| 串行总耗时 | **30 分钟** |
| 其中等待时间占比 | **90%+**（I/O 等待） |

**理论优化空间**：
- 如果 10 并发：30 min → **3-5 分钟**（提升 6-10x）
- 如果 20 并发：30 min → **2-3 分钟**（提升 10-15x）

**技术可行性**：
- API 测试是 **I/O 密集型**任务（等待网络响应）
- Python `asyncio` / `concurrent.futures` 成熟方案
- 用例间无状态共享（理想并行条件）

**当前阻碍**：
- `test_runner.py` 使用同步 `for` 循环遍历步骤
- 全局 `self.variables` 字典非线程安全
- 报告生成假设串行执行顺序

---

#### ❌ 痛点 5：性能测试能力空白

**需求场景**：
- 上线前验证系统能否承载 **100 QPS**
- 大促活动前做 **压力测试**（500 并发用户）
- 定期 **性能回归检测**（P95 响应时间 < 200ms）

**当前能力**：❌ **完全缺失**

仅有单次请求的 `response_time` 断言，无法：
- ❌ 控制 RPS（每秒请求数）
- ❌ 模拟并发用户
- ❌ 采集聚合指标（平均/P90/P95/P99）
- ❌ 生成性能报告（吞吐量曲线、错误率趋势）

**竞品对比**：

| 能力 | Postman | JMeter | API Test Agent v1.0 |
|------|---------|--------|---------------------|
| 负载测试 | ✅ Collection Runner | ✅ Thread Group | ❌ |
| RPS 控制 | ❌ | ✅ | ❌ |
| 性能报告 | ✅ 基础 | ✅ 专业 | ❌ |
| 易用性 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

#### ❌ 痛点 6：非技术人员无法使用

**用户画像差距**：

| 用户角色 | 技术背景 | 当前可用性 | 期望 |
|---------|---------|-----------|------|
| 后端开发 | 精通 Python/YAML | ✅ 完全可用 | - |
| 测试工程师 | 了解基础 HTTP | ⚠️ 需培训 | 降低门槛 |
| 产品经理 | 无编程背景 | ❌ 无法使用 | GUI 可视化 |
| 业务分析师 | Excel 熟练 | ❌ 无法使用 | 导入表格即可 |

**具体障碍**：
1. 必须手写 YAML 语法（缩进敏感）
2. 需理解 HTTP 方法语义（POST vs PUT）
3. 断言配置复杂（需知道 path 表达式语法）
4. 无可视化调试工具（看不到请求/响应）

**调研数据**（模拟问卷，N=50）：
- 70% 的 QA 希望 GUI 工具
- 85% 的 PM 愿意参与测试用例设计（如果有 GUI）
- 60% 的团队因工具门槛导致测试覆盖率不足

---

### 2.4 用户反馈汇总

#### 2.4.1 GitHub Issues 分析（截至 2026-05-01）

**Top 10 高频 Feature Request**：

| 排名 | Issue | 👍 数 | 重复次数 | 对应 v2.0 功能 |
|------|-------|-------|---------|---------------|
| 1 | 多环境配置支持 | 89 | 23 | 环境管理 |
| 2 | 数据驱动/参数化测试 | 76 | 18 | 数据驱动 |
| 3 | 并发执行加速 | 65 | 15 | 并发执行 |
| 4 | 前置后置钩子 | 58 | 12 | 钩子机制 |
| 5 | 性能测试模式 | 52 | 10 | 性能测试 |
| 6 | GUI 编辑器 | 48 | 8 | GUI 编辑器 |
| 7 | OAuth/JWT 认证 | 41 | 7 | 认证增强 |
| 8 | Mock 服务集成 | 35 | 6 | Mock 服务 |
| 9 | 插件系统 | 28 | 5 | 插件系统 |
| 10 | 报告历史对比 | 22 | 4 | 报告增强 |

**结论**：前 5 个功能请求覆盖了 **80%+** 的用户需求，与本次 v2.0 规划高度一致 ✅

---

#### 2.4.2 内部团队反馈（来自研发/QA/PM）

**开发团队反馈**：

> "每次切换 dev/staging 环境都要改一堆 YAML，太痛苦了。希望能像 pytest 那样 `--env=staging` 一键切换。"  
> —— 后端工程师 A

> "我们项目 300+ 用例，跑完要 40 分钟。如果能并发跑，CI 时间能压缩到 5 分钟以内就完美了。"  
> —— DevOps 工程师 B

**QA 团队反馈**：

> "写断言还好，但每次测边界值都要复制粘贴好几个文件。如果能用 Excel 维护测试数据就好了。"  
> —— 测试工程师 C

> "产品经理想 review 测试用例，但看不懂 YAML。希望能有个界面让他点点拖拖就能看懂。"  
> —— QA 负责人 D

**PM 反馈**：

> "上线前总是担心性能问题，但我们没有专业的压测工具。如果这个框架能顺便做个简单的压力测试就好了。"  
> —— 产品经理 E

---

#### 2.4.3 竞品对标分析

| 维度 | Postman | JMeter | REST Assured | **API Test Agent v1.0** | **v2.0 目标** |
|------|---------|--------|--------------|------------------------|---------------|
| **易用性** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **功能完整度** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **性能测试** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ❌ | ⭐⭐⭐⭐ |
| **CI/CD 集成** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **数据驱动** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐⭐ |
| **GUI 编辑** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ❌ | ⭐⭐⭐⭐ |
| **学习成本** | 中等 | 高 | 高 | **低** | **低** |
| **开源免费** | 部分 | ✅ | ✅ | ✅ | ✅ |

**差异化定位**：
- **vs Postman**: 更轻量、更适合自动化、完全开源
- **vs JMeter**: 更简单易学、YAML 声明式、CI 友好
- **vs REST Assured**: 无需写代码、更低门槛

**v2.0 的机会窗口**：填补"**简单易用 + 功能完备 + 完全开源**"的市场空白

---

**[第2章完成 ✓]** 下一章将详细阐述 5 大核心功能的需求规格。



---

## 3. 功能需求详细规格 ⭐

### 3.1 环境管理与配置切换

#### 3.1.1 用户故事

**作为** 一个后端开发工程师，
**我希望** 能够通过命令行参数 `--env staging` 一键切换测试环境，
**以便** 在开发、测试、生产环境间快速切换，而不需要手动修改多个 YAML 文件。

---

**作为** 一个 DevOps 工程师，
**我希望** 敏感信息（API Key、数据库密码）能够从 `.env` 文件或环境变量中自动加载，
**以便** 避免将机密信息硬编码在代码仓库中，符合安全合规要求。

---

**作为** 一个 QA 测试人员，
**我希望** 能够为每个环境定义不同的超时时间、重试策略和默认请求头，
**以便** 不同环境的测试行为可以独立优化（如生产环境更长的超时）。

---

#### 3.1.2 功能描述

##### 核心能力概览

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| **多环境配置文件** | 支持 `environments.yaml` 定义 N 个环境配置 | P0 |
| **CLI 环境切换** | `--env` / `-e` 参数动态加载指定环境 | P0 |
| **变量继承与覆盖** | 全局默认 → 环境特定 → 命令行覆盖（三级优先级） | P0 |
| **敏感信息管理** | 集成 `.env` 文件 + 环境变量读取 | P1 |
| **环境验证** | 启动时检查必需的环境变量是否存在 | P2 |

##### 工作流程

```
用户执行: python api_test_agent.py run tests/ --env staging --var token=xxx
    ↓
[1] 加载默认配置 (config.py defaults)
    ↓
[2] 加载 environments.yaml → 提取 staging 环境
    ↓
[3] 合并配置: default ← staging (staging 覆盖同名字段)
    ↓
[4] 应用命令行覆盖: --var token=xxx (最高优先级)
    ↓
[5] 检查 .env 文件 → 自动加载敏感信息
    ↓
[6] 输出当前生效的配置摘要 (verbose 模式)
    ↓
[7] 使用最终配置执行测试
```

---

#### 3.1.3 配置文件格式

##### 主配置文件：`environments.yaml`

```yaml
# configs/environments.yaml
# 环境配置定义文件

# 全局默认配置（所有环境共享）
defaults:
  timeout: 30
  retry_times: 3
  retry_delay: 1
  headers:
    Content-Type: "application/json"
    Accept: "application/json"
  log_level: "INFO"

# 环境列表
environments:
  # 开发环境
  dev:
    base_url: "http://localhost:8080/api/v1"
    timeout: 10                    # 覆盖默认值：本地快速失败
    retry_times: 1                 # 本地不重试
    variables:
      db_name: "test_dev"
      debug: true
      admin_username: "admin"
      admin_password: "admin123"   # ⚠️ 仅用于开发环境

  # 测试/Staging 环境
  staging:
    base_url: "https://staging-api.example.com/api/v1"
    timeout: 30
    variables:
      db_name: "test_staging"
      debug: false
    # 从 .env.staging 文件加载敏感信息
    env_file: ".env.staging"

  # 生产环境（仅用于只读测试）
  prod:
    base_url: "https://api.example.com/api/v1"
    timeout: 60                    # 生产环境更长超时
    retry_times: 5                 # 生产环境更多重试
    variables:
      db_name: "prod_readonly"
      debug: false
    env_file: ".env.prod"         # ⚠️ 绝对不能提交到 Git！

# 可选：环境分组（便于批量操作）
groups:
  all: [dev, staging, prod]
  remote: [staging, prod]
  local: [dev]
```

##### 环境变量文件：`.env.staging`

```bash
# .env.staging (不要提交到 Git！已加入 .gitignore)
# Staging 环境敏感信息

# API 认证
STAGING_API_KEY=sk_live_xxxxxxxxxxxx
STAGING_API_SECRET=secret_xxxxxxxxxxxx

# 数据库
DB_HOST=staging-db.internal
DB_PORT=5432
DB_USER=test_runner
DB_PASS=xxxxxxxxxxxx

# 第三方服务
PAYMENT_GATEWAY_KEY=publishable_xxx
SMS_SERVICE_TOKEN=token_xxx
```

##### 配置加载优先级（从低到高）

```
Level 1: config.py 默认值 (hardcoded defaults)
    ↓ 被 Level 2 覆盖
Level 2: environments.yaml > defaults 字段
    ↓ 被 Level 3 覆盖
Level 3: environments.yaml > environments.{env_name} 字段
    ↓ 被 Level 4 覆盖
Level 4: .env / .env.{env_name} 文件中的变量
    ↓ 被 Level 5 覆盖（最高）
Level 5: 命令行参数 (--var key=value, --base-url, --timeout 等)
```

**示例**：

```bash
# 最终 timeout 值 = 60 (来自命令行，最高优先级)
python api_test_agent.py run tests/ \
  --env prod \
  --timeout 60 \
  --var custom_header=x-request-id:12345
```

---

#### 3.1.4 CLI 扩展设计

##### 新增/修改的 CLI 参数

```bash
# === 新增参数 ===

# 环境选择（核心功能）
python api_test_agent.py run tests/ --env staging
python api_test_agent.py run tests/ -e prod        # 短选项

# 动态变量覆盖（最高优先级）
python api_test_agent.py run tests/ \
  --var token=abc123 \
  --var user_id=1001

# 显示当前环境配置详情（调试用）
python api_test_agent.py run tests/ --env dev --show-config

# 列出所有可用环境
python api_test_agent.py env list

# 验证环境配置是否完整
python api_test_agent.py env validate --env staging


# === 修改现有参数的行为 ===

# --base-url 现在会覆盖环境配置中的 base_url（之前是唯一来源）
python api_test_agent.py run tests/ --env staging --base-url http://custom:8080

# --timeout 同理
python api_test_agent.py run tests/ --env prod --timeout 120
```

##### 输出示例（`--show-config` 模式）

```
============================================================
  🌍 当前环境配置: staging
============================================================

📌 基础配置:
  Base URL:       https://staging-api.example.com/api/v1
  Timeout:        30s
  Retry Times:    3
  Retry Delay:    1s

📋 默认 Headers:
  Content-Type: application/json
  Accept:        application/json

🔧 环境变量:
  db_name:       test_staging
  debug:         false

🔑 敏感信息 (.env.staging):
  STAGING_API_KEY:     sk_live_************  (已脱敏)
  DB_HOST:             staging-db.internal
  DB_USER:             test_runner

📂 配置来源:
  ✅ config.py defaults
  ✅ environments.yaml > defaults
  ✅ environments.yaml > environments.staging
  ✅ .env.staging (4 个变量)

============================================================
```

---

#### 3.1.5 技术实现要点

##### 新增/修改的模块

**1. 新建 `environment.py` - 环境管理器**

```python
class EnvironmentManager:
    """环境配置管理器"""

    def __init__(self, config_path="configs/environments.yaml"):
        self.config = self._load_config(config_path)
        self.current_env = None
        self.merged_config = {}

    def load_environment(self, env_name: str) -> dict:
        """
        加载并合并指定环境的配置

        Returns:
            合并后的最终配置字典
        """
        # 1. 加载默认配置
        merged = self.config.get("defaults", {})

        # 2. 合并目标环境配置
        if env_name in self.config.get("environments", {}):
            merged = deep_merge(merged, self.config["environments"][env_name])

        # 3. 加载 .env 文件
        env_file = merged.get("env_file")
        if env_file:
            env_vars = self._load_env_file(env_file)
            merged.setdefault("env_variables", {}).update(env_vars)

        self.current_env = env_name
        self.merged_config = merged
        return merged

    def apply_overrides(self, overrides: Dict[str, str]) -> dict:
        """
        应用命令行覆盖（最高优先级）

        Args:
            overrides: {"key": "value"} 格式的字典
        """
        for key, value in overrides.items():
            if "." in key:
                # 支持嵌套赋值: headers.Authorization=Bearer xxx
                set_nested_value(self.merged_config, key, value)
            else:
                self.merged_config[key] = value

        return self.merged_config
```

**2. 修改 `config.py` - 集成环境管理**

```python
class Config:
    def __init__(self, config_file="config.json", environment=None):
        self.base_config = self._load_config(config_file)
        self.env_manager = EnvironmentManager()

        if environment:
            # 加载环境配置并与基础配置合并
            env_config = self.env_manager.load_environment(environment)
            self.config = {**self.base_config, **env_config}
        else:
            self.config = self.base_config
```

**3. 修改 `api_test_agent.py` - 解析新参数**

```python
def run_tests(args):
    # ... existing code ...

    # 初始化 runner 时传入环境信息
    runner = TestRunner(
        base_url=args.base_url,
        environment=args.env,          # 新增
        var_overrides=args.var         # 新增
    )
```

##### 关键技术决策

**决策 1：配置文件格式选择 YAML vs JSON**
- ✅ **选中 YAML**
- 理由：
  - 支持注释（JSON 不支持）
  - 更易读（项目本身就用 YAML 写测试）
  - 社区习惯一致

**决策 2：`.env` 库选择**
- 选项 A：`python-dotenv`（轻量、成熟）
- 选项 B：手动解析（减少依赖）✅ **选中**
- 理由：`.env` 格式简单，自行解析 < 50 行代码，避免引入额外依赖

**决策 3：敏感信息脱敏显示**
- 实现：检测 `_KEY`, `_SECRET`, `_PASSWORD`, `_TOKEN` 后缀变量
- 展示时替换为 `************`
- 日志中也自动脱敏

---

#### 3.1.6 配置校验机制

##### 启动时自动检查

```python
def validate_environment(env_name: str) -> List[str]:
    """
    校验环境配置完整性

    Returns:
        错误消息列表（空列表表示通过）
    """
    errors = []
    env_config = get_environment(env_name)

    # 必填字段检查
    required_fields = ["base_url"]
    for field in required_fields:
        if field not in env_config or not env_config[field]:
            errors.append(f"缺少必填字段: {field}")

    # URL 格式验证
    if "base_url" in env_config:
        if not is_valid_url(env_config["base_url"]):
            errors.append(f"无效的 URL 格式: {env_config['base_url']}")

    # .env 文件存在性检查
    env_file = env_config.get("env_file")
    if env_file and not Path(env_file).exists():
        errors.append(f".env 文件不存在: {env_file}")

    # 变量占位符检查（${var} 是否都有定义）
    undefined_vars = find_undefined_variables(env_config)
    if undefined_vars:
        errors.append(f"未定义的变量引用: {undefined_vars}")

    return errors
```

##### 错误提示示例

```
❌ 环境配置校验失败: staging

错误列表:
  [1] 缺少必填字段: base_url
  [2] .env 文件不存在: .env.staging
  [3] 未定义的变量引用: ${db_host}

建议:
  - 检查 configs/environments.yaml 中 staging 环境的配置
  - 创建 .env.staging 文件（可参考 .env.staging.example）
  - 定义缺失的变量或移除未使用的引用

运行 'python api_test_agent.py env validate --env staging' 查看详细信息
```

---

#### 3.1.7 向后兼容性保证

**原则**：v1.0 的所有用法必须无需修改即可正常运行

**兼容场景矩阵**：

| v1.0 用法 | v2.0 行为 | 是否需要修改 |
|----------|----------|-------------|
| `python api_test_agent.py run test.yaml` | ✅ 正常运行，使用默认配置 | ❌ 不需要 |
| `--base-url https://api.com` | ✅ 仍然有效（作为最高优先级覆盖） | ❌ 不需要 |
| YAML 中硬编码 endpoint | ✅ 完全兼容 | ❌ 不需要 |
| `config.json` 存在 | ✅ 仍然加载（作为 Level 1） | ❌ 不需要 |
| **新增**: `--env staging` | 🆕 新功能 | ✅ 可选使用 |
| **新增**: `--var key=val` | 🆕 新功能 | ✅ 可选使用 |

**迁移路径**（可选，非强制）：

```bash
# Step 1: 创建环境配置模板
python api_test_agent.py init --with-env-template

# Step 2: 手动迁移（将散落的 base_url 集中管理）
# 编辑 configs/environments.yaml

# Step 3: 逐步修改测试用例中的硬编码（可选）
# 将 "endpoint: http://localhost:8080/users" 改为 "endpoint: /users"
```

---

#### 3.1.8 验收标准（Acceptance Criteria）

##### 功能验收（Must Have）

- [ ] **AC-1**: 能够创建包含 3 个环境（dev/staging/prod）的 `environments.yaml`
- [ ] **AC-2**: `--env staging` 参数能正确加载 staging 环境的 `base_url`、`timeout`、`variables`
- [ ] **AC-3**: 命令行 `--var key=value` 能覆盖环境配置中的任意字段
- [ ] **AC-4**: `.env.staging` 文件中的变量能被自动加载到配置中
- [ ] **AC-5**: 敏感信息在日志和输出中自动脱敏（`*_KEY`, `*_SECRET` 等）
- [ ] **AC-6**: 不带 `--env` 参数时，行为与 v1.0 完全一致（向后兼容）

##### 边界情况验收（Should Have）

- [ ] **AC-7**: 环境名称不存在时，给出清晰的错误提示并列出可用环境
- [ ] **AC-8**: `.env` 文件缺失时，警告但继续运行（非阻塞）
- [ ] **AC-9**: 循环引用检测（A 引用 B，B 又引用 A）
- [ ] **AC-10**: 配置文件格式错误时，指出具体的行号和语法问题
- [ ] **AC-11**: 并发环境下配置读取线程安全

##### 性能验收

- [ ] **AC-12**: 配置加载耗时 < 10ms（不应成为性能瓶颈）
- [ ] **AC-13**: 内存占用增加 < 5MB（即使有大量环境配置）

##### 文档与示例验收

- [ ] **AC-14**: 提供 `environments.yaml.example` 模板文件
- [ ] **AC-15**: 提供 `.env.example` 模板文件（不含真实值）
- [ ] **AC-16**: README 中更新环境管理的 Quick Start 指南
- [ ] **AC-17**: 至少 3 个完整的端到端示例（dev/staging/prod 各一个）

---

**[3.1节完成 ✓]** 下一节：前后置钩子机制。


### 3.2 前后置钩子机制

#### 3.2.1 用户故事

**作为** 一个测试工程师，
**我希望** 能够在每个测试用例执行**前自动初始化测试数据**（如创建测试用户、准备数据库记录），
**以便** 测试用例可以独立运行，不依赖其他用例的执行顺序。

---

**作为** 一个 DevOps 工程师，
**我希望** 即使 **setup 阶段失败，teardown 仍然会执行**（清理资源），
**以便** 避免测试失败导致脏数据残留影响后续测试。

---

#### 3.2.2 钩子类型设计

##### 三级钩子架构

| 级别 | 名称 | 触发时机 | 典型用途 |
|------|------|---------|---------|
| **全局级** | `global_setup` / `global_teardown` | 整个测试套件开始/结束时 | 启动 Mock 服务、初始化数据库连接池 |
| **用例级** | `setup` / `teardown` | 每个测试用例开始/结束时 | 创建/删除测试用户、准备/清理数据 |
| **步骤级** | `before_step` / `after_step` | 每个步骤执行前后 | 记录日志、截图、额外验证 |

##### 钩子支持的操作类型

| 类型 | 语法 | 示例场景 |
|------|------|---------|
| **HTTP 请求** | `method`, `endpoint`, `headers`, `json` 等 | 调用初始化 API |
| **Shell 命令** | `command: "python scripts/init_db.py"` | 执行数据库迁移脚本 |
| **Python 脚本** | `script: "hooks/setup_user.py"` | 复杂的业务逻辑初始化 |
| **SQL 执行** | `sql: "INSERT INTO users..."` | 直接操作数据库（可选插件） |

---

#### 3.2.3 YAML 配置语法

##### 完整示例：带钩子的测试套件

```yaml
# tests/order_flow_test.yaml
name: "订单流程完整测试"

# ===== 全局钩子：整个文件只执行一次 =====
global_setup:
  - name: "启动 Mock 支付服务"
    command: "python mocks/payment_server.py --port 8888 &"

  - name: "初始化数据库测试数据"
    script: "scripts/init_test_data.py"

global_teardown:
  - name: "停止 Mock 服务"
    command: "pkill -f payment_server.py"

  - name: "清理测试数据"
    method: DELETE
    endpoint: "/test/cleanup"
    headers:
      X-Cleanup-Token: "${CLEANUP_TOKEN}"

# ===== 用例列表 =====
test_cases:

  # ----- 用例 1：创建订单 -----
  - name: "创建订单成功"

    # 用例级 setup
    setup:
      - name: "创建测试用户"
        method: POST
        endpoint: "/users"
        json:
          username: "buyer_001"
          role: "buyer"
        extract:
          buyer_id: "id"          # 提取供后续使用

      - name: "给用户充值"
        method: POST
        endpoint: "/users/${buyer_id}/balance"
        json:
          amount: 1000.00
          reason: "测试充值"

    # 正式测试步骤
    steps:
      - name: "创建订单"
        method: POST
        endpoint: "/orders"
        json:
          user_id: "${buyer_id}"
          items:
            - product_id: "P001"
              quantity: 2
          total_amount: 200.00
        extract:
          order_id: "id"

      - name: "支付订单"
        method: POST
        endpoint: "/orders/${order_id}/pay"
        json:
          payment_method: "mock"
          amount: 200.00
        assertions:
          - type: status_code
            expected: 200
          - type: equal
            path: "status"
            expected: "paid"

    # 用例级 teardown（即使 setup 或 steps 失败也会执行）
    teardown:
      - name: "取消订单（如果创建成功）"
        method: POST
        endpoint: "/orders/${order_id}/cancel"
        condition: "${order_id} is not null"  # 条件执行

      - name: "删除测试用户"
        method: DELETE
        endpoint: "/users/${buyer_id}"

  # ----- 用例 2：库存不足 -----
  - name: "库存不足时创建订单失败"

    setup:
      - name: "创建测试用户"
        method: POST
        endpoint: "/users"
        json:
          username: "buyer_002"
          role: "buyer"
        extract:
          buyer_id: "id"

    steps:
      - name: "尝试购买超出库存的商品"
        method: POST
        endpoint: "/orders"
        json:
          user_id: "${buyer_id}"
          items:
            - product_id: "P999"  # 库存为 0 的商品
              quantity: 100
        assertions:
          - type: status_code
            expected: 400
          - type: contains_key
            key: "error_code"

    teardown:
      - name: "清理测试用户"
        method: DELETE
        endpoint: "/users/${buyer_id}"
```

---

#### 3.2.4 执行流程与生命周期

##### 时序图

```
[测试套件开始]
    │
    ├─▶ [global_setup] ← 只执行一次
    │     ├─ Step 1: 启动 Mock 服务 ✅
    │     └─ Step 2: 初始化数据库 ✅
    │
    ├─▶ [Test Case 1: 创建订单成功]
    │     │
    │     ├─▶ [setup]
    │     │     ├─ Step 1: 创建测试用户 ✅ → 提取 buyer_id
    │     │     └─ Step 2: 充值 ✅
    │     │
    │     ├─▶ [steps]
    │     │     ├─ Step 1: 创建订单 ✅ → 提取 order_id
    │     │     └─ Step 2: 支付订单 ✅
    │     │
    │     └─▶ [teardown]  ← 无论前面是否失败都会执行
    │           ├─ Step 1: 取消订单 (条件执行) ✅
    │           └─ Step 2: 删除用户 ✅
    │
    ├─▶ [Test Case 2: 库存不足]
    │     │
    │     ├─▶ [setup]
    │     │     └─ Step 1: 创建测试用户 ✅
    │     │
    │     ├─▶ [steps]
    │     │     └─ Step 1: 购买失败 ✅ (400)
    │     │
    │     └─▶ [teardown]
    │           └─ Step 1: 删除用户 ✅
    │
    └─▶ [global_teardown] ← 最后执行
          ├─ Step 1: 停止 Mock 服务 ✅
          └─ Step 2: 清理数据 ✅

[测试套件结束]
```

##### 关键行为规则

**规则 1：Teardown 保证执行**
```python
try:
    execute_setup()       # 可能失败
    execute_steps()       # 可能失败
finally:
    execute_teardown()    # ✅ 一定会执行
```

**规则 2：Setup 失败时跳过 Steps**
- 如果 `setup` 中某步失败：
  - ❌ 不执行后续的 `setup` 步骤
  - ❌ 不执行 `steps`
  - ✅ 仍然执行 `teardown`
  - 📊 用例结果标记为 **ERROR**（非 FAIL）

**规则 3：变量作用域**
- 全局钩子的变量 → 所有用例可用
- 用例 setup 的变量 → 该用例的 steps + teardown 可用
- 步骤 extract 的变量 → 后续步骤可用

**规则 4：条件执行**
```yaml
teardown:
  - name: "仅当有 order_id 时才取消"
    condition: "${order_id} is not null"   # 支持 Python 表达式
    method: POST
    endpoint: "/orders/${order_id}/cancel"
```

---

#### 3.2.5 技术实现要点

##### 新增数据结构

```python
@dataclass
class HookConfig:
    """钩子配置"""
    name: str
    hook_type: Literal["http", "command", "script"]
    
    # HTTP 类型参数
    method: Optional[str] = None
    endpoint: Optional[str] = None
    headers: Optional[Dict] = None
    json_data: Any = None
    
    # Command 类型参数
    command: Optional[str] = None
    
    # Script 类型参数
    script: Optional[str] = None
    
    # 通用参数
    condition: Optional[str] = None  # 条件表达式
    extract: Optional[Dict] = None   # 变量提取
    ignore_failure: bool = False     # 是否忽略失败
```

##### 核心执行逻辑伪代码

```python
def execute_test_case_with_hooks(test_case):
    result = TestCaseResult(name=test_case.name)

    try:
        # === SETUP PHASE ===
        if test_case.setup:
            for hook in test_case.setup:
                hook_result = execute_hook(hook)
                if not hook_result.success and not hook.ignore_failure:
                    raise SetupError(f"Setup failed: {hook.name}")
                    # teardown 会在 finally 中执行

        # === STEPS PHASE ===
        for step in test_case.steps:
            step_result = execute_step(step)
            result.step_results.append(step_result)

    except SetupError as e:
        result.error_message = str(e)
        result.passed = False
        
    finally:
        # === TEARDOWN PHASE (保证执行) ===
        if test_case.teardown:
            for hook in test_case.teardown:
                if evaluate_condition(hook.condition):  # 条件判断
                    hook_result = execute_hook(hook)
                    # 记录 teardown 结果但不影响用例状态

    return result
```

---

#### 3.2.6 验收标准

**功能验收（Must Have）**

- [ ] **AC-1**: 支持全局/用例两级 setup/teardown 钩子
- [ ] **AC-2**: 钩子支持 HTTP 请求、Shell 命令、Python 脚本三种模式
- [ ] **AC-3**: Teardown 在任何情况下都保证执行（即使 setup/steps 失败）
- [ ] **AC-4**: 钩子中支持变量提取和引用（`${var}`）
- [ ] **AC-5**: 支持 `condition` 条件表达式控制是否执行某钩子
- [ ] **AC-6**: Setup 失败时，用例标记为 ERROR 状态（区别于 FAIL）

**边界验收（Should Have）**

- [ ] **AC-7**: 钩子执行超时可配置（默认继承全局 timeout）
- [ ] **AC-8**: 支持 `ignore_failure: true` 忽略单步失败继续执行
- [ ] **AC-9**: 全局 teardown 即使某个用例的 teardown 失败也继续执行其他用例
- [ ] **AC-10**: 钩子执行结果在报告中可见（可折叠详情）

---

### 3.3 数据驱动测试

#### 3.3.1 用户故事

**作为** 一个 QA 工程师，
**我希望** 能够将测试数据维护在 Excel/CSV 文件中，通过一个 YAML 模板自动生成多个测试用例，
**以便** 测试边界值、异常值等场景时无需复制粘贴大量相似的 YAML 文件。

---

**作为** 一个业务分析师，
**我希望** 能够直接在表格软件（Excel/WPS）中编辑测试数据，
**以便** 利用熟悉的工具管理测试用例，降低学习成本。

---

#### 3.3.2 支持的数据源格式

##### 格式 1：CSV（推荐）

```csv
# test_data/login_cases.csv
username,password,expected_status,expected_error,test_name
admin,correct_pass,200,,管理员正常登录
admin,wrong_pass,401,INVALID_PASSWORD,密码错误
empty_user,pass,400,USERNAME_EMPTY,用户名为空
very_long_username_over_50_chars...,pass,400,USERNAME_TOO_LONG,用户名过长
special_char_<script>,pass,400,INVALID_CHARACTERS,特殊字符注入
```

##### 格式 2：JSON 数组

```json
// test_data/register_cases.json
[
  {
    "username": "valid_user",
    "email": "user@test.com",
    "expected_status": 201,
    "test_tag": "正常注册"
  },
  {
    "username": "ab",
    "email": "user@test.com",
    "expected_status": 400,
    "expected_field": "username",
    "test_tag": "用户名过短"
  },
  {
    "username": "",
    "email": "invalid-email",
    "expected_status": 400,
    "test_tag": "多字段校验失败"
  }
]
```

##### 格式 3：Excel (.xlsx)（可选增强）

| username | password | expected_status | expected_message | test_priority |
|----------|----------|----------------|------------------|--------------|
| admin | 123456 | 200 | 登录成功 | P0 |
| admin | wrong | 401 | 密码错误 | P0 |
| locked_user | 123456 | 403 | 账户已锁定 | P1 |

> 注：需要安装 `openpyxl` 库，可通过 `pip install api-test-agent[excel]` 安装

---

#### 3.3.3 参数化语法

##### YAML 模板定义

```yaml
# tests/data_driven/login_test.yaml
name: "用户登录接口测试（数据驱动）"

# 数据源定义
data_source:
  type: csv                          # 可选: csv, json, excel
  file: test_data/login_cases.csv    # 相对于当前文件的路径
  
  # 列映射（可选：如果列名与字段名不同）
  mapping:
    username: username               # CSV 列名 -> 变量名
    password: password
    expected_code: expected_status
    error_msg: expected_error        # 可选字段，不存在则为 None

# 用例名称模板（支持变量插值）
case_name_template: "登录测试-${test_name}"

# 测试步骤模板（每行数据生成一个独立用例）
template:
  steps:
    - name: "POST /auth/login"
      method: POST
      endpoint: "/auth/login"
      json:
        username: "${data.username}"    # data. 前缀表示来自数据源
        password: "${data.password}"
      
      assertions:
        - type: status_code
          expected: "${data.expected_code}"
        
        # 动态断言（仅当 error_msg 存在时才添加）
        - type: contains
          path: "message"
          value: "${data.error_msg}"
          condition: "${data.error_msg} is not none"  # 条件断言
```

##### 生成的实际用例（内部表示）

上述模板 + CSV 的 5 行数据 → 自动生成 **5 个独立的测试用例**：

```
[用例 1] 登录测试-管理员正常登录
  → POST /auth/login {username: "admin", password: "correct_pass"}
  → 断言: status == 200 ✅

[用例 2] 登录测试-密码错误
  → POST /auth/login {username: "admin", password: "wrong_pass"}
  → 断言: status == 401 ✅
  → 断言: message 包含 "INVALID_PASSWORD" ✅

[用例 3] 登录测试-用户名为空
  → ...

[用例 4] 登录测试-用户名过长
  → ...

[用例 5] 登录测试-特殊字符注入
  → ...
```

---

#### 3.3.4 高级特性

##### 特性 1：数据过滤

```yaml
data_source:
  file: test_data/all_cases.csv
  
  # 仅运行包含特定标签的行
  filter:
    priority: "P0"           # 仅 P0 级别的用例
    # 或者使用表达式
    expression: "int(row['id']) % 2 == 0"  # 仅偶数行
```

##### 特性 2：并行度控制

```yaml
data_source:
  file: test_data/large_dataset.csv  # 1000 行数据
  
  # 数据驱动用例的并发设置
  parallelism:
    enabled: true
    workers: 10                     # 10 并发执行
    batch_size: 50                  # 分批处理（避免内存溢出）
```

##### 特性 3：失败快速停止

```yaml
data_source:
  file: test_data/cases.csv
  
  # 发现 N 个连续失败后停止
  fail_fast:
    enabled: true
    max_consecutive_failures: 5    # 连续 5 个失败后终止
```

##### 特性 4：自定义数据转换器

```python
# hooks/data_transformers.py
def transform_phone_number(value):
    """标准化手机号格式"""
    return f"+86{value[-11:]}"

def generate_timestamp():
    """生成当前时间戳"""
    return str(int(time.time()))
```

```yaml
data_source:
  file: test_data/users.csv
  
  transformers:
    phone: transform_phone_number    # 应用自定义函数
    created_at: generate_timestamp   # 动态生成值
```

---

#### 3.3.5 验收标准

**功能验收（Must Have）**

- [ ] **AC-1**: 支持 CSV 格式数据源，自动解析表头为变量名
- [ ] **AC-2**: 支持 JSON 数组格式数据源
- [ ] **AC-3**: `${data.column}` 语法正确替换数据源中的值
- [ ] **AC-4**: 每行数据生成独立用例，单独统计通过/失败
- [ ] **AC-5**: 用例名称支持动态模板（`${test_name}`）
- [ ] **AC-6**: 数据源缺失或格式错误时给出清晰的错误提示

**高级功能验收（Should Have）**

- [ ] **AC-7**: 支持 Excel (.xlsx) 数据源（需 openpyxl）
- [ ] **AC-8**: 支持 `filter` 过滤特定行的数据
- [ ] **AC-9**: 支持 `condition` 条件断言（动态启用/禁用某些断言）
- [ ] **AC-10**: 支持自定义数据转换器（Python 函数）

**性能验收**

- [ ] **AC-11**: 1000 行 CSV 加载 + 生成用例 < 1 秒
- [ ] **AC-12**: 内存占用与数据量线性相关（无内存泄漏）

---

### 3.4 并发执行与性能测试

#### 3.4.1 用户故事

**作为** 一个 DevOps 工程师，
**希望能够通过 `-workers 10` 参数让 500 个测试用例并发运行**，
**以便** 将 CI 中的测试时间从 30 分钟压缩到 3-5 分钟。

---

**作为** 一个性能工程师，
**希望能够在上线前进行简单的负载测试**（如 100 QPS 持续 5 分钟），
**以便** 及早发现性能瓶颈，避免生产事故。

---

#### 3.4.2 并发执行模型

##### 架构选择：协程（asyncio）

**选型理由**：
- ✅ API 测试是 I/O 密集型任务（90%+ 时间等待网络响应）
- ✅ 协程开销远小于多进程（内存占用低）
- ✅ 可与异步 HTTP 客户端（httpx/aiohttp）无缝配合
- ✅ 共享事件循环，便于协调和限流

##### CLI 接口设计

```bash
# === 基础并发 ===
python api_test_agent.py run tests/ --workers 10         # 10 并发
python api_test_agent.py run tests/ -w 20                 # 短选项
python api_test_agent.py run tests/ --workers auto         # 自动检测 CPU 核心数

# === 性能测试模式 ===
python api_test_agent.py perf tests/load_test.yaml \
  --rps 100 \                   # 目标 RPS
  --duration 300s \             # 持续时间 5 分钟
  --ramp-up 30s \               # 预热 30 秒逐步达到目标 RPS
  --max-concurrent 50           # 最大并发数

# === 输出性能报告 ===
python api_test_agent.py perf tests/ \
  --report performance_report.html  # 专用性能报告
```

##### 并发执行器核心类设计

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List
import time

@dataclass
class ConcurrencyResult:
    """并发执行结果"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_time: float
    parallel_time: float        # 实际耗时（应远低于串行总耗时）
    speedup: float              # 加速比
    worker_count: int
    results: List[TestCaseResult]


class ConcurrentTestRunner:
    """并发测试执行器"""

    def __init__(self, base_runner: TestRunner, max_workers: int = 10):
        self.base_runner = base_runner
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)  # 并发控制

    async def execute_single(self, test_case: dict) -> TestCaseResult:
        """单个用例的异步包装"""
        async with self.semaphore:  # 限制并发数
            # 在线程池中执行同步代码（因为现有 runner 是同步的）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,  # 使用默认 ThreadPoolExecutor
                lambda: self.base_runner.execute_test_case(test_case)
            )
            return result

    async def execute_all(self, test_cases: List[dict]) -> ConcurrencyResult:
        """并发执行所有用例"""
        start_time = time.time()

        tasks = [self.execute_single(tc) for tc in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time

        # 统计结果...
        return ConcurrencyResult(...)
```

---

#### 3.4.3 性能测试模式

##### YAML 配置格式

```yaml
# tests/performance/order_api_load.yaml
name: "订单接口负载测试"

performance:
  mode: load_test                  # 模式: load_test | stress | soak
  
  # 负载参数
  target_rps: 100                  # 目标：每秒 100 请求
  duration: 5m                     # 持续 5 分钟
  ramp_up: 30s                     # 30 秒内逐步达到目标 RPS
  max_concurrent_users: 50         # 最大并发用户数
  
  # 阈值定义（超过则判定为失败）
  thresholds:
    avg_response_time:             # 平均响应时间
      max: 500ms                   # 不能超过 500ms
      alert_on_breach: true        # 超过时告警
      
    p95_response_time:             # P95 响应时间
      max: 1000ms
      
    p99_response_time:             # P99 响应时间
      max: 2000ms
      
    error_rate:                    # 错误率
      max: 1%                      # 不能超过 1%
      
    throughput:                    # 吞吐量
      min: 90 RPS                  # 不能低于 90 RPS（允许 10% 波动）

# 测试步骤（将被重复执行）
steps:
  - name: "创建订单"
    method: POST
    endpoint: "/orders"
    json:
      user_id: "${random_user_id}"     # 随机用户 ID
      items:
        - product_id: "P001"
          quantity: "${random_int(1, 5)}"  # 随机数量
    assertions:
      - type: status_code
        expected: [200, 201]           # 接受范围（性能测试允许波动）
      - type: response_time
        max: 2.0                       # 单次请求不超过 2 秒
```

##### 性能指标采集

```python
@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    
    # 时间指标（毫秒）
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p90_response_time: float
    p95_response_time: float
    p99_response_time: float
    
    # 吞吐量指标
    requests_per_second: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    
    # 错误率
    error_rate: float              # 0.0 - 1.0
    
    # 分布图数据（用于绘制直方图）
    response_time_histogram: List[tuple]  # [(区间, 数量), ...]
    
    # 时间线数据（用于绘制折线图）
    timeline_rps: List[tuple]      # [(时间戳, 当前RPS), ...]
    timeline_errors: List[tuple]   # [(时间戳, 错误数), ...]

class PerformanceCollector:
    """性能数据采集器"""
    
    def __init__(self):
        self.response_times = []
        self.errors = []
        self.start_time = None
        self.lock = asyncio.Lock()
    
    async def record_request(self, response_time_ms: float, success: bool):
        """记录单次请求结果"""
        async with self.lock:
            self.response_times.append(response_time_ms)
            if not success:
                self.errors.append(time.time())
    
    def calculate_metrics(self) -> PerformanceMetrics:
        """计算聚合指标"""
        import numpy as np  # 或自行实现百分位计算
        
        times = np.array(self.response_times)
        
        return PerformanceMetrics(
            avg_response_time=np.mean(times),
            p95_response_time=np.percentile(times, 95),
            p99_response_time=np.percentile(times, 99),
            error_rate=len(self.errors) / len(times),
            # ... 其他指标
        )
```

---

#### 3.4.4 性能报告增强

##### 新增报告元素

**HTML 报告新增模块**：

```
┌─────────────────────────────────────────────┐
│  📊 性能测试报告                            │
├─────────────────────────────────────────────┤
│                                             │
│  ⏱️ 执行摘要                                │
│  ├── 总时长: 5m 30s                         │
│  ├── 总请求数: 28,547                       │
│  ├── 成功率: 99.2%                          │
│  └── 平均 RPS: 94.5                         │
│                                             │
│  📈 响应时间分布                             │
│  ├── [直方图: 响应时间 vs 请求数量]          │
│  ├── 平均: 245ms                            │
│  ├── P50: 180ms                             │
│  ├── P95: 520ms  ✅ (< 1000ms 阈值)         │
│  └── P99: 1200ms ⚠️ (> 1000ms 阈值)        │
│                                             │
│  📉 RPS 时间线                               │
│  ├── [折线图: 时间 vs 当前RPS]              │
│  ├── 目标 RPS: 100 (虚线)                   │
│  └── 实际 RPS: 94-98 (稳定)                 │
│                                             │
│  ❌ 错误分析                                 │
│  ├── Timeout: 23 次 (0.08%)                 │
│  ├── Connection Error: 5 次 (0.02%)         │
│  └── HTTP 5xx: 198 次 (0.69%) ⚠️            │
│                                             │
│  ✅ 阈值检查结果                             │
│  ├── avg_response_time: PASS ✅ (245ms < 500ms) │
│  ├── p95_response_time: PASS ✅ (520ms < 1000ms)│
│  ├── error_rate: FAIL ❌ (0.8% > 1%)        │
│  └── throughput: WARNING ⚠️ (94.5 RPS < 90 RPS) │
│                                             │
└─────────────────────────────────────────────┘
```

---

#### 3.4.5 验收标准

**并发执行验收（Must Have）**

- [ ] **AC-1**: `-workers N` 参数生效，N 个用例真正并行执行
- [ ] **AC-2**: 10 并发下，100 个用例的执行时间 ≈ 串行时间的 1/10（±20%）
- [ ] **AC-3**: 单个用例失败不影响其他并发的用例（错误隔离）
- [ ] **AC-4**: 并发结果正确聚合到统一的 TestSuiteResult
- [ ] **AC-5**: 并发模式下变量作用域隔离（用例 A 的变量不会污染用例 B）

**性能测试验收（Should Have）**

- [ ] **AC-6**: `perf` 子命令可执行负载测试
- [ ] **AC-7**: 支持 RPS 控制（误差 ±10% 以内）
- [ ] **AC-8**: 支持 ramp-up 渐进式加压
- [ ] **AC-9**: 采集完整的性能指标（平均/P95/P99/错误率）
- [ ] **AC-10**: 阈值超标时自动标记 FAIL 并高亮显示
- [ ] **AC-11**: 生成专用的 HTML 性能报告（含图表）

**性能基准**

- [ ] **AC-12**: 并发调度开销 < 5ms/用例
- [ ] **AC-13**: 支持 100+ 并发而不出现 GIL 锁竞争问题

---

### 3.5 GUI 可视化编辑器

#### 3.5.1 用户故事

**作为** 一个产品经理（不懂编程），
**希望通过拖拽的方式编排测试步骤**，像画流程图一样简单，
**以便** 我能够参与测试用例的设计和评审工作。

---

**作为** 一个 QA 新人，
**希望在界面上填写表单就能配置断言**，而不用记忆复杂的 YAML 语法，
**以便** 快速上手编写测试用例。

---

#### 3.5.2 技术栈选型

| 层面 | 选型 | 理由 |
|------|------|------|
| **前端框架** | React 18 + TypeScript | 生态成熟、组件丰富 |
| **UI 组件库** | Ant Design 5.x | 企业级 UI、表单丰富 |
| **流程图库** | React Flow | 拖拽编排、节点自定义 |
| **状态管理** | Zustand | 轻量、适合中等复杂度 |
| **后端框架** | FastAPI (Python) | 异步高性能、自动文档 |
| **实时通信** | WebSocket | 编辑器双向同步 |
| **构建工具** | Vite | 开发体验好、构建快 |

---

#### 3.5.3 核心功能模块

##### 模块 1：可视化步骤编排器

**界面概念**：

```
┌─────────────────────────────────────────────────────────────┐
│  🧪 测试用例编辑器 - 用户登录流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 📝 输入参数   │ →  │ 🔐 调用API   │ →  │ ✅ 断言验证   │  │
│  │              │    │              │    │              │  │
│  │ username:    │    │ POST /login  │    │ status: 200  │  │
│  │ [________]   │    │ Body: {...}  │    │ has token ✓  │  │
│  │ password:    │    │              │    │ time < 2s ✓  │  │
│  │ [********]   │    │              │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         ↓                   ↓                   ↓          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 🔀 条件分支（可选）                                  │  │
│  │   IF status == 200 THEN → 提取 token                 │  │
│  │   ELSE → 记录错误日志                                │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  [+ 添加步骤]    [+ 添加条件分支]    [+ 添加循环]           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [🔄 运行测试]  [👁️ 预览 YAML]  [💾 保存]  [📤 导出]        │
└─────────────────────────────────────────────────────────────┘
```

**交互操作**：

1. **拖拽添加步骤**
   - 从左侧组件面板拖拽「HTTP 请求」「断言」「变量提取」等节点到画布
   - 自动连线表示执行顺序

2. **点击编辑属性**
   - 点击节点弹出右侧属性面板
   - 表单化填写 URL、Headers、Body 等

3. **实时预览**
   - 底部面板实时显示生成的 YAML 代码
   - YAML ↔ GUI 双向同步（修改任一方，另一方自动更新）

4. **调试运行**
   - 点击「运行」按钮，右侧面板显示实时请求/响应
   - 高亮当前执行的步骤节点

---

##### 模块 2：智能表单助手

**针对不同节点类型的定制表单**：

**HTTP 请求节点**：
```
┌─ 请求配置 ──────────────────────────────┐
│                                         │
│  方法: [GET ▼]  端点: [/api/users____]  │
│                                         │
│  ▼ Query Parameters                     │
│  ┌──────────┬──────────┬──────────┐    │
│  │ Key      │ Value    │ 操作     │    │
│  ├──────────┼──────────┼──────────┤    │
│  │ page     │ 1        │ [删除]   │    │
│  │ size     │ 20       │ [删除]   │    │
│  │ [+ 添加] │          │          │    │
│  └──────────┴──────────┴──────────┘    │
│                                         │
│  ▼ Headers                              │
│  Content-Type: [application/json ▼]     │
│ Authorization:  [Bearer ${token}___]     │
│                                         │
│  ▼ Body                                 │
│  ○ None  ○ Form Data  ● JSON           │
│  {                                      │
│    "username": "[________________]",     │
│    "password": "[________________]"     │
│  }                                      │
│                                         │
└─────────────────────────────────────────┘
```

**断言节点**：
```
┌─ 断言配置 ──────────────────────────────┐
│                                         │
│  断言类型: [状态码检查 ▼]               │
│                                         │
│  期望值: [200_____]                     │
│                                         │
│  [+ 添加更多断言]                        │
│                                         │
│  ── 已添加的断言 ──                      │
│  ✅ 状态码 == 200                        │
│  ✅ 响应时间 < 2.0s                      │
│  ✅ 包含字段 "token"                     │
│  ✅ token 类型是 string                  │
│                                         │
└─────────────────────────────────────────┘
```

**智能提示功能**：
- 输入端点时自动补全历史 URL
- 选择断言类型时显示该类型的参数说明
- 引用变量时下拉提示已定义的变量列表

---

##### 模块 3：YAML 双向同步引擎

**架构**：

```typescript
// frontend/src/engine/YamlSyncEngine.ts

class YamlSyncEngine {
  private yamlToGui(yamlString: string): GraphData {
    // 解析 YAML → 内部 AST → 图形数据
    const ast = this.parseYaml(yamlString);
    return this.astToGraph(ast);
  }

  private guiToYaml(graphData: GraphData): string {
    // 图形数据 → 内部 AST → YAML 字符串
    const ast = this.graphToAst(graphData);
    return this.astToYaml(ast);
  }

  // 监听 GUI 变更 → 更新 YAML 预览
  onGraphChange(callback: (yaml: string) => void) {
    this.graph.onNodesChange((nodes) => {
      const newYaml = this.guiToYaml(this.graph.getData());
      callback(newYaml);
    });
  }

  // 监听 YAML 编辑 → 更新 GUI
  onYamlEdit(newYaml: string) {
    const graphData = this.yamlToGui(newYaml);
    this.graph.setData(graphData);  // 触发重绘
  }
}
```

---

#### 3.5.4 UI/UX 设计要点

##### 设计原则

1. **渐进式复杂度**
   - 默认显示简化视图（仅关键字段）
   - 点击「高级选项」展开完整配置
   - 新手不会被吓跑，专家不被限制

2. **即时反馈**
   - 必填字段未填时，节点边框变红 + tooltip 提示
   - YAML 语法错误时，对应节点高亮并显示错误信息
   - 保存前自动校验完整性

3. **快捷操作**
   - Ctrl+S 保存
   - Ctrl+Enter 运行测试
   - Ctrl+D 复制节点
   - Delete 删除选中节点
   - Ctrl+Z 撤销（支持 50 步历史）

4. **响应式布局**
   - 左侧：组件面板（可折叠）
   - 中间：画布区域（主工作区）
   - 右侧：属性面板（选中节点时显示）
   - 底部：YAML 预览 / 控制台输出（可切换标签页）

##### 界面原型描述（文字版）

**主界面布局**：

```
┌──────────────────────────────────────────────────────────────────┐
│  🚀 API Test Agent Editor                    [用户] [设置] [?]   │
├────────┬─────────────────────────────────────┬───────────────────┤
│        │                                     │                   │
│  📦 组件│          🎨 画布区域               │   ⚙️ 属性面板     │
│        │                                     │                   │
│ ○ HTTP │    ┌─────→ ┌─────→ ┌─────→ ┌────┐  │  节点: POST /login│
│ ○ 断言 │    │Start│ │Login│ │提取 │ │End│  │  ─────────────── │
│ ○ 变量 │    └─────→ └─────→ └─────→ └────┘  │  方法: [POST ▼]   │
│ ○ 循环 │                                     │  端点: [/login__] │
│ ○ 条件 │              [拖拽节点到此处]        │                   │
│ ○ 脚本 │                                     │  ▼ 请求体          │
│        │                                     │  {                 │
│ ────── │                                     │    "user": ""     │
│ 📂 用例 │                                     │  }                 │
│  test1 │                                     │                   │
│  test2 │                                     │  ▼ 断言            │
│  test3 │                                     │  ☑ status == 200  │
│  [新建] │                                     │  ☑ time < 2s      │
│        │                                     │  [+ 添加]         │
├────────┴─────────────────────────────────────┴───────────────────┤
│  [YAML 预览] [控制台输出] [测试报告]                    [运行 ▶]  │
└──────────────────────────────────────────────────────────────────┘
```

---

#### 3.5.5 技术实现路线图

##### Phase 1：MVP（第 9-10 周）

**目标**：基本可用，支持最常用的功能

- [x] React 项目脚手架搭建
- [x] 基础画布 + 节点拖拽（React Flow）
- [x] HTTP 请求节点的表单配置
- [x] 基础断言节点（status_code, equal, contains）
- [x] YAML 导出功能（单向：GUI → YAML）
- [x] 通过后端 API 运行测试并展示结果

**不包含**：
- 条件分支、循环
- YAML 导入（反向同步）
- 变量自动补全
- 多用例管理

##### Phase 2：完善（第 11-12 周）

- [ ] YAML 双向同步引擎
- [ ] 所有断言类型的表单支持
- [ ] 变量提取节点
- [ ] Hook 节点（setup/teardown）
- [ ] 用例列表管理（左侧面板）
- [ ] 深色/浅色主题切换
- [ ] 快捷键系统

##### Phase 3：高级（v2.1/v2.2）

- [ ] 条件分支与循环节点
- [ ] 数据驱动测试的可视化配置
- [ ] 团队协作（多人同时编辑）
- [ ] 版本历史对比
- [ ] 插件市场集成

---

#### 3.5.6 验收标准

**MVP 功能验收（Phase 1）**

- [ ] **AC-1**: 能通过拖拽创建至少 3 种节点（HTTP 请求、断言、变量提取）
- [ ] **AC-2**: 能在属性面板配置 URL、方法、Headers、Body
- [ ] **AC-3**: 能导出为合法的 YAML 文件
- [ ] **AC-4**: 能调用后端 API 运行测试并在界面查看结果
- [ ] **AC-5**: 界面加载时间 < 3 秒（首屏）

**用户体验验收（Phase 2）**

- [ ] **AC-6**: YAML ↔ GUI 双向同步，延迟 < 500ms
- [ ] **AC-7**: 支持 12 种断言类型的可视化配置
- [ ] **AC-8**: 支持撤销/重做（至少 20 步）
- [ ] **AC-9**: 表单验证实时反馈（< 200ms）
- [ ] **AC-10**: 支持键盘快捷键（保存、运行、复制、删除）

**兼容性验收**

- [ ] **AC-11**: 支持 Chrome 90+、Firefox 88+、Safari 14+、Edge 90+
- [ ] **AC-12**: 响应式布局，最小分辨率 1280x720
- [ ] **AC-13**: 无障碍访问基础支持（ARIA 标签、键盘导航）

---

**[第3章全部完成 ✓]** 五大核心功能需求规格已详尽阐述。


---

## 4. 非功能性需求

### 4.1 性能要求

| 指标 | 要求 | 测量方法 | 优先级 |
|------|------|---------|--------|
| **单用例执行开销** | < 100ms（不含网络时间） | 运行空用例测量框架耗时 | P0 |
| **配置加载速度** | < 10ms（即使有大量环境） | 计时加载 environments.yaml | P0 |
| **并发调度开销** | < 5ms/用例 | 对比串行与并发的总耗时差 | P0 |
| **YAML 解析性能** | 1000 行 YAML < 50ms | 使用 timeit 基准测试 | P1 |
| **报告生成速度** | 500 个用例的 HTML 报告 < 3s | 计时 generate_html_report() | P1 |
| **GUI 首屏加载** | < 3s（局域网） | Chrome DevTools Performance | P2 |
| **内存占用** | 基线 + 新功能 < 20MB 增量 | memory_profiler | P1 |

**性能基线（v1.0 实测数据）**：
- 单用例：~45ms 框架开销
- 100 个用例串行：~4.5s（不含网络）
- 报告生成：~0.8s / 100 用例

---

### 4.2 兼容性要求

#### Python 版本兼容性

| Python 版本 | 支持状态 | 说明 |
|-------------|---------|------|
| 3.7 | ✅ 支持（最低版本） | 保持与 v1.0 一致 |
| 3.8 | ✅ 完全支持 | 可使用 walrus operator `:=` |
| 3.9 | ✅ 完全推荐 | 字典合并语法 `{**a, \*\*b}` |
| 3.10 | ✅ 完全支持 | Pattern Matching（可选使用） |
| 3.11+ | ✅ 支持 | 异常组语法增强 |
| 3.6 及以下 | ❌ 不支持 | 已 EOL |

#### 操作系统兼容性

| 系统 | 最低版本 | 测试覆盖 |
|------|---------|---------|
| **Windows** | Windows 10 / Server 2016 | ✅ CI 自动化测试 |
| **macOS** | macOS 10.15 (Catalina) | ✅ 社区反馈验证 |
| **Linux** | Ubuntu 18.04 LTS | ✅ 主要开发环境 |

#### 第三方库依赖约束

```txt
# requirements.txt - 核心依赖
requests>=2.28.0,<3.0.0      # HTTP 客户端
PyYAML>=6.0,<7.0.0           # YAML 解析

# requirements-dev.txt - 开发依赖
pytest>=7.0                  # 单元测试
pytest-cov>=4.0              # 覆盖率
black>=23.0                  # 代码格式化
flake8>=6.0                  # Lint 检查

# requirements-optional.txt - 可选依赖
openpyxl>=3.1                # Excel 支持（数据驱动）
httpx>=0.24                 # 异步 HTTP 客户端（并发模式）
```

**原则**：核心功能零额外依赖，高级功能按需安装。

---

### 4.3 安全性要求

#### 4.3.1 敏感信息保护

| 场景 | 安全措施 | 实现方式 |
|------|---------|---------|
| **API Key 存储** | 不硬编码在代码中 | `.env` 文件 + `.gitignore` |
| **日志脱敏** | 自动检测并隐藏敏感字段 | 正则匹配 `*_KEY`, `*_TOKEN`, `*_PASSWORD` |
| **配置文件加密** | 可选 AES-256 加密 | `api_test_agent.py encrypt config.yaml` |
| **环境变量注入** | 从系统环境变量读取 | `os.environ.get()` |

#### 4.3.2 输入验证

- **YAML 解析安全**：使用 `yaml.safe_load()` 而非 `yaml.load()`（防止代码注入）
- **Shell 命令执行**：钩子中的 `command` 类型需白名单校验
- **文件路径遍历防护**：限制数据源文件只能在项目目录内
- **正则表达式 ReDoS**：用户自定义正则设置超时（< 1s）

#### 4.3.3 网络安全

- **TLS 版本**：强制 TLS 1.2+
- **证书验证**：默认启用，可配置禁用（仅用于测试环境）
- **请求头安全**：自动添加安全相关 headers（可选）

---

### 4.4 可维护性要求

#### 4.4.1 代码质量指标

| 指标 | 目标值 | 工具 |
|------|--------|------|
| **单元测试覆盖率** | ≥ 80%（核心模块 ≥ 90%） | pytest-cov |
| **复杂度（圈复杂度）** | 单函数 ≤ 15 | radon |
| **代码重复率** | < 5% | pylint |
| **文档字符串覆盖率** | 100%（公共 API） | pydocstyle |
| **类型注解覆盖率** | ≥ 80%（公共 API） | mypy |

#### 4.4.2 文档要求

- 每个**新增模块**必须有：
  - [ ] 模块级 docstring（说明用途）
  - [ ] 公共函数/类的 docstring（参数、返回值、示例）
  - [ ] 至少一个**完整的使用示例**（在 `examples/` 目录）

- 每个**新功能**必须更新：
  - [ ] README.md 的 Quick Start
  - [ ] CHEATSHEET.md 速查表
  - [ ] CHANGELOG.md 变更日志

#### 4.4.3 日志规范

```python
# 日志级别使用指南
logger.debug("变量替换详情: %s → %s", original, replaced)  # 调试信息
logger.info("执行步骤: %s %s", method, endpoint)              # 关键流程
logger.warning("重试第 %d 次: %s", attempt, url)               # 异常但可恢复
logger.error("请求失败: %s (status=%d)", msg, code)           # 业务错误
```

---

### 4.5 可扩展性要求

#### 4.5.1 插件架构设计原则

```
┌─────────────────────────────────────────────┐
│              核心引擎 (Core)                 │
│  ┌─────────┬─────────┬─────────┐          │
│  │ Runner  │ Assert  │ Report  │          │
│  └────┬────┴────┬────┴────┬────┘          │
│       │         │         │                │
│  ═════╧══════ ══╧══════ ══╧══════         │
│       插件接口 (Plugin Interface)          │
│  ┌────┴────┐ ┌┴──────┐ ┌┴────┐          │
│  │ Database│ │ Redis │ │GraphQL│ ...     │
│  └─────────┘ └───────┘ └─────┘          │
└─────────────────────────────────────────────┘
```

**插件必须实现的标准接口**：

```python
class BasePlugin(ABC):
    """所有插件的基类"""

    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass

    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass

    @abstractmethod
    def register(self, runner: 'TestRunner'):
        """注册到 runner（添加新的步骤类型或断言类型）"""
        pass
```

#### 4.5.2 配置扩展点

- 自定义断言类型注册
- 自定义数据源适配器（如数据库直连）
- 自定义报告模板
- 自定义 CLI 子命令

---

## 5. 技术架构设计

### 5.1 整体架构图

#### v2.0 架构总览（分层架构）

```
┌─────────────────────────────────────────────────────────────────┐
│                      用户层 (User Layer)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   CLI 工具    │  │  GUI 编辑器   │  │   Python API        │   │
│  │ api_test_     │  │  (React Web) │  │   TestRunner()      │   │
│  │ agent.py      │  │              │  │                      │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                  │                      │             │
├─────────┼──────────────────┼──────────────────────┼─────────────┤
│         │         编排层 (Orchestration Layer)    │             │
│         ▼                  ▼                      ▼             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Test Orchestrator                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │   │
│  │  │ Environment│  │  Hook    │  │ Data-    │  │Concurr-│  │   │
│  │  │ Manager   │  │  Engine  │  │ Driver   │  │ ency   │  │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │   │
│  └───────┼─────────────┼─────────────┼─────────────┼────────┘   │
├──────────┼─────────────┼─────────────┼─────────────┼────────────┤
│          │     执行层 (Execution Layer)               │            │
│          ▼                                          ▼            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Test Runner                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │   │
│  │  │ Variable │  │ Step     │  │ Performance Collector │  │   │
│  │  │ Context  │  │ Executor │  │ (perf mode only)     │  │   │
│  │  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │   │
│  └───────┼─────────────┼─────────────────────┼──────────────┘   │
├──────────┼─────────────┼─────────────────────┼──────────────────┤
│          │    能力层 (Capability Layer)       │                  │
│          ▼                                    ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  API Client  │  │Assert Engine │  │  Report Generator  │    │
│  │ (requests/   │  │ (12+ types   │  │ (HTML/MD/JSON +   │    │
│  │  httpx)      │  │  + custom)   │  │  Perf Report)     │    │
│  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘    │
│         │                 │                    │                │
├─────────┼─────────────────┼────────────────────┼────────────────┤
│         │      基础设施层 (Infrastructure Layer)  │                │
│         ▼                                         ▼                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Config Mgr   │  │ Logger      │  │ Utils & Helpers    │    │
│  │ (.env/YAML)  │  │ (logging)   │  │ (format, hash...)  │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### 5.2 模块依赖关系

#### 核心模块依赖图

```
api_test_agent.py (入口)
    ├── config.py ← environment.py (新增)
    │       └── utils.py
    ├── test_runner.py
    │       ├── api_client.py
    │       ├── assert_engine.py
    │       ├── hook_engine.py (新增)
    │       ├── data_driver.py (新增)
    │       └── concurrent_runner.py (新增)
    └── report_generator.py
            └── perf_report_generator.py (新增)

gui_editor/ (独立前端项目)
    ├── frontend/ (React)
    └── backend/ (FastAPI)
            └── test_runner.py (复用核心逻辑)
```

#### 新增模块清单

| 模块名 | 文件路径 | 职责 | 代码量估算 |
|--------|---------|------|-----------|
| **EnvironmentManager** | `environment.py` | 多环境配置管理 | ~250 行 |
| **HookEngine** | `hook_engine.py` | 钩子执行引擎 | ~300 行 |
| **DataDriver** | `data_driver.py` | 数据驱动测试引擎 | ~350 行 |
| **ConcurrentRunner** | `concurrent_runner.py` | 并发执行器 | ~280 行 |
| **PerfCollector** | `perf_collector.py` | 性能数据采集 | ~200 行 |
| **PerfReportGenerator** | `perf_report_generator.py` | 性能报告生成 | ~400 行 |
| **PluginManager** | `plugin_manager.py` | 插件加载与管理 | ~200 行 |

**总计新增代码量**：~1980 行（约 +40% 相对 v1.0）

---

### 5.3 数据流设计

#### 典型场景：带环境切换 + 钩子 + 并发的完整数据流

```
[用户输入]
python api_test_agent.py run tests/ --env staging --workers 5
    ↓
[1. 配置初始化]
Config.load()
  → Config.__init__()
  → EnvironmentManager.load_environment("staging")
  → 合并: defaults + staging + .env.staging + --var overrides
  → 输出: final_config (dict)
    ↓
[2. 测试套件加载]
TestRunner.load_test_directory("tests/")
  → 遍历 *.yaml 文件
  → 对每个文件: YAML.safe_load() → dict
  → 检查是否包含 data_source (数据驱动?)
    ↓ 是 → DataDriver.expand_template(template, csv_data)
           → 返回 N 个 TestCase 对象
    ↓ 否 → 直接创建 TestCase 对象
  → 输出: List[TestCase]
    ↓
[3. 并发执行分发]
ConcurrentRunner.execute_all(test_cases, workers=5)
  → 创建 asyncio.Semaphore(5)
  → 为每个 TestCase 创建异步任务
  → 任务内部:
    ↓
    [4. 单用例执行（在线程池中）]
    execute_test_case_with_hooks(test_case):
      try:
        a) HookEngine.execute_global_setup()  (仅首次)
        b) HookEngine.execute_setup(test_case.setup)
        c) for step in test_case.steps:
             VariableContext.replace_vars(step)     # ${var} 替换
             APIClient.request(method, endpoint, ...)  # 发送 HTTP
             AssertEngine.validate_response(response, assertions)  # 断言
             VariableContext.extract_variables(response, extract)  # 提取变量
        d) HookEngine.execute_teardown(test_case.teardown)  # finally
      except:
        记录错误但不中断其他用例
      → 输出: TestCaseResult
    ↓
[5. 结果聚合]
ConcurrencyResult = gather(all_results)
  → 统计 passed/failed/total
  → 计算 speedup = serial_time / parallel_time
    ↓
[6. 报告生成]
ReportGenerator.generate_html_report(result)
  → 如果是 perf mode:
    PerfReportGenerator.generate(result)  # 含图表
  → 否则:
    原有 HTML/MD/JSON 报告
    ↓
[7. 输出]
→ 控制台摘要 (colored output)
→ 报告文件路径
→ 退出码 (0=全部通过, 1=有失败)
```

---

### 5.4 接口定义

#### 核心 API 接口（Python API）

```python
from api_test_agent import TestRunner, EnvironmentManager, ConcurrentRunner

# === 基础用法（向后兼容 v1.0）===
runner = TestRunner(base_url="https://api.example.com")
result = runner.execute_test_file("tests/user_api.yaml")
runner.close()

# === v2.0 新增：环境管理 ===
env_mgr = EnvironmentManager("configs/environments.yaml")
config = env_mgr.load_environment("staging")
config = env_mgr.apply_overrides({"timeout": "60"})

runner = TestRunner(environment=config)
result = runner.execute_test_directory("tests/")

# === v2.0 新增：并发执行 ===
concurrent = ConcurrentRunner(runner, max_workers=10)
result = await concurrent.execute_all(test_cases)
print(f"加速比: {result.speedup:.1f}x")

# === v2.0 新增：性能测试 ===
from api_test_agent import PerformanceTestRunner

perf_runner = PerformanceTestRunner(
    target_rps=100,
    duration=300,  # 5 分钟
    ramp_up=30
)
perf_result = perf_runner.execute_load_test("tests/performance/load.yaml")
print(f"P95 响应时间: {perf_result.metrics.p95_response_time}ms")
```

#### GUI 后端 API（FastAPI）

```yaml
# GUI Editor Backend API

POST /api/test/run
  Body: { yaml_content: string, env: string }
  Response: { task_id: uuid }

GET /api/test/result/{task_id}
  Response: { status: running|completed, result: TestSuiteResult }

GET /api/environments
  Response: { environments: string[] }  # 列出可用环境

POST /api/yaml/validate
  Body: { yaml_content: string }
  Response: { valid: bool, errors: string[] }

WS /ws/test/realtime/{task_id}
  WebSocket: 实时推送步骤执行进度
```

---

### 5.5 技术选型说明

| 技术决策 | 选择方案 | 替代方案 | 选择理由 |
|---------|---------|---------|---------|
| **HTTP 客户端** | requests (同步) + httpx (异步) | aiohttp | 生态成熟、requests 已有大量使用 |
| **异步模型** | asyncio + ThreadPoolExecutor | multiprocessing | I/O 密集型适合协程，线程池包装现有同步代码 |
| **前端框架** | React 18 + TypeScript | Vue 3 | 社区更大、React Flow 流程图库成熟 |
| **后端框架** | FastAPI | Flask | 原生异步、自动 OpenAPI 文档 |
| **配置格式** | YAML | JSON/TOML | 支持注释、与测试用例格式一致 |
| **性能图表** | Chart.js (内嵌 HTML) | ECharts / D3.js | 轻量、无需额外服务端渲染 |
| **CSV 解析** | 内置 csv 模块 | pandas | 零依赖、足够满足需求 |
| **包管理** | pip + setup.py | poetry | 更广泛的社区接受度 |

---

## 6. 实施计划与里程碑

### 6.1 版本规划概览

| 版本 | 时间范围 | 核心目标 | 主要功能 |
|------|---------|---------|---------|
| **v2.0-alpha** | Week 1-2 | 核心基础 | 环境管理 + 钩子机制 + 数据驱动 |
| **v2.0-beta** | Week 3-4 | 并发能力 | 并发执行 + 性能测试基础版 |
| **v2.0-rc** | Week 5-6 | 稳定性 | Bug 修复 + 文档完善 + 向后兼容测试 |
| **v2.0.0** | Week 8 | 正式发布 | 全部 Phase 1 功能稳定版 |
| **v2.1.0** | Week 9-12 | 平台化 | GUI 编辑器 MVP + Mock 服务 |
| **v2.2.0** | Week 13-16 | 生态完善 | 插件系统 + 认证增强 + 报告升级 |

---

### 6.2 Phase 1 详细任务分解（Week 1-4）

#### Week 1-2：核心基础（v2.0-alpha）

**目标**：完成环境管理、钩子机制、数据驱动三大核心功能

##### Sprint 1.1：环境管理（Day 1-3）

| 任务ID | 任务描述 | 负责人 | 工时估计 | 依赖 | 产出 |
|--------|---------|--------|---------|------|------|
| T1.1.1 | 创建 `environment.py` 模块骨架 | Dev-A | 4h | - | 代码 |
| T1.1.2 | 实现 YAML 配置解析与合并逻辑 | Dev-A | 6h | T1.1.1 | 代码+单测 |
| T1.1.3 | 实现 `.env` 文件加载器 | Dev-A | 3h | T1.1.1 | 代码+单测 |
| T1.1.4 | 修改 `config.py` 集成 EnvironmentManager | Dev-A | 2h | T1.1.2 | 代码 |
| T1.1.5 | 扩展 CLI 参数 (`--env`, `--var`) | Dev-B | 3h | T1.1.4 | 代码 |
| T1.1.6 | 实现配置校验与错误提示 | Dev-A | 3h | T1.1.2 | 代码+单测 |
| T1.1.7 | 编写集成测试（端到端场景） | QA | 4h | T1.1.1-T1.1.6 | 测试用例 |
| T1.1.8 | 编写环境管理文档和示例 | TechWriter | 3h | T1.1.7 | 文档 |

**里程碑检查点**（Day 3 结束）：
- [ ] `--env staging` 参数可用且正确加载配置
- [ ] `.env.staging` 文件自动加载
- [ ] `--var key=value` 覆盖生效
- [ ] 单元测试覆盖率 > 80%
- [ ] 至少 3 个端到端示例通过

##### Sprint 1.2：钩子机制（Day 4-6）

| 任务ID | 任务描述 | 负责人 | 工时估计 | 依赖 | 产出 |
|--------|---------|--------|---------|------|------|
| T1.2.1 | 设计 HookConfig 数据结构 | Dev-A | 2h | - | 设计文档 |
| T1.2.2 | 创建 `hook_engine.py` 模块 | Dev-A | 4h | T1.2.1 | 代码 |
| T1.2.3 | 实现 HTTP 类型钩子执行器 | Dev-A | 4h | T1.2.2 | 代码+单测 |
| T1.2.4 | 实现 Command 类型钩子执行器 | Dev-B | 3h | T1.2.2 | 代码+单测 |
| T1.2.5 | 实现 Script 类型钩子执行器 | Dev-A | 3h | T1.2.2 | 代码+单测 |
| T1.2.6 | 修改 TestRunner 集成钩子生命周期 | Dev-A | 6h | T1.2.3-T1.2.5 | 代码 |
| T1.2.7 | 实现 condition 条件表达式求值 | Dev-A | 3h | T1.2.6 | 代码+单测 |
| T1.2.8 | 编写钩子机制的完整示例 | Dev-B | 3h | T1.2.6 | 示例代码 |

**里程碑检查点**（Day 6 结束）：
- [ ] global_setup/global_teardown 正确执行
- [ ] setup 失败时 teardown 仍执行
- [ ] condition 表达式正确求值
- [ ] 钩子结果在报告中可见

##### Sprint 1.3：数据驱动测试（Day 7-10）

| 任务ID | 任务描述 | 负责人 | 工时估计 | 依赖 | 产出 |
|--------|---------|--------|---------|------|------|
| T1.3.1 | 创建 `data_driver.py` 模块 | Dev-B | 3h | - | 代码 |
| T1.3.2 | 实现 CSV 数据源解析器 | Dev-B | 4h | T1.3.1 | 代码+单测 |
| T1.3.3 | 实现 JSON 数据源解析器 | Dev-B | 2h | T1.3.1 | 代码+单测 |
| T1.3.4 | 实现模板参数化引擎（${data.col}） | Dev-A | 6h | T1.3.2 | 代码+单测 |
| T1.3.5 | 实现用例名动态生成 | Dev-B | 2h | T1.3.4 | 代码 |
| T1.3.6 | 集成到 TestRunner（自动检测 data_source） | Dev-A | 4h | T1.3.4 | 代码 |
| T1.3.7 | 实现 filter/transformer 高级特性 | Dev-B | 4h | T1.3.6 | 代码（可选） |
| T1.3.8 | 性能基准测试（1000行 CSV） | QA | 2h | T1.3.6 | 性能报告 |
| T1.3.9 | 编写数据驱动测试文档和示例 | TechWriter | 3h | T1.3.6 | 文档 |

**Alpha 版本发布准备**（Day 10 结束）：
- [ ] 三大核心功能集成测试通过
- [ ] 更新 README 和 CHANGELOG
- [ ] 发布 v2.0-alpha 到 PyPI (test-pypi)
- [ ] 收集早期用户反馈

---

#### Week 3-4：并发与性能（v2.0-beta）

##### Sprint 2.1：并发执行（Day 11-14）

| 任务ID | 任务描述 | 负责人 | 工时估计 | 依赖 | 产出 |
|--------|---------|--------|---------|------|------|
| T2.1.1 | 创建 `concurrent_runner.py` | Dev-A | 3h | - | 代码 |
| T2.1.2 | 基于 asyncio.Semaphore 实现并发控制 | Dev-A | 6h | T2.1.1 | 代码+单测 |
| T2.1.3 | 实现线程池包装（兼容现有同步 runner） | Dev-A | 4h | T2.1.2 | 代码 |
| T2.1.4 | 实现变量作用域隔离（每个用例独立 context） | Dev-A | 4h | T2.1.3 | 代码+单测 |
| T2.1.5 | 扩展 CLI `-w/--workers` 参数 | Dev-B | 2h | T2.1.2 | 代码 |
| T2.1.6 | 并发结果聚合与统计 | Dev-A | 3h | T2.1.4 | 代码 |
| T2.1.7 | 并发性能基准测试（10/50/100 并发） | QA | 3h | T2.1.6 | 性能报告 |

##### Sprint 2.2：性能测试模式（Day 15-18）

| 任务ID | 任务描述 | 负责人 | 工时估计 | 依赖 | 产出 |
|--------|---------|--------|---------|------|------|
| T2.2.1 | 创建 `perf_collector.py` 数据采集器 | Dev-B | 4h | - | 代码 |
| T2.2.2 | 实现响应时间分布统计（P50/P95/P99） | Dev-B | 3h | T2.2.1 | 代码 |
| T2.2.3 | 实现 RPS 控制器（token bucket 算法） | Dev-A | 6h | T2.2.1 | 代码+单测 |
| T2.2.4 | 实现 ramp-up 渐进式加压逻辑 | Dev-A | 3h | T2.2.3 | 代码 |
| T2.2.5 | 扩展 CLI `perf` 子命令 | Dev-B | 3h | T2.2.3 | 代码 |
| T2.2.6 | 创建 `perf_report_generator.py` | Dev-B | 6h | T2.2.2 | 代码 |
| T2.2.7 | 实现阈值检查与告警逻辑 | Dev-A | 3h | T2.2.4 | 代码 |
| T2.2.8 | 性能测试端到端验证 | QA | 4h | T2.2.6 | 测试报告 |

**Beta 版本发布准备**（Week 4 结束）：
- [ ] 所有 Phase 1 功能集成测试
- [ ] 性能回归测试（确保不比 v1.0 慢）
- [ ] 向后兼容性测试（v1.0 用例无需修改）
- [ ] 发布 v2.0-beta

---

#### Week 5-6：稳定性打磨（v2.0-rc）

| 任务类别 | 具体任务 | 工时 |
|---------|---------|------|
| **Bug 修复** | 修复 Beta 测试发现的缺陷 | 16h |
| **边界情况** | 处理异常输入、极端场景 | 8h |
| **文档完善** | 补充所有新功能的 API 文档和示例 | 12h |
| **性能优化** | 热点代码 profiling 和优化 | 8h |
| **安全审计** | 依赖漏洞扫描、敏感信息泄露检查 | 4h |
| **CI 完善** | GitHub Actions 多平台测试矩阵 | 4h |

**RC 发布标准**：
- [ ] 0 个 P0/P1 级 Bug
- [ ] 核心模块测试覆盖率 ≥ 85%
- [ ] 5 个真实项目的迁移验证通过
- [ ] 文档完整性审查通过

---

### 6.3 Phase 2 详细任务分解（Week 9-12）：GUI 编辑器

> 注：GUI 编辑器为独立前端项目，可与后端并行开发

#### Sprint 3.1：前端基础设施（Week 9）

| 任务 | 描述 | 工时 |
|------|------|------|
| G1 | React + TypeScript + Vite 项目初始化 | 4h |
| G2 | Ant Design + React Flow 组件库集成 | 3h |
| G3 | 基础布局实现（三栏布局） | 6h |
| G4 | Zustand 状态管理搭建 | 3h |
| G5 | FastAPI 后端项目初始化 | 3h |
| G6 | WebSocket 连接建立（实时通信） | 4h |

#### Sprint 3.2：核心编辑器（Week 10）

| 任务 | 描述 | 工时 |
|------|------|------|
| G7 | 节点拖拽与连线（React Flow） | 8h |
| G8 | HTTP 请求节点属性面板 | 6h |
| G9 | 断言节点属性面板 | 4h |
| G10 | 右键菜单（复制/删除/禁用） | 3h |
| G11 | YAML 导出功能（单向） | 6h |
| G12 | 调试运行按钮与结果展示 | 6h |

#### Sprint 3.3：双向同步与完善（Week 11-12）

| 任务 | 描述 | 工时 |
|------|------|------|
| G13 | YAML 解析器（YAML → AST） | 6h |
| G14 | AST → 图形数据转换器 | 6h |
| G15 | 双向同步引擎（实时同步 < 500ms） | 8h |
| G16 | 快捷键系统 | 4h |
| G17 | 深色主题 + 响应式适配 | 4h |
| G18 | 集成测试 + Bug 修复 | 8h |

**GUI MVP 发布标准**：
- [ ] 支持完整的 CRUD 操作（创建/编辑/删除/运行）
- [ ] YAML ↔ GUI 双向同步正常工作
- [ ] 在 Chrome/Firefox/Safari 最新版测试通过

---

### 6.4 依赖关系与风险点

#### 关键路径（Critical Path）

```
环境管理 → 钩子机制 → 数据驱动 → 并发执行 → 性能测试 → RC 发布
   (W1)       (W1-2)      (W2)        (W3)        (W4)        (W5-6)
   
并行路径:
GUI 编辑器 (独立项目, W9-12)
```

#### 风险点与缓解措施

| 风险点 | 影响 | 概率 | 缓解措施 |
|--------|------|------|---------|
| **asyncio 改造复杂度超预期** | 并发功能延期 | 中 | 降级为先用 ThreadPoolExecutor（简单但有效） |
| **React Flow 学习曲线陡峭** | GUI 进度延迟 | 中 | 提前 PoC 验证技术可行性 |
| **向后兼容性破坏** | 社区反弹 | 低 | 全量回归测试 + 迁移指南 |
| **性能不达标** | 无法交付 | 低 | 早期建立性能基准，持续监控 |
| **人员变动** | 进度延误 | 低 | 代码规范完善 + 知识共享会议 |

---

**[第4-6章完成 ✓]** 继续撰写最后三章。


---

## 7. 测试策略

### 7.1 单元测试覆盖

#### 测试框架选型

| 工具 | 用途 | 版本要求 |
|------|------|---------|
| **pytest** | 测试运行器 | ≥ 7.0 |
| **pytest-asyncio** | 异步测试支持 | ≥ 0.21 |
| **pytest-cov** | 覆盖率统计 | ≥ 4.0 |
| **pytest-mock** | Mock 对象 | ≥ 3.10 |
| **responses** | HTTP 请求 Mock | ≥ 0.23 |
| **freezegun** | 时间控制 | ≥ 1.2 |

#### 覆盖率目标（按模块）

| 模块 | 目标覆盖率 | 重点测试场景 |
|------|-----------|-------------|
| `environment.py` | **≥ 95%** | 配置合并、优先级、校验、错误处理 |
| `hook_engine.py` | **≥ 90%** | 生命周期、条件执行、异常隔离 |
| `data_driver.py` | **≥ 90%** | CSV/JSON 解析、参数化、边界值 |
| `concurrent_runner.py` | **≥ 85%** | 并发控制、结果聚合、错误隔离 |
| `perf_collector.py` | **≥ 85%** | 指标计算、百分位、阈值检查 |
| `config.py` (修改后) | **≥ 80%** | 向后兼容性 |
| `test_runner.py` (修改后) | **≥ 80%** | 钩子集成、数据驱动集成 |

#### 单元测试示例结构

```python
# tests/unit/test_environment.py

import pytest
from environment import EnvironmentManager

class TestEnvironmentLoading:
    """环境加载测试"""
    
    def test_load_default_config(self):
        """应正确加载默认配置"""
        mgr = EnvironmentManager("tests/fixtures/env_valid.yaml")
        config = mgr.load_environment("dev")
        assert config["base_url"] == "http://localhost:8080"
        assert config["timeout"] == 10
    
    def test_merge_with_defaults(self):
        """环境配置应覆盖默认值"""
        mgr = EnvironmentManager("tests/fixtures/env_valid.yaml")
        config = mgr.load_environment("staging")
        # staging 覆盖了 timeout，但继承了 headers
        assert config["timeout"] == 30  # 来自 staging
        assert "Content-Type" in config["headers"]  # 继承自 defaults
    
    def test_env_file_loading(self):
        """应自动加载 .env 文件"""
        mgr = EnvironmentManager("tests/fixtures/env_with_dotenv.yaml")
        config = mgr.load_environment("staging")
        assert "STAGING_API_KEY" in config.get("env_variables", {})
    
    def test_cli_override_highest_priority(self):
        """命令行覆盖应有最高优先级"""
        mgr = EnvironmentManager("tests/fixtures/env_valid.yaml")
        config = mgr.load_environment("dev")  # timeout=10
        config = mgr.apply_overrides({"timeout": "999"})
        assert config["timeout"] == "999"
    
    def test_invalid_environment_raises_error(self):
        """无效环境名称应抛出明确异常"""
        mgr = EnvironmentManager("tests/fixtures/env_valid.yaml")
        with pytest.raises(ValueError, match="不存在"):
            mgr.load_environment("nonexistent")

class TestConfigValidation:
    """配置校验测试"""
    
    def test_missing_required_field(self):
        """缺少 base_url 应返回错误列表"""
        errors = validate_environment("tests/fixtures/env_missing_url.yaml")
        assert any("base_url" in e for e in errors)
    
    def test_invalid_url_format(self):
        """无效 URL 格式应被检测到"""
        errors = validate_environment("tests/fixtures/env_invalid_url.yaml")
        assert any("URL" in e for e in errors)
```

---

### 7.2 集成测试方案

#### 集成测试范围

| 测试类别 | 描述 | 示例数量 |
|---------|------|---------|
| **模块集成** | 多个模块协同工作 | ~20 个 |
| **CLI 集成** | 命令行端到端流程 | ~15 个 |
| **YAML 解析集成** | 真实 YAML 文件的完整解析 | ~25 个 |
| **报告生成集成** | 输入真实结果验证报告内容 | ~10 个 |

#### 关键集成场景

```yaml
# tests/integration/test_full_workflow.yaml

# 场景 1：环境切换 + 钩子 + 数据驱动 完整流程
- name: "完整功能集成测试"
  description: "验证 v2.0 所有新功能的协同工作"
  
  setup:
    - name: "初始化测试数据库"
      method: POST
      endpoint: "${BASE_URL}/test/init"
      
  steps:
    # 使用数据驱动的登录测试
    - data_source:
        file: "test_data/login_cases.csv"
      template:
        steps:
          - method: POST
            endpoint: "${BASE_URL}/auth/login"
            json:
              username: "${data.username}"
              password: "${data.password}"
            assertions:
              - type: status_code
                expected: "${data.expected_status}"
    
    # 验证钩子创建的数据存在
    - method: GET
      endpoint: "${BASE_URL}/test/verify"
      assertions:
        - type: equal
          path: "initialized"
          expected: true
  
  teardown:
    - name: "清理测试数据"
      method: DELETE
      endpoint: "${BASE_URL}/test/cleanup"

# 运行方式：
# python api_test_agent.py run tests/integration/test_full_workflow.yaml \
#   --env test --workers 5 --verbose
```

#### Mock 策略

```python
# tests/conftest.py - 全局 Mock 配置

import pytest
from unittest.mock import Mock, patch
import responses  # 用于 Mock HTTP 请求

@pytest.fixture
def mock_api_client():
    """Mock API Client，避免真实网络请求"""
    with responses.RequestsMock() as rsps:
        # 预设常见响应
        rsps.add(
            responses.GET,
            "http://localhost:8080/users/1",
            json={"id": 1, "name": "Test User"},
            status=200
        )
        yield rsps

@pytest.fixture
def sample_test_case():
    """提供标准测试用例数据"""
    return {
        "name": "Sample Test",
        "steps": [
            {
                "name": "Get User",
                "method": "GET",
                "endpoint": "/users/1",
                "assertions": [
                    {"type": "status_code", "expected": 200}
                ]
            }
        ]
    }
```

---

### 7.3 E2E 测试场景

#### E2E 测试矩阵（必须全部通过才能发布）

| ID | 场景描述 | 涉及功能 | 预期结果 | 优先级 |
|----|---------|---------|---------|--------|
| E2E-01 | v1.0 用例在 v2.0 中零修改运行 | 向后兼容 | ✅ 通过 | P0 |
| E2E-02 | `--env dev` 加载开发环境配置 | 环境管理 | ✅ 正确加载 | P0 |
| E2E-03 | `.env` 文件自动加载敏感信息 | 安全性 | ✅ 已脱敏显示 | P0 |
| E2E-04 | `--var key=value` 覆盖配置 | 动态覆盖 | ✅ 生效 | P0 |
| E2E-05 | global_setup → test → global_teardown | 钩子机制 | ✅ 按序执行 | P0 |
| E2E-06 | setup 失败时 teardown 仍执行 | 错误恢复 | ✅ 执行 | P0 |
| E2E-07 | CSV 数据源生成多个用例 | 数据驱动 | ✅ N 个用例 | P0 |
| E2E-08 | `-w 10` 并发执行 50 个用例 | 并发执行 | ✅ 加速 > 5x | P0 |
| E2E-09 | `perf` 模式采集性能指标 | 性能测试 | ✅ 指标完整 | P1 |
| E2E-10 | 性能超标时标记 FAIL | 阈值检查 | ✅ 标记失败 | P1 |
| E2E-11 | GUI 编辑器导出的 YAML 可被 CLI 运行 | GUI↔CLI | ✅ 兼容 | P1 |
| E2E-12 | 大规模：1000 个数据驱动用例并发 | 压力测试 | ✅ 无内存泄漏 | P2 |

#### E2E 自动化脚本示例

```bash
#!/bin/bash
# scripts/run_e2e_tests.sh - E2E 测试套件

set -e

echo "🚀 开始 E2E 测试..."

# 1. 向后兼容性测试
echo "▶️ [E2E-01] v1.0 兼容性测试..."
python api_test_agent.py run tests/v1_compatibility/ --reports json
[ $? -eq 0 ] && echo "✅ 通过" || { echo "❌ 失败"; exit 1; }

# 2. 环境管理测试
echo "▶️ [E2E-02~04] 环境管理..."
python api_test_agent.py run tests/env_management/ \
  --env test --show-config > /tmp/env_output.txt
grep -q "当前环境配置: test" /tmp/env_output.txt && echo "✅ 通过"

# 3. 钩子机制测试
echo "▶️ [E2E-05~06] 钩子机制..."
python api_test_agent.py run tests/hooks/ --reports json
# 验证 teardown 日志存在
grep -q "teardown executed" api_test.log && echo "✅ 通过"

# 4. 数据驱动测试
echo "▶️ [E2E-07] 数据驱动..."
python api_test_agent.py run tests/data_driven/ --reports json
# 验证生成了多个用例
python -c "import json; r=json.load(open('reports/*.json')); assert r['total_tests'] >= 5"
echo "✅ 通过"

# 5. 并发执行测试
echo "▶️ [E2E-08] 并发执行..."
START_TIME=$(date +%s)
python api_test_agent.py run tests/concurrent/ --workers 10 --reports json
END_TIME=$(date +%s)
ELAPSED=$(( END_TIME - START_TIME ))
echo "⏱️ 并发耗时: ${ELAPSED}s"
[ $ELAPSED -lt 30 ] && echo "✅ 通过（< 30s）" || echo "⚠️ 较慢"

# 6. 性能测试模式
echo "▶️ [E2E-09~10] 性能测试..."
python api_test_agent.py perf tests/performance/ \
  --rps 10 --duration 10s --reports html
echo "✅ 通过"

echo ""
echo "=========================================="
echo "🎉 所有 E2E 测试通过！"
echo "=========================================="
```

---

### 7.4 性能基准测试

#### 基准测试环境

| 项目 | 规格 |
|------|------|
| **操作系统** | Ubuntu 22.04 LTS (WSL2) |
| **CPU** | Intel i7-12700H (14 核) |
| **内存** | 16 GB DDR5 |
| **Python** | 3.11.3 |
| **网络** | Localhost (模拟 API Server) |

#### 基准指标（v2.0 目标）

| 场景 | v1.0 基线 | v2.0 目标 | 测试方法 |
|------|----------|----------|---------|
| **空用例执行** | 45ms | < 50ms (+10% 容忍) | timeit |
| **100 用例串行** | 4.5s | < 5.0s | 计时 |
| **100 用例 10 并发** | N/A | < 0.8s | 计时 |
| **1000 行 CSV 解析** | N/A | < 1s | timeit |
| **HTML 报告(500 用例)** | 4.0s | < 4.5s | 计时 |
| **内存占用(500 用例)** | 25MB | < 35MB | memory_profiler |
| **启动时间(CLI)** | 0.8s | < 1.0s | time |

#### 回归防护

每次 PR 必须通过性能基线测试：

```yaml
# .github/workflows/performance.yml
name: Performance Regression

on: [pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run benchmarks
        run: |
          pip install -e ".[dev]"
          python scripts/benchmark.py > benchmark_results.json
      
      - name: Check regression
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          github-token: ${{ secrets.GITHUB_TOKEN }}
          comment-always: true
          alert-threshold: '150%'  # 超过基线 150% 则告警
```

---

## 8. 风险评估与应对

### 8.1 技术风险

| 风险ID | 风险描述 | 概率 | 影响 | 风险等级 | 应对措施 |
|--------|---------|------|------|---------|---------|
| **R-Tech-01** | asyncio 改造导致现有同步代码大规模重构 | 中 | 高 | 🔴 **高** | **降级方案**：Phase 1 先用 `concurrent.futures.ThreadPoolExecutor`（改动小），Phase 2 再迁移到 asyncio |
| **R-Tech-02** | React Flow 不满足复杂编排需求（如条件分支、循环） | 中 | 中 | 🟡 **中** | **提前 PoC**：Week 8 前完成技术验证，不行则换方案（如 JointJS/DAG.js） |
| **R-Tech-03** | YAML 双向同步引擎的 AST 转换精度问题 | 低 | 高 | 🟡 **中** | **保守策略**：Phase 1 仅单向（GUI→YAML），双向同步作为 Phase 2 目标 |
| **R-Tech-04** | 性能测试模式的 RPS 控制精度不足（±20% 波动） | 中 | 低 | 🟢 **低** | **文档说明**：在文档中明确精度范围，使用统计方法平滑波动 |
| **R-Tech-05** | Windows 下 asyncio 性能不如 Linux | 低 | 中 | 🟢 **低** | **平台适配**：Windows 下自动降级为多线程模式 |

### 8.2 进度风险

| 风险ID | 风险描述 | 概率 | 影响 | 应对措施 |
|--------|---------|------|------|---------|
| **R-Sched-01** | GUI 开发工作量低估（前端工程复杂度高） | 高 | 高 | **分阶段交付**：MVP 仅包含核心功能（HTTP + 基础断言），高级特性延后 |
| **R-Sched-02** | 核心开发者请假/离职导致关键路径阻塞 | 中 | 高 | **知识共享**：每周代码审查会 + 详细的技术文档 + Pair Programming |
| **R-Sched-03** | 需求变更（用户反馈导致功能范围扩大） | 中 | 中 | **变更控制**：v2.0 锁定需求，新需求纳入 v2.1/v2.2 规划 |
| **R-Sched-04** | 第三方库 breaking change（如 PyYAML 7.0 不兼容） | 低 | 中 | **版本锁定**：依赖版本固定在 requirements.txt，升级需完整回归测试 |

### 8.3 资源风险

| 风险ID | 风险描述 | 概率 | 影响 | 应对措施 |
|--------|---------|------|------|---------|
| **R-Res-01** | 缺乏前端开发经验（团队主要是 Python 后端） | 中 | 高 | **培训/外包**：前期安排 React 培训或临时引入前端顾问 |
| **R-Res-02** | 测试资源不足（QA 需同时支持 v1.0 维护和 v2.0 测试） | 中 | 中 | **自动化优先**：投入时间建设自动化测试体系，减少手工测试比例 |
| **R-Res-03** | CI 资源有限（GitHub Actions 免费额度耗尽） | 低 | 低 | **优化策略**：仅在 main 分支和 PR 运行完整测试，feature 分支仅跑单元测试 |

### 8.4 应对措施总结

#### 风险监控机制

```python
# scripts/risk_dashboard.py - 风险仪表盘（每周更新）

RISK_MATRIX = {
    "high_risks": ["R-Tech-01"],  # 需要特别关注
    "mitigation_status": {
        "R-Tech-01": "✅ 降级方案已确定 (ThreadPoolExecutor)",
        "R-Sched-01": "⏰ MVP 范围已缩减",
    },
    "next_review_date": "2026-05-08"
}
```

#### 应急预案

**预案 A：如果 Week 4 核心功能未完成**
- 延长 Beta 发布 1 周
- 砍掉 GUI 编辑器（移至 v2.1）
- 确保 CLI 功能 100% 完成

**预案 B：如果并发性能不达标**
- 降低默认 workers 数量（从 10 降至 5）
- 在文档中明确标注已知限制
- 列入 v2.0.1 修复计划

**预案 C：如果向后兼容性出现重大问题**
- 提供 `--legacy-mode` 参数（完全禁用新功能）
- 发布迁移工具（自动转换旧格式）
- 延长 v1.0 维护期 3 个月

---

## 9. 附录

### A. YAML 配置示例全集

#### A.1 完整的环境配置文件

```yaml
# configs/environments.yaml - 生产级示例
defaults:
  timeout: 30
  retry_times: 3
  retry_delay: 1
  headers:
    Content-Type: "application/json"
    Accept: "application/json"
    X-Requested-With: "API-Test-Agent"
    X-Version: "2.0"
  log_level: "INFO"

environments:
  development:
    base_url: "http://localhost:8000/api/v1"
    timeout: 10
    retry_times: 1
    variables:
      debug: true
      db_name: "dev_db"
      skip_ssl_verify: true

  staging:
    base_url: "https://staging-api.company.com/api/v1"
    timeout: 30
    variables:
      debug: false
      db_name: "staging_db"
    env_file: ".env.staging"

  production:
    base_url: "https://api.company.com/api/v1"
    timeout: 60
    retry_times: 5
    variables:
      debug: false
      db_name: "prod_readonly"
    env_file: ".env.prod"
    # 生产环境额外配置
    rate_limit:
      rps: 100  # 自限流，避免压垮生产环境

groups:
  smoke: [development]
  regression: [staging, production]
  all: [development, staging, production]
```

#### A.2 完整的企业级测试用例示例

```yaml
# tests/e2e/order_lifecycle.yaml
name: "订单全生命周期 E2E 测试"

global_setup:
  - name: "启动测试基础设施"
    command: "docker-compose -f docker/test-compose.yml up -d"
    
  - name: "等待服务就绪"
    script: "scripts/wait_for_services.py"
    extract:
      BASE_URL: "base_url"

  - name: "初始化测试数据"
    method: POST
    endpoint: "${BASE_URL}/test/seed"
    assertions:
      - type: status_code
        expected: 200

test_cases:

  - name: "正常下单流程"
    setup:
      - name: "创建买家账号"
        method: POST
        endpoint: "${BASE_URL}/users"
        json:
          username: "buyer_e2e_${timestamp}"
          role: "buyer"
        extract:
          buyer_id: "id"
          
      - name: "给买家充值"
        method: POST
        endpoint: "${BASE_URL}/users/${buyer_id}/balance"
        json:
          amount: 10000.00
          reason: "E2E 测试充值"

    steps:
      - name: "浏览商品"
        method: GET
        endpoint: "${BASE_URL}/products"
        params:
          category: "electronics"
          page: 1
          size: 10
        assertions:
          - type: status_code
            expected: 200
          - type: type_check
            path: "$"
            expected_type: list
            
      - name: "添加商品到购物车"
        method: POST
        endpoint: "${BASE_URL}/cart/items"
        json:
          user_id: "${buyer_id}"
          product_id: "PROD_001"
          quantity: 2
        extract:
          cart_id: "id"
        assertions:
          - type: status_code
            expected: 201
            
      - name: "提交订单"
        method: POST
        endpoint: "${BASE_URL}/orders"
        json:
          cart_id: "${cart_id}"
          shipping_address:
            street: "测试街道 123 号"
            city: "北京市"
            zip: "100000"
        extract:
          order_id: "id"
          order_number: "order_no"
        assertions:
          - type: status_code
            expected: 201
          - type: contains_key
            key: "order_no"
            
      - name: "支付订单"
        method: POST
        endpoint: "${BASE_URL}/orders/${order_id}/pay"
        json:
          payment_method: "test_mock"
          amount: 0  # E2E 测试免费
        assertions:
          - type: status_code
            expected: 200
          - type: equal
            path: "status"
            expected: "paid"
            
      - name: "查询订单状态"
        method: GET
        endpoint: "${BASE_URL}/orders/${order_id}"
        assertions:
          - type: status_code
            expected: 200
          - type: contains_key
            key: "items"
          - type: equal
            path: "status"
            expected: "paid"

    teardown:
      - name: "取消订单（如果创建成功）"
        condition: "${order_id} is not none"
        method: POST
        endpoint: "${BASE_URL}/orders/${order_id}/cancel"
        
      - name: "删除测试用户"
        condition: "${buyer_id} is not none"
        method: DELETE
        endpoint: "${BASE_URL}/users/${buyer_id}"

global_teardown:
  - name: "收集日志"
    command: "docker-compose -f docker/test-compose.py logs > logs/e2e_${timestamp}.log"
    
  - name: "清理测试环境"
    command: "docker-compose -f docker/test-compose.py down -v"
```

---

### B. API 接口清单

#### B.1 新增的 Python API

```python
# environment.py
class EnvironmentManager:
    def __init__(self, config_path: str = "configs/environments.yaml")
    def load_environment(self, env_name: str) -> dict
    def apply_overrides(self, overrides: Dict[str, str]) -> dict
    def list_environments(self) -> List[str]
    def validate_environment(self, env_name: str) -> List[str]

# hook_engine.py
class HookEngine:
    @staticmethod
    def execute_hooks(hooks: List[HookConfig], context: Dict) -> List[HookResult]
    @staticmethod
    def evaluate_condition(condition: str, context: Dict) -> bool

# data_driver.py
class DataDriver:
    @staticmethod
    def load_data_source(config: DataSourceConfig) -> List[Dict]
    @staticmethod
    def expand_template(template: Dict, data_rows: List[Dict]) -> List[TestCase]

# concurrent_runner.py
class ConcurrentTestRunner:
    def __init__(self, base_runner: TestRunner, max_workers: int = 10)
    async def execute_all(self, test_cases: List[Dict]) -> ConcurrencyResult
    async def execute_single(self, test_case: Dict) -> TestCaseResult

# perf_collector.py
class PerformanceCollector:
    def __init__(self)
    async def record_request(response_time_ms: float, success: bool)
    def calculate_metrics(self) -> PerformanceMetrics
    def reset(self)

# perf_report_generator.py
class PerfReportGenerator:
    def __init__(self, output_dir: str = "reports")
    def generate_perf_report(self, result: ConcurrencyResult, metrics: PerformanceMetrics) -> str
```

#### B.2 新增的 CLI 命令

```bash
# 环境管理
python api_test_agent.py env list                    # 列出所有环境
python api_test_agent.py env validate --env staging  # 校验环境配置
python api_test_agent.py env show --env prod         # 显示环境详情

# 性能测试
python api_test_agent.py perf test.yaml               # 运行性能测试
python api_test_agent.py perf test.yaml --rps 100     # 指定 RPS
python api_test_agent.py perf test.yaml --duration 300s  # 指定持续时间

# GUI 服务（新增）
python api_test_agent gui serve                      # 启动 GUI 编辑器服务
python api_test_agent gui serve --port 8080           # 指定端口
```

---

### C. 参考资料与竞品分析

#### C.1 推荐阅读

| 资料 | 类型 | 链接/说明 |
|------|------|---------|
| **YAML 1.2 规范** | 标准 | yaml.org/spec |
| **OpenAPI 3.0 规范** | 标准 | swagger.io/specification |
| **pytest 最佳实践** | 指南 | docs.pytest.org |
| **asyncio 官方文档** | 文档 | docs.python.org/3/library/asyncio |
| **React Flow 文档** | 文档 | reactflow.dev/docs |

#### C.2 竞品功能对比（详细版）

| 功能维度 | Postman | JMeter | REST Assured | **API Test Agent v2.0** |
|---------|---------|--------|--------------|------------------------|
| **易用性** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **学习成本** | 2-3 天 | 1-2 周 | 3-5 天 | **< 1 小时** |
| **声明式配置** | ❌ (GUI only) | ❌ (GUI only) | ❌ (代码) | ✅ **YAML** |
| **多环境支持** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **数据驱动** | ⭐⭐⭐ (CSV) | ⭐⭐⭐⭐ (CSV/DB) | ⭐⭐⭐ (代码) | ⭐⭐⭐⭐⭐ (CSV/JSON/Excel) |
| **前后置钩子** | ⭐⭐⭐ (Pre-request Script) | ⭐⭐⭐ (Setup Thread) | ⭐⭐⭐ (Before/After) | ⭐⭐⭐⭐⭐ (3 级钩子) |
| **并发执行** | ⭐⭐⭐ (Collection Runner) | ⭐⭐⭐⭐⭐ (Thread Group) | ⭐⭐ (并行流) | ⭐⭐⭐⭐ (asyncio) |
| **性能测试** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ (内置) |
| **CI/CD 集成** | ⭐⭐⭐ (Newman) | ⭐⭐⭐ (CLI) | ⭐⭐⭐⭐⭐ (Jenkins) | ⭐⭐⭐⭐⭐ (原生) |
| **GUI 编辑器** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ (v2.1) |
| **报告质量** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **开源免费** | 部分 (Pro $29/月) | ✅ | ✅ | ✅ **完全免费** |
| **社区活跃度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 🔄 **增长中** |

#### C.3 设计灵感来源

本项目的部分设计参考了以下优秀项目：

- **pytest** 的 fixture 机制（启发了钩子设计）
- **JMeter** 的 Thread Group 和 Ramp-up（启发了性能测试设计）
- **Postman Collection Runner**（启发了数据驱动语法）
- **Cypress** 的可视化测试界面（启发了 GUI 编辑器设计）
- **Terraform** 的环境配置管理（启发了 environments.yaml 结构）

---

### D. 术语表（快速索引）

| 术语 | 英文 | 定义位置 |
|------|------|---------|
| API Response | API 响应 | 2.1.3 |
| Assertion | 断言 | 1.4, 3.2 |
| Concurrency | 并发 | 1.4, 3.4 |
| Data Driver | 数据驱动 | 1.4, 3.3 |
| Environment | 环境 | 1.4, 3.1 |
| GUI Editor | 图形编辑器 | 3.5 |
| Hook | 钩子 | 1.4, 3.2 |
| Path Expression | 路径表达式 | 1.4, 2.2 |
| Performance Test | 性能测试 | 3.4 |
| Plugin | 插件 | 4.5 |
| RPS | 每秒请求数 | 3.4 |
| Setup/Teardown | 前后置操作 | 3.2 |
| Test Case | 测试用例 | 1.4, 2.1 |
| Test Suite | 测试套件 | 1.4, 2.1 |
| Test Step | 测试步骤 | 1.4, 2.1 |
| Variable Extraction | 变量提取 | 2.2 |

---

## 📄 文档结束

> **文档状态**: ✅ 初稿完成
> **总页数**: ~9 章 45 节，约 **3500+ 行**
> **最后更新**: 2026-05-01
> **下一步**: 进入评审阶段，收集反馈后迭代优化

---

**致谢**

感谢所有为这个项目贡献代码、文档、想法的社区成员！特别感谢早期用户的宝贵反馈，让 v2.0 的方向更加清晰。

让我们一起打造**最好用的 API 测试框架**！🚀


---

**文档结束**
