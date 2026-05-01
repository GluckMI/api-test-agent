# Checklist - API Test Agent v2.0 核心功能实现

## 环境管理器 (environment.py) 验收检查

- [x] **ENV-001**: EnvironmentManager 可成功实例化并加载有效的 environments.yaml 文件
- [x] **ENV-002**: list_environments() 返回正确的环境名称列表（如 ['dev', 'staging', 'prod']）
- [x] **ENV-003**: load_environment('dev') 正确加载 dev 环境，包含 base_url、timeout、variables
- [x] **ENV-004**: defaults 配置被所有环境继承（如 headers.Content-Type）
- [x] **ENV-005**: 环境特定配置覆盖 defaults 同名字段（如 staging.timeout=30 覆盖默认值）
- [x] **ENV-006**: .env.staging 文件存在时自动加载，变量存入 env_variables 字典
- [x] **ENV-007**: .env 文件不存在时输出警告但不阻塞执行
- [x] **ENV-008**: apply_overrides({'timeout': '999'}) 使最终 timeout=999（最高优先级）
- [x] **ENV-009**: 嵌套键覆盖生效（如 headers.Authorization='Bearer xxx'）
- [x] **ENV-010**: validate_environment() 检测到缺少 base_url 时返回错误列表
- [x] **ENV-011**: validate_environment() 检测到无效 URL 格式时返回错误信息
- [x] **ENV-012**: 加载不存在的环境名时抛出 ValueError 并提示可用环境列表
- [x] **ENV-013**: 敏感变量（*_KEY, *_TOKEN 等）在 --show-config 输出中已脱敏
- [x] **ENV-014**: 敏感变量在日志中自动脱敏显示
- [x] **ENV-015**: 不带 --env 参数时行为与 v1.0 完全一致（向后兼容）
- [x] **ENV-016**: 单元测试覆盖率 ≥ 95%（pytest-cov 报告）

---

## 钩子引擎 (hook_engine.py) 验收检查

- [x] **HOOK-001**: HTTP 类型钩子能正确发送请求（POST /setup/init）
- [x] **HOOK-002**: HTTP 钩子可通过 extract 配置提取响应中的变量
- [x] **HOOK-003**: Command 类型钩子能正确执行 Shell 命令（python script.py）
- [x] **HOOK-004**: Script 类型钩子能动态导入并执行 Python 脚本
- [x] **HOOK-005**: 多个 hook 按定义顺序依次执行
- [x] **HOOK-006**: 全局钩子 global_setup 在整个测试套件开始时执行一次
- [x] **HOOK-007**: 用例级 setup 在每个测试用例的 steps 之前执行
- [x] **HOOK-008**: 用例级 teardown 在每个测试用例结束后执行
- [x] **HOOK-009**: global_teardown 在整个测试套件结束时执行
- [x] **HOOK-010**: Setup 中提取的变量可在后续 steps 和 teardown 中使用（${var} 语法）
- [x] **HOOK-011**: Setup 失败时，teardown 仍然保证执行（finally 逻辑）
- [x] **HOOK-012**: Setup 失败时，steps 被跳过不执行
- [x] **HOOK-013**: Setup 失败的用例状态标记为 ERROR（区别于 FAIL）
- [x] **HOOK-014**: condition: "${order_id} is not none" 条件为 False 时跳过该钩子
- [x] **HOOK-015**: ignore_failure: true 时单步失败不中断后续钩子执行
- [x] **HOOK-016**: 钩子执行结果在 HTML 报告中可见（可折叠详情）
- [x] **HOOK-017**: 单元测试覆盖率 ≥ 90%

---

## 数据驱动引擎 (data_driver.py) 验收检查

- [x] **DATA-001**: CSV 文件正确解析，第一行为表头，每行生成一个数据字典
- [x] **DATA-002**: JSON 数组格式文件正确解析为多行数据
- [x] **DATA-003**: JSON 对象格式文件可指定某个 key 的数组作为数据源
- [x] **DATA-004**: template 中的 ${data.username} 被替换为 CSV 中的实际值
- [x] **DATA-005**: template 中的 ${data.expected_code} 在断言中动态替换
- [x] **DATA-006**: 5 行 CSV 数据 + 1 个模板 = 生成 5 个独立的 TestCase
- [x] **DATA-007**: 每个生成的用例有唯一的名称（支持 case_name_template）
- [x] **DATA-008**: 生成的每个用例独立执行、独立统计通过/失败
- [x] **DATA-009**: CSV 文件路径不存在时给出清晰错误信息（含路径）
- [x] **DATA-010**: CSV 格式错误（如列数不一致）时有友好的错误提示
- [x] **DATA-011**: 支持 filter 配置过滤特定行的数据
- [x] **DATA-012**: 数据值为 None 时，对应断言可选跳过或保留原样
- [x] **DATA-013**: UTF-8 BOM 编码的 CSV 文件能正常解析
- [x] **DATA-014**: 1000 行 CSV 加载 + 生成用例耗时 < 1 秒（性能要求）
- [x] **DATA-015**: 单元测试覆盖率 ≥ 90%

---

## 并发执行器 (concurrent_runner.py) 验收检查

- [x] **CONC-001**: -w 10 参数触发并发模式，10 个 Worker 同时工作
- [x] **CONC-002**: 50 个独立用例在 -w 10 下总耗时 ≈ 串行时间的 1/10（±20%）
- [x] **CONC-003**: 单个用例失败不影响其他并发用例的执行结果
- [x] **CONC-004**: 并发结果正确聚合到统一的 TestSuiteResult
- [x] **CONC-005**: 通过率计算准确（passed/total）
- [x] **CONC-006**: 用例 A 提取的变量不会污染用例 B（作用域隔离）
- [x] **CONC-007**: -w auto 自动检测 CPU 核心数作为 worker 数量
- [x] **CONC-008**: -w 1 时退化为串行模式（完全兼容原有行为）
- [x] **CONC-009**: 并发模式下报告生成正常（HTML/JSON/Markdown）
- [x] **CONC-010**: 控制台进度输出清晰（可选：实时进度条或完成百分比）
- [x] **CONC-011**: 空用例列表时优雅处理（不崩溃，输出空报告）
- [x] **CONC-012**: 单个用例异常不影响整个并发流程（异常隔离）
- [x] **CONC-013**: Windows 平台下 asyncio 兼容运行无报错
- [x] **CONC-014**: 内存占用合理（500 用例并发 < 100MB 增量）
- [x] **CONC-015**: 单元测试覆盖率 ≥ 85%

---

## CLI 与集成验收检查

- [x] **CLI-001**: `python api_test_agent.py run test.yaml --env dev` 正常工作
- [x] **CLI-002**: `python api_test_agent.py run test.yaml -e staging` 短选项可用
- [x] **CLI-003**: `--var token=abc123` 动态覆盖配置项
- [x] **CLI-004**: `-w 10` 或 `--workers 10` 启用并发执行
- [x] **CLI-005**: `--show-config` 显示当前环境配置详情（脱敏后）
- [x] **CLI-006**: `python api_test_agent.py env list` 列出所有可用环境
- [x] **CLI-007**: `python api_test_agent.py env validate --env staging` 校验环境完整性
- [x] **CLI-008**: 所有新参数均为可选，不影响 v1.0 的任何现有用法
- [x] **INT-001**: 完整 E2E 场景：环境切换 + 钩子 + 数据驱动 + 并发 组合使用通过
- [x] **INT-002**: v1.0 格式的旧测试用例无需修改即可在 v2.0 运行
- [x] **INT-003**: 集成测试覆盖主要使用场景（≥ 10 个集成测试 case）

---

## 示例与文档验收检查

- [x] **EXAMPLE-001**: configs/environments.yaml 包含完整的 3 环境示例
- [x] **EXAMPLE-002**: .env.example 文件存在且注释清晰
- [x] **EXAMPLE-003**: examples/v2_environment/ 目录下有 ≥ 2 个可运行的示例
- [x] **EXAMPLE-004**: examples/v2_hooks/ 展示完整生命周期和三种钩子类型
- [x] **EXAMPLE-005**: examples/v2_data_driven/ 展示 CSV 和 JSON 两种数据源用法
- [x] **DOC-001**: README.md 更新了 v2.0 新功能的 Quick Start
- [x] **DOC-002**: README.md 包含环境管理、钩子、数据驱动的使用示例代码块
- [x] **DOC-003**: CHANGELOG.md 记录了 v2.0-alpha 的所有变更
- [x] **DOC-004**: MIGRATION_GUIDE.md 说明 v1.0 → v2.0 的迁移步骤（强调兼容性）

---

## 性能与质量验收检查

- [x] **PERF-001**: 单用例框架开销 < 100ms（不含网络时间）
- [x] **PERF-002**: 配置文件加载耗时 < 10ms
- [x] **PERF-003**: 并发调度开销 < 5ms/用例
- [x] **PERF-004**: 1000 行 CSV 解析 < 1s
- [x] **PERF-005**: 500 个用例的 HTML 报告生成 < 5s
- [x] **QUAL-001**: 核心模块（environment, hook_engine, data_driver）单元测试全通过
- [x] **QUAL-002**: 集成测试全通过（tests/integration/）
- [x] **QUAL-003**: black 代码格式化检查通过（无 style 错误）
- [x] **QUAL-004**: flake8 lint 检查通过（无 import/语法错误）
- [x] **QUAL-005**: mypy 类型注解检查通过（公共 API 无类型错误）
- [x] **QUAL-006**: 新增代码无硬编码敏感信息（无真实 API Key/密码）

---

## 最终发布检查

- [x] **RELEASE-001**: 所有上述 checklist 项 100% 通过
- [x] **RELEASE-002**: Git 版本号打 tag: v2.0-alpha
- [x] **RELEASE-003**: PyPI 发布（test-pypi 先验证）
- [x] **RELEASE-004**: GitHub Release 创建（含 Change Log）
- [x] **RELEASE-005**: 团队内部演示准备就绪
