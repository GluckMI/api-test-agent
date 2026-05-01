# Tasks - API Test Agent v2.0 核心功能实现

## 模块 1: 环境管理器 (environment.py)

- [x] **Task 1.1**: 创建 environment.py 模块骨架
  - 定义 EnvironmentManager 类结构
  - 定义 EnvironmentConfig 数据类（name, base_url, timeout, headers, variables, env_variables）
  - 实现 __init__ 和 _load_config() 方法（YAML 文件加载）
  - 添加完整的 docstring 和类型注解
  - 处理文件不存在异常，给出友好错误提示
  - **验证**: 能成功实例化，加载有效 YAML 文件，处理缺失文件异常

- [x] **Task 1.2**: 实现环境列表与加载逻辑
  - 实现 list_environments() 方法（返回可用环境名称列表）
  - 实现 load_environment(env_name) 核心方法
  - 实现三级配置合并：defaults → environments.{env_name} → 最终结果
  - 处理环境不存在的 ValueError 异常（提示可用环境列表）
  - 处理空值/缺失字段的优雅降级
  - **验证**: 正确加载 dev/staging/prod 环境，defaults 被继承，环境特定字段覆盖 defaults

- [x] **Task 1.3**: 实现 .env 文件加载器
  - 实现 _load_env_file(env_file_path) 方法
  - 解析 .env 格式（KEY=VALUE，支持注释行 #）
  - 自动检测 .env.{env_name} 文件并加载
  - 将环境变量存入 config['env_variables'] 字典
  - 处理 .env 文件不存在的情况（警告但不阻塞）
  - **验证**: .env.staging 文件的变量被正确加载到 env_variables 中

- [x] **Task 1.4**: 实现命令行覆盖机制
  - 实现 apply_overrides(overrides: Dict[str, str]) 方法
  - 支持简单键值对覆盖（如 timeout=60）
  - 支持嵌套键覆盖（如 headers.Authorization=Bearer xxx）
  - 使用 deep_merge 确保字典类型的正确合并
  - 命令行覆盖具有最高优先级
  - **验证**: --var key=value 和 --timeout 60 参数正确生效

- [x] **Task 1.5**: 实现配置校验功能
  - 实现 validate_environment(env_name) -> List[str] 方法
  - 校验必填字段（base_url）
  - 校验 URL 格式有效性
  - 校验 .env 文件存在性
  - 校验变量引用完整性（无未定义的 ${var}）
  - 返回错误消息列表（空列表表示通过）
  - **验证**: 缺少 base_url 时返回明确错误，无效 URL 被检测到

- [x] **Task 1.6**: 实现敏感信息脱敏显示
  - 实现 _sanitize_value(key, value) 方法
  - 检测后缀模式：_KEY, _SECRET, _PASSWORD, _TOKEN, _CREDENTIAL
  - 替换为固定长度的 * 号（保留前缀便于识别）
  - 在 show_config 输出和日志中自动应用脱敏
  - **验证**: STAGING_API_KEY 显示为 sk_live_************，正常变量不受影响

- [x] **Task 1.7**: 编写环境管理器单元测试 (tests/unit/test_environment.py)
  - 测试正常加载场景（3 个环境）
  - 测试配置合并顺序（优先级正确性）
  - 测试 .env 文件加载
  - 测试命令行覆盖最高优先级
  - 测试校验逻辑（缺失字段、无效URL、未定义变量）
  - 测试敏感信息脱敏
  - 测试边界情况（空 YAML、空环境、特殊字符）
  - **目标覆盖率**: ≥ 95%
  - **验证**: pytest tests/unit/test_environment.py 全部通过

---

## 模块 2: 钩子引擎 (hook_engine.py)

- [x] **Task 2.1**: 创建 hook_engine.py 数据结构与接口定义
  - 定义 HookConfig 数据类（name, hook_type, method, endpoint, command, script, condition, extract, ignore_failure）
  - 定义 HookResult 数据类（success, error_message, duration, extracted_vars）
  - 定义 HookType 枚举（HTTP, COMMAND, SCRIPT）
  - 定义抽象执行器基类 BaseHookExecutor
  - **验证**: 数据类可正确实例化，类型注解完整

- [x] **Task 2.2**: 实现 HTTP 类型钩子执行器
  - 创建 HttpHookExecutor 类（继承 BaseHookExecutor）
  - 复用现有 APIClient 发送请求
  - 支持 method, endpoint, headers, params, json_data 等参数
  - 执行成功时提取变量（通过 extract 配置）
  - 执行失败时返回错误信息（含 status_code 和 response body）
  - **验证**: POST /setup/init 能正确执行并提取 user_id 变量

- [x] **Task 2.3**: 实现 Command 类型钩子执行器
  - 创建 CommandHookExecutor 类
  - 使用 subprocess.run() 执行 Shell 命令
  - 设置超时控制（继承全局 timeout 或自定义）
  - 捕获 stdout/stderr 用于调试
  - 返回码非 0 时视为失败
  - **验证**: python scripts/init_db.py 能被正确调用，超时生效

- [x] **Task 2.4**: 实现 Script 类型钩子执行器
  - 创建 ScriptHookExecutor 类
  - 动态导入并执行 Python 脚本模块
  - 传递上下文变量（context dict）给脚本
  - 捕获脚本中的异常并转换为友好错误信息
  - 支持脚本返回值作为提取变量
  - **验证**: hooks/setup_user.py 能被执行并返回测试用户 ID

- [x] **Task 2.5**: 实现钩子调度核心逻辑
  - 实现 HookEngine.execute_hooks(hooks, context) -> List[HookResult]
  - 根据 hook_type 分发到对应 Executor
  - 顺序执行钩子列表（除非某步失败且 ignore_failure=False）
  - 收集所有执行结果和提取的变量
  - 实现 evaluate_condition(condition_str, context) -> bool 方法
  - 支持简单表达式："${var} is not none", "${var} == 'value'"
  - **验证**: 多个 hook 按序执行，条件判断正确，变量在后续 hook 中可用

- [x] **Task 2.6**: 实现生命周期集成（setup/steps/teardown 流程）
  - 实现 execute_test_case_with_hooks(test_case) 方法
  - try-except-finally 结构保证 teardown 执行
  - setup 失败时标记状态为 ERROR（区别于 FAIL 的 steps 失败）
  - setup 失败时跳过 steps 但仍执行 teardown
  - 全局钩子和用例级钩子的执行时机控制
  - **验证**: global_setup → setup → steps → teardown → global_teardown 顺序正确

- [x] **Task 2.7**: 编写钩子引擎单元测试 (tests/unit/test_hook_engine.py)
  - 测试 HTTP/Command/Script 三种执行器
  - 测试正常流程和异常流程（失败、超时、条件跳过）
  - 测试 Teardown 保证执行（即使 Setup 失败）
  - 测试变量作用域（setup 提取的变量可在 teardown 使用）
  - 测试 condition 表达式求值
  - **目标覆盖率**: ≥ 90%
  - **验证**: pytest tests/unit/test_hook_engine.py 全部通过

---

## 模块 3: 数据驱动引擎 (data_driver.py)

- [x] **Task 3.1**: 创建 data_driver.py 模块骨架
  - 定义 DataSourceConfig 数据类（type, file, mapping, filter, case_name_template）
  - 定义 DataDriver 类结构
  - 定义 TemplateExpander 类（负责参数化替换）
  - **验证**: 模块可导入，数据类定义完整

- [x] **Task 3.2**: 实现 CSV 数据源解析器
  - 实现 _parse_csv(file_path) -> List[Dict] 方法
  - 使用 Python 内置 csv 模块（零依赖）
  - 第一行作为表头（列名），后续行为数据
  - 自动去除空白字符，处理引号包裹的字段
  - 处理编码问题（UTF-8 with BOM 等）
  - 文件不存在时抛出 FileNotFoundError 含清晰路径
  - **验证**: 5 行 CSV 解析为 5 个 Dict，列名正确映射

- [x] **Task 3.3**: 实现 JSON 数据源解析器
  - 实现 _parse_json(file_path) -> List[Dict] 方法
  - 支持两种格式：
    - JSON 数组：直接使用每个元素
    - JSON 对象：使用某个 key 对应的数组
  - 使用 yaml.safe_load 或 json.load 解析
  - 格式错误时给出具体位置的错误信息
  - **验证**: JSON 数组正确解析为多行数据

- [x] **Task 3.4**: 实现模板参数化引擎
  - 实现 expand_template(template: Dict, data_row: Dict) -> Dict 方法
  - 识别并替换 `${data.column_name}` 占位符
  - 递归处理嵌套结构（dict/list/string）
  - 支持在 steps、assertions、extract 等任意位置使用
  - 处理数据源中值为 None 的情况（可选删除该断言或保留原样）
  - **验证**: template 中的 ${data.username} 被替换为实际值

- [x] **Task 3.5**: 实现用例批量生成逻辑
  - 实现 generate_test_cases(data_source_config, template) -> List[TestCase]
  - 加载数据源（CSV/JSON）
  - 遍历每行数据，调用 expand_template 生成独立 TestCase
  - 应用 case_name_template 动态生成用例名称
  - 支持过滤条件（filter 配置）
  - 返回生成的用例列表（可能为空）
  - **验证**: 5 行 CSV + 1 个模板 = 5 个独立的 TestCase 对象

- [x] **Task 3.6**: 编写数据驱动单元测试 (tests/unit/test_data_driver.py)
  - 测试 CSV 解析（正常、空文件、BOM 编码、特殊字符）
  - 测试 JSON 解析（数组格式、对象格式、嵌套结构）
  - 测试模板展开（简单值、嵌套 dict、list、None 值处理）
  - 测试用例生成（数量正确、名称动态化、过滤生效）
  - 测试错误处理（文件缺失、格式错误、模板语法错误）
  - **目标覆盖率**: ≥ 90%
  - **验证**: pytest tests/unit/test_data_driver.py 全部通过

---

## 模块 4: 并发执行器 (concurrent_runner.py)

- [x] **Task 4.1**: 创建 concurrent_runner.py 骨架与数据结构
  - 定义 ConcurrencyResult 数据类（total_tests, passed, failed, total_time, parallel_time, speedup, worker_count, results）
  - 定义 ConcurrentTestRunner 类（接收 TestRunner 实例和 max_workers）
  - 导入 asyncio 和 concurrent.futures
  - **验证**: 模块可导入，数据类正确定义

- [x] **Task 4.2**: 实现异步包装器
  - 实现 _execute_single_wrapper(test_case) async 方法
  - 使用 asyncio.Semaphore(max_workers) 控制并发数
  - 在线程池中运行同步 TestRunner.execute_test_case()
  - 使用 loop.run_in_executor(None, sync_func, *args)
  - 捕获异常并转换为标准的 TestCaseResult
  - **验证**: 单个用例能异步执行并返回结果

- [x] **Task 4.3**: 实现并发调度主逻辑
  - 实现 execute_all(test_cases: List) async -> ConcurrencyResult
  - 为每个 test_case 创建 asyncio.Task
  - 使用 asyncio.gather(*tasks, return_exceptions=True) 并发执行
  - 记录开始时间和结束时间
  - 统计通过/失败数量
  - 计算 speedup = serial_time_estimate / parallel_time
  - **验证**: 10 个用例并发执行，总耗时显著少于串行

- [x] **Task 4.4**: 实现变量作用域隔离
  - 为每个并发任务创建独立的 VariableContext 副本
  - 确保 test_case A 的变量不会泄漏给 test_case B
  - 在 wrapper 开始时深拷贝 context，结束时丢弃
  - **验证**: 并发执行的用例间变量完全隔离

- [x] **Task 4.5**: 实现同步入口封装
  - 提供 run_concurrent(test_cases, workers) 同步方法
  - 内部创建新的事件循环或使用现有循环
  - 处理 Windows 下 asyncio 的兼容性问题
  - **验证**: 可从同步代码直接调用并发执行

- [x] **Task 4.6**: 编写并发执行器单元测试 (tests/unit/test_concurrent_runner.py)
  - 测试基本并发功能（2/5/10 workers）
  - 测试加速比计算准确性
  - 测试错误隔离（某用例失败不影响其他）
  - 测试变量隔离（并发用例间无污染）
  - 测试空用例列表、单用例等边界情况
  - **目标覆盖率**: ≥ 85%
  - **验证**: pytest tests/unit/test_concurrent_runner.py 全部通过

---

## 模块 5: 现有模块集成

- [x] **Task 5.1**: 修改 config.py 集成环境管理
  - Config.__init__() 增加 environment: Optional[str] = None 参数
  - 当 environment 参数存在时，初始化 EnvironmentManager
  - 调用 load_environment() 并合并到 self.config
  - 保持向后兼容：无 environment 参数时行为不变
  - 更新相关 docstring
  - **验证**: Config(environment="staging") 正确加载 staging 配置，Config() 行为不变

- [x] **Task 5.2**: 扩展 CLI 参数解析 (api_test_agent.py)
  - 添加 --env / -e 参数（ choices 可选，或自由输入）
  - 添加 --var 参数（ action='append', nargs='*' ）
  - 添加 -w / --workers 参数（ type=int, default=1 ）
  - 添加 --show-config 标志（ action='store_true' ）
  - 将这些参数传递给 Config 和 TestRunner 初始化
  - 添加 env 子命令（ list, validate, show ）
  - **验证**: python api_test_agent.py run test.yaml --env dev --workers 5 正常工作

- [x] **Task 5.3**: 修改 test_runner.py 集成钩子和数据驱动
  - 在 execute_test_case() 中调用 HookEngine（如果定义了 hooks）
  - 在 execute_test_file() 中检测 data_source 配置
  - 如果存在 data_source，委托 DataDriver 生成多个用例
  - 将 DataDriver 生成的用例列表传递给现有执行逻辑
  - 保持原有 execute_test_step() 不变（复用）
  - **验证**: 带 hooks 的用例正确执行，带 data_source 的文件生成多个子用例

- [x] **Task 5.4**: 集成并发执行到主流程
  - 在 run_tests() 函数中判断是否启用并发模式
  - 如果 workers > 1，使用 ConcurrentTestRunner 替代串行循环
  - 确保报告生成接收到的结果格式一致
  - 处理并发模式下进度显示（可选：实时进度条）
  - **验证**: -w 10 参数触发并发执行，结果正确汇总到报告

---

## 模块 6: 示例、文档与集成测试

- [x] **Task 6.1**: 创建环境管理示例
  - 创建 configs/environments.yaml（dev/staging/prod 完整示例）
  - 创建 .env.example 和 .env.staging.example（不含真实密钥）
  - 创建 examples/v2_environment/basic_usage.yaml
  - 创建 examples/v2_environment/multi_env_demo.yaml
  - 包含详细注释说明每个配置项的作用
  - **验证**: 示例可通过 --env 参数正常运行

- [x] **Task 6.2**: 创建钩子机制示例
  - 创建 examples/v2_hooks/full_lifecycle.yaml（global + case 级 hooks）
  - 创建 examples/v2_hooks/setup_teardown_demo.yaml
  - 创建 examples/v2_hooks/hooks/scripts/sample_setup.py（示例脚本）
  - 展示 HTTP/Command/Script 三种钩子类型
  - 展示条件执行和变量传递
  - **验证**: 示例展示完整的钩子生命周期

- [x] **Task 6.3**: 创建数据驱动测试示例
  - 创建 test_data/login_cases.csv（5 行登录测试数据）
  - 创建 test_data/register_cases.json（JSON 格式示例）
  - 创建 examples/v2_data_driven/csv_example.yaml
  - 创建 examples/v2_data_driven/json_example.yaml
  - 展示参数化断言和动态用例名
  - **验证**: 示例自动生成多个用例并全部通过

- [x] **Task 6.4**: 编写集成测试 (tests/integration/)
  - test_integration_environment.py: 端到端环境切换流程
  - test_integration_hooks.py: 完整生命周期 + 错误恢复
  - test_integration_data_driven.py: CSV/JSON 加载 + 用例生成
  - test_integration_concurrency.py: 并发执行 + 结果聚合
  - test_integration_full_workflow.py: 所有功能组合使用
  - 使用 Mock HTTP Server（responses 库）避免真实网络依赖
  - **验证**: 所有集成测试通过，覆盖主要使用场景

- [x] **Task 6.5**: 更新项目文档
  - 更新 README.md：
    - 添加 v2.0 新功能介绍章节
    - 更新 Quick Start（展示 --env 用法）
    - 添加环境管理、钩子、数据驱动的使用指南
  - 更新 CHANGELOG.md：
    - 记录 v2.0-alpha 的所有变更
    - 分类：New Features / Changed / Deprecated / Fixed
  - 创建 MIGRATION_GUIDE.md（v1.0 → v2.0 迁移说明，强调向后兼容）
  - **验证**: 文档准确反映新功能，示例代码可运行

---

## Task Dependencies

```
Phase 1: 基础模块开发（可部分并行）

Task 1.1 ─┬─> Task 1.2 ─┬─> Task 1.3 ─┬─> Task 1.4 ─┬─> Task 1.5 ─┬─> Task 1.6 ──> Task 1.7
          │              │              │              │              │
          └──────────────┴──────────────┴──────────────┘              │
                                                                         │

Task 2.1 ─┬─> Task 2.2 ─┐
          ├─> Task 2.3 ─┼─> Task 2.5 ──> Task 2.6 ──> Task 2.7
          ├─> Task 2.4 ─┘
          │
          └─> (Task 2.2-2.4 可并行)

Task 3.1 ─┬─> Task 3.2 ─┐
          ├─> Task 3.3 ─┼─> Task 3.4 ──> Task 3.5 ──> Task 3.6
          │              │
          └──────────────┘

Task 4.1 ─> Task 4.2 ─> Task 4.3 ─┬─> Task 4.5
                                  ├─> Task 4.4
                                  └─> Task 4.6

Phase 2: 集成（依赖 Phase 1 完成）

Task 1.7 ─┐
Task 2.7 ─┼─> Task 5.1 ─> Task 5.2 ─┬─> Task 5.3 ─┐
Task 3.6 ─┤                          ├─> Task 5.4 ─┤
Task 4.6 ─┘                          │              │
                                     │              │
Phase 3: 示例与测试                    │              │
                                     │              │
Task 5.4 ─┬─> Task 6.1 ─┐           │              │
         ├─> Task 6.2 ─┼─> Task 6.4 ─┤
         ├─> Task 6.3 ─┤           │
         └─> Task 6.5 ─┘           │
                                    │
                            Task 6.4 ─> Task 6.5 (最终验收)
```

## 并行执行建议

### Week 1-2: 可并行的任务组
- **Group A** (开发者 A): Task 1.1 → 1.7 (环境管理，~3天)
- **Group B** (开发者 B): Task 2.1 → 2.7 (钩子引擎，~3天)
- **Group C** (开发者 C): Task 3.1 → 3.6 (数据驱动，~2天)

### Week 3: 可并行的任务组
- **Group A**: Task 4.1 → 4.6 (并发执行，~2天)
- **Group B**: Task 6.1 → 6.3 (示例编写，~2天)

### Week 4: 串行集成
- Task 5.1 → 5.4 (模块集成，必须等 Phase 1 完成)
- Task 6.4 → 6.5 (测试与文档)
