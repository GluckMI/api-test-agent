# API Test Agent v3.0 - 系统优化修复 Spec

## Why

API Test Agent v3.0 GUI 功能虽已完善，但存在以下关键问题：
1. **异步阻塞问题**：TestRunner 同步调用阻塞 asyncio 事件循环，导致并发请求卡住
2. **内存泄漏风险**：WebSocket 连接和执行记录无清理机制，长期运行会内存溢出
3. **版本不一致**：`__init__.py` 显示 v2.0.0，但 GUI 标注 v3.0.0-alpha
4. **缺乏安全限制**：无输入验证、无限流，易被滥用
5. **前端性能差**：未使用 React 优化手段（memo、useMemo）

本次优化将修复除认证外的所有 P0/P1/P2 问题，提升系统稳定性、性能和安全性。

## What Changes

### 核心修复
- **execution_service.py**: 使用 ThreadPoolExecutor 包装同步 TestRunner 调用
- **websocket/manager.py**: 添加连接清理、最大连接数限制
- **execution_service.py**: 添加执行记录自动清理、有序字典限制历史数量
- **__init__.py**: 版本号更新为 v3.0.0-alpha

### 安全增强
- **所有路由**: 添加输入验证（YAML 安全加载、路径检查）
- **请求限流**: 使用滑动窗口限流（自定义实现，不引入新依赖）
- **错误处理**: 敏感信息脱敏，生产模式隐藏堆栈

### 性能优化
- **前端组件**: 使用 React.memo 优化重渲染
- **长列表**: 使用虚拟滚动（react-virtualized 或 antd 虚拟列表）
- **数据获取**: 使用 useMemo/useCallback 优化

### 体验增强
- **日志系统**: 添加文件轮转处理器
- **健康检查**: 扩展 /health 端点（依赖状态检查）
- **CORS**: 限制为明确定义的源
- **MockManager**: 占位功能完善

### BREAKING Changes
- 无（完全向后兼容）

## Impact

- Affected specs: v3.0-gui-optimizations
- Affected code:
  - 后端修复: execution_service.py, websocket/manager.py, __init__.py, gui_server.py
  - 前端优化: ExecutionConsole.tsx, Dashboard.tsx, TestCaseList.tsx, TestCaseEditor.tsx
  - 安全增强: 所有 routes/*.py, 中间件

## ADDED Requirements

### Requirement: 异步非阻塞执行 (ASYNC-EXEC)

系统 SHALL 支持异步非阻塞执行测试，不阻塞 FastAPI 事件循环。

#### 实现方式
- 使用 `asyncio.get_event_loop().run_in_executor()` 将同步 TestRunner 放到线程池
- 线程池大小可配置（默认 4 worker）
- 执行状态通过回调/事件推送更新

#### 场景 1: 并发请求不阻塞
- **GIVEN** 同时发起 5 个测试执行请求
- **WHEN** 第 1 个测试执行中（耗时 10s）
- **THEN** 其他 4 个请求可正常响应（非阻塞）
- **AND** 每个请求的执行状态独立更新

---

### Requirement: 内存管理与清理 (MEM-CLEANUP)

系统 SHALL 提供自动内存清理机制，防止长期运行导致内存溢出。

#### WebSocket 连接管理
- 最大同时连接数：100/执行 ID
- 断开连接后自动清理
- 定期清理空闲连接（60s 无活动）

#### 执行记录管理
- 使用 OrderedDict 限制最多保留 500 条历史记录
- 自动移除最旧记录（FIFO）
- 提供手动清理 API

#### 场景 1: 执行记录自动清理
- **GIVEN** 系统已有 500 条执行记录
- **WHEN** 新增第 501 条执行
- **THEN** 自动移除第 1 条（最旧记录）
- **AND** 保留最近的 500 条

---

### Requirement: 输入验证与安全 (INPUT-SECURITY)

系统 SHALL 对所有用户输入进行验证和清洗，防止注入攻击。

#### YAML 安全
- 使用 `yaml.safe_load()` 禁止任意对象反序列化
- 限制 YAML 文件大小（10MB）
- 验证 YAML 结构（仅允许定义的字段）

#### 路径安全
- 禁止路径遍历（`..` 检查）
- 限制文件路径在 `gui_data/` 目录下
- 验证 test_id 格式（UUID 或合法字符串）

#### 请求限流
- 执行接口：10 次/分钟/IP
- CRUD 接口：30 次/分钟/IP
- WebSocket：5 个并发连接/IP

#### 场景 1: 恶意 YAML 拒绝
- **GIVEN** 用户提交包含 `!!python/object` 的 YAML
- **WHEN** 尝试解析
- **THEN** 返回错误："YAML 格式无效：不允许任意对象反序列化"

---

### Requirement: 版本号统一 (VERSION-SYNC)

系统中所有版本号 SHALL 保持一致。

#### 修改点
- `src/api_test_agent/__init__.py`: `__version__ = "3.0.0-alpha"`
- 从 `gui/config.py` 移除硬编码版本，改为引用核心版本

---

### Requirement: 前端性能优化 (FE-PERF)

前端组件 SHALL 使用 React 性能优化手段。

#### 组件优化
- `React.memo()` 用于列表项组件
- `useMemo()` 用于计算结果缓存
- `useCallback()` 用于事件处理函数
- 虚拟列表用于 >100 条数据的场景

#### 场景 1: 测试用例列表渲染
- **GIVEN** 100 个测试用例
- **WHEN** 打开 TestCaseList 页面
- **THEN** 仅渲染可见区域（虚拟滚动）
- **AND** 滚动时不卡顿（<16ms/帧）

---

## MODIFIED Requirements

### Requirement: 日志系统增强 (LOG-ENHANCE)

现有 setup_logging 函数 SHALL 扩展为支持文件轮转。

#### 修改点
- 添加 `RotatingFileHandler`（10MB 单文件，保留 5 个备份）
- 日志目录 `logs/` 自动创建
- 日志格式保持不变（`%(asctime)s - %(levelname)s - %(message)s`）

---

### Requirement: 健康检查增强 (HEALTH-ENHANCE)

现有 `/health` 端点 SHALL 扩展为显示依赖状态。

#### 新增信息
- 磁盘空间使用率
- 数据库状态（如使用）
- 活跃 WebSocket 连接数
- 内存使用情况

---

### Requirement: CORS 限制收紧 (CORS-TIGHTEN)

现有 CORS 配置 SHALL 限制为明确的源。

#### 修改点
- `gui/config.py` 中移除通配 `*`
- 仅允许配置的源列表（环境变量可覆盖）
- 限制允许的方法（GET/POST/PUT/DELETE 等，不含 TRACE）

---

## REMOVED Requirements

无（仅优化，不删除任何现有功能）
