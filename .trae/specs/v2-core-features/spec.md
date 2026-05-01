# API Test Agent v2.0 - 核心功能实现 Spec

## Why

当前 API Test Agent v1.0 存在以下关键限制，严重影响企业级使用：
1. **单环境配置瓶颈**：无法快速切换 dev/staging/prod 环境，每次需手动修改多个 YAML 文件
2. **无测试隔离机制**：缺少前后置钩子（setup/teardown），测试用例间存在数据依赖和污染
3. **参数化测试缺失**：无法通过外部数据源（CSV/JSON）批量生成测试用例，导致大量重复代码
4. **串行执行性能差**：500+ 用例执行耗时 30+ 分钟，无法利用 I/O 并行加速

本次升级将实现 **Phase 1 核心基础**（环境管理、钩子机制、数据驱动、并发执行），为后续 GUI 编辑器和性能测试奠定基础。

## What Changes

### 新增模块
- **environment.py**: 多环境配置管理器（支持 YAML 配置、.env 文件加载、三级优先级合并）
- **hook_engine.py**: 前后置钩子执行引擎（全局/用例/步骤三级钩子，支持 HTTP/Command/Script 类型）
- **data_driver.py**: 数据驱动测试引擎（CSV/JSON 数据源解析、模板参数化、用例批量生成）
- **concurrent_runner.py**: 并发执行器（asyncio 协程模型、Worker 数量控制、结果聚合）

### 修改现有模块
- **config.py**: 集成 EnvironmentManager，支持动态环境切换
- **api_test_agent.py**: 扩展 CLI 参数（--env, --var, -w/--workers）
- **test_runner.py**: 集成钩子生命周期和数据驱动逻辑

### 新增配置文件
- **configs/environments.yaml**: 多环境定义文件（dev/staging/prod）
- **.env.example / .env.staging.example**: 敏感信息模板

### 新增示例和文档
- **examples/v2_environment/**: 环境管理完整示例
- **examples/v2_hooks/**: 钩子机制完整示例
- **examples/v2_data_driven/**: 数据驱动测试示例
- 更新 README.md 和 CHANGELOG.md

### BREAKING Changes
- 无（完全向后兼容 v1.0）

## Impact

- Affected specs: 无前置 spec（首次实现）
- Affected code:
  - 核心新增: environment.py, hook_engine.py, data_driver.py, concurrent_runner.py (~1200 行新代码)
  - 需修改: config.py, api_test_agent.py, test_runner.py (~200 行改动)
  - 测试新增: tests/unit/, tests/integration/ (~1500 行测试代码)

## ADDED Requirements

### Requirement: 环境管理与配置切换 (ENV-MGMT)

系统 SHALL 提供多环境配置管理能力，支持通过命令行一键切换测试环境。

#### 基本能力
- **WHEN** 用户执行 `python api_test_agent.py run tests/ --env staging`
- **THEN** 系统自动加载 `configs/environments.yaml` 中 staging 环境的 base_url、timeout、variables 等配置
- **AND** 合并顺序为：defaults → 环境特定配置 → .env 文件 → 命令行 --var 覆盖（优先级递增）

#### 场景 1: 加载有效环境
- **GIVEN** environments.yaml 中定义了 dev/staging/prod 三个环境
- **WHEN** 执行 `--env staging`
- **THEN** 正确应用 staging 的 base_url、timeout=30、variables 等配置
- **AND** 如果存在 .env.staging 文件则自动加载其中的敏感信息

#### 场景 2: 命令行覆盖最高优先级
- **GIVEN** staging 环境配置 timeout=30
- **WHEN** 执行 `--env staging --timeout 60`
- **THEN** 最终 timeout 值为 60（命令行覆盖环境配置）

#### 场景 3: 敏感信息脱敏
- **GIVEN** .env 文件中包含 STAGING_API_KEY=sk_live_xxx
- **WHEN** 使用 --show-config 查看配置或输出日志时
- **THEN** 显示为 STAGING_API_KEY=sk_live_************（已脱敏）

#### 场景 4: 向后兼容
- **WHEN** 不带 --env 参数执行命令
- **THEN** 行为与 v1.0 完全一致（使用 config.json 或默认值）

---

### Requirement: 前后置钩子机制 (HOOK-SYSTEM)

系统 SHALL 提供灵活的钩子机制，支持在测试生命周期的关键节点执行自定义操作。

#### 钩子类型
- **全局钩子**: global_setup / global_teardown（整个测试套件执行一次）
- **用例钩子**: setup / teardown（每个测试用例执行前后）
- **步骤钩子**: before_step / after_step（每个步骤执行前后，可选实现）

#### 支持的操作类型
- HTTP 请求：method, endpoint, headers, json 等
- Shell 命令：command 字段
- Python 脚本：script 字段

#### 场景 1: 正常执行流程
- **GIVEN** 测试用例定义了 setup（创建用户）、steps（调用 API）、teardown（删除用户）
- **WHEN** 执行该测试用例
- **THEN** 按 setup → steps → teardown 顺序执行
- **AND** setup 中提取的变量可在 steps 和 teardown 中使用

#### 场景 2: Setup 失败时 Teardown 仍执行
- **GIVEN** setup 中某步失败（如创建用户返回 500）
- **WHEN** 执行测试用例
- **THEN** 跳过后续 setup 步骤和 steps
- **BUT** 仍然执行 teardown（保证资源清理）
- **AND** 用例状态标记为 ERROR（非 FAIL）

#### 场景 3: 条件执行
- **GIVEN** teardown 定义了 condition: "${order_id} is not none"
- **WHEN** order_id 变量为 None 时
- **THEN** 跳过该 teardown 步骤

---

### Requirement: 数据驱动测试 (DATA-DRIVEN)

系统 SHALL 支持从外部数据源（CSV/JSON）加载数据，通过模板批量生成独立测试用例。

#### 数据源格式
- CSV: 第一行为表头作为变量名，每行数据生成一个用例
- JSON: 数组格式，每个元素为一组测试数据

#### 参数化语法
- 使用 `${data.column_name}` 引用数据源中的值
- 支持 `${data.expected_code}` 在断言中动态设置期望值

#### 场景 1: CSV 数据源生成多用例
- **GIVEN** login_cases.csv 包含 5 行测试数据（username, password, expected_status）
- **WHEN** 测试用例定义了 data_source.type=csv 且 template.steps
- **THEN** 自动生成 5 个独立的测试用例
- **AND** 每个用例的名称可通过 case_name_template 自定义

#### 场景 2: 动态断言
- **GIVEN** 某行数据的 expected_status=401
- **WHEN** 执行该用例
- **THEN** 断言 status_code == 401（来自数据源而非硬编码）

#### 场景 3: 数据验证
- **GIVEN** CSV 文件路径不存在或格式错误
- **WHEN** 加载数据源时
- **THEN** 输出清晰的错误信息（包含文件路径和具体问题）
- **AND** 不崩溃，返回空用例列表

---

### Requirement: 并发执行 (CONCURRENCY)

系统 SHALL 支持并发执行测试用例，显著缩短大规模测试套件的运行时间。

#### 并发模型
- 基于 asyncio.Semaphore 控制最大并发数
- 使用 ThreadPoolExecutor 包装现有同步 TestRunner（兼容性考虑）
- 每个 Worker 维护独立的变量上下文（避免污染）

#### CLI 接口
- `-w N` 或 `--workers N`: 指定 Worker 数量
- `-w auto`: 自动检测 CPU 核心数

#### 场景 1: 并发加速效果
- **GIVEN** 100 个独立测试用例（无相互依赖）
- **WHEN** 使用 `-workers 10` 执行
- **THEN** 总耗时 ≈ 串行时间的 1/10（±20% 容忍度）
- **AND** 所有用例结果正确聚合到统一报告

#### 场景 2: 错误隔离
- **GIVEN** 用例 A 执行失败（如断言不通过）
- **WHEN** 与其他用例并发执行时
- **THEN** 用例 A 的失败不影响其他用例的执行和结果判定

#### 场景 3: 变量作用域隔离
- **GIVEN** 用例 A 提取了变量 token=abc
- **WHEN** 用例 B 并发执行时
- **THEN** 用例 B 无法访问 token=abc（作用域独立）

---

## MODIFIED Requirements

### Requirement: 配置管理增强 (CONFIG-ENHANCE)

现有 config.py SHALL 扩展以支持环境管理集成。

#### 修改点
- Config.__init__() 增加 environment 参数
- 加载逻辑改为：base_config → env_config → merged_config
- 保持向后兼容：无 environment 参数时行为不变

---

### Requirement: CLI 参数扩展 (CLI-EXTEND)

现有 api_test_agent.py SHALL 增加新的命令行参数。

#### 新增参数
- `--env` / `-e`: 环境名称（可选）
- `--var key=value`: 动态变量覆盖（可多次使用）
- `-w` / `--workers`: 并发 Worker 数量（默认 1 即串行）
- `--show-config`: 显示当前生效的配置详情

#### 向后兼容
- 所有新参数均为可选，不影响现有用法

---

## REMOVED Requirements

无（纯增量开发，不删除任何现有功能）
