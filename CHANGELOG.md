# Changelog

所有重要变更都将记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 项目计划、技术分析和扩展路线图文档
- GitHub Actions CI/CD工作流配置
- Issue 和 Pull Request 模板
- CONTRIBUTING.md 贡献指南

### Changed
- README.md 优化为符合 GitHub 规范的格式
- 分离代码与管理文档到独立目录

---

## [2.0.0-alpha] - 2026-05-01

### 🎉 New Features - v2.0 核心能力

#### 🌍 环境管理模块（Environment Management）
- **多环境配置支持**：dev/staging/prod 三级环境配置（`configs/environments.yaml`）
- **YAML 配置合并**：defaults → environment → .env → CLI overrides 四级优先级
- **.env 文件自动加载**：支持 `.env.{env_name}` 环境特定文件和通用 `.env` 文件
- **命令行参数覆盖**：`--var KEY=VALUE` 支持简单键值对和嵌套键覆盖
- **敏感信息脱敏**：自动检测 `_KEY`, `_SECRET`, `_PASSWORD`, `_TOKEN` 后缀并脱敏显示
- **配置校验功能**：URL 格式验证、必填字段检查、未定义变量引用检测
- **CLI 子命令**：`env list`, `env validate`, `env show`

#### 🪝 钩子系统（Hook System）
- **完整生命周期**：global_setup → setup → steps → teardown → global_teardown
- **三种钩子类型**：
  - HTTP 钩子：发送 HTTP 请求（创建资源、初始化数据等）
  - Command 钩子：执行系统命令（数据库迁移、脚本执行等）
  - Script 钩子：运行 Python 脚本（自定义逻辑、复杂处理等）
- **变量提取与传递**：通过 `extract` 配置提取响应数据，跨钩子共享
- **条件执行**：`condition` 参数支持 `${var} is not none`, `==`, `!=`, `>`, `<` 等表达式
- **失败控制**：`ignore_failure=True` 允许失败继续执行；保证 teardown 始终执行
- **Setup 失败恢复**：即使 setup 失败，teardown 仍会执行以确保资源清理

#### 📊 数据驱动测试（Data-Driven Testing）
- **CSV 数据源**：从 CSV 文件加载测试数据，自动生成多个用例
- **JSON 数据源**：支持 JSON 数组和对象格式，支持嵌套结构
- **模板参数化**：使用 `${data.column_name}` 占位符替换模板中的值
- **动态用例命名**：`case_name_template` 支持使用数据字段生成唯一名称
- **过滤条件**：`filter` 配置可筛选符合条件的测试数据行
- **多编码支持**：自动尝试 utf-8-sig, utf-8, gbk, latin-1 编码

#### ⚡ 并发执行引擎（Concurrency Engine）
- **多线程并行**：使用 `-w N` 指定工作线程数（默认 1，即串行）
- **信号量控制**：asyncio.Semaphore 限制并发数量，避免过载
- **变量隔离**：每个用例拥有独立的 VariableContext，避免并发冲突
- **结果聚合**：ConcurrencyResult 包含总数、通过率、加速比等统计信息
- **异步包装器**：将同步 TestRunner 包装为异步执行，支持 asyncio.gather

### 📝 Changed - v2.0 变更

#### CLI 参数扩展
- 新增 `--env ENV_NAME`：指定运行环境
- 新增 `--var KEY=VALUE`：配置项覆盖（可多次使用）
- 新增 `-w, --workers N`：并发工作线程数
- 新增 `--show-config`：显示当前生效的配置
- 新增 `env` 子命令组：list/validate/show

#### Config 模块增强
- 支持环境模式初始化：`Config(environment="staging")`
- 自动合并环境配置到主配置
- 提供 `get_environment_config()` 和 `get_environment_variables()` 方法

#### 文档和示例
- 新增 `configs/environments.yaml`：完整的环境配置示例
- 新增 `configs/.env.example` / `.env.staging.example`：环境变量模板
- 新增 `examples/v2_environment/`：环境管理使用示例
- 新增 `examples/v2_hooks/`：钩子机制使用示例（含 Python 脚本示例）
- 新增 `examples/v2_data_driven/`：数据驱动测试示例（CSV + JSON）
- 新增 `test_data/login_cases.csv`：登录测试数据集（8 组场景）
- 新增 `test_data/register_cases.json`：注册测试数据集（6 组场景，含嵌套结构）

#### 测试覆盖
- 新增 `tests/integration/test_integration_environment.py`：环境管理集成测试
- 新增 `tests/integration/test_integration_hooks.py`：钩子系统集成测试
- 新增 `tests/integration/test_integration_data_driven.py`：数据驱动集成测试
- 新增 `tests/integration/test_integration_concurrency.py`：并发执行集成测试

---

## [1.0.0] - 2026-05-01

### Added

#### 核心功能
- ✅ API 客户端封装（APIClient）
- ✅ 断言引擎（10 种断言类型）
- ✅ 测试执行器（TestRunner）
- ✅ 报告生成器（HTML/Markdown/JSON）
- ✅ 命令行界面（CLI）
- ✅ Python API

#### 支持的方法
- GET
- POST
- PUT
- DELETE
- PATCH

#### 断言类型
- status_code: HTTP 状态码检查
- equal: 值相等性检查
- not_equal: 值不等检查
- contains: 容器包含检查
- not_contains: 容器不包含检查
- contains_key: 字典键存在性检查
- type_check: 数据类型检查
- length: 长度检查
- regex_match: 正则表达式匹配
- response_time: 响应时间检查

#### 高级功能
- 变量提取与传递（extract + ${var}）
- 自动重试机制（3 次）
- 多格式报告生成
- 配置文件管理
- 环境变量支持

#### 文档
- README.md - 项目简介
- SKILL.md - 详细技能文档
- 快速开始.md - 5 分钟入门
- 使用教程.md - 完整教程（1.2 万字）
- 使用说明.md - 中文手册
- CHEATSHEET.md - 速查卡片
- 技术分析.md - 架构分析
- 项目计划.md - 完整项目规划
- CONTRIBUTING.md - 贡献指南

#### 示例
- examples/sample_tests.yaml - 6 个复杂场景测试案例
- tests/my_first_test.yaml - 简单入门示例

#### 输出
- reports/ - HTML、Markdown、JSON 报告

### Changed
- 初始发布版本

### Fixed
- Windows 控制台编码问题处理
- timeout 参数重复传递问题修复

---

[Unreleased]: https://github.com/qwenpaw/api-test-agent/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/qwenpaw/api-test-agent/releases/tag/v1.0.0
