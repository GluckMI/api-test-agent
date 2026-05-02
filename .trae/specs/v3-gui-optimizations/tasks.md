# Tasks

- [x] Task 1: 统一版本号
  - [x] SubTask 1.1: 修改 `src/api_test_agent/__init__.py` 版本号为 "3.0.0-alpha"
  - [x] SubTask 1.2: 修改 `src/api_test_agent/gui/config.py` 使用统一版本引用
  - [x] SubTask 1.3: 验证版本号一致性

- [x] Task 2: 修复异步阻塞问题
  - [x] SubTask 2.1: 修改 `execution_service.py`，使用 `run_in_executor` 包装同步 TestRunner
  - [x] SubTask 2.2: 添加 ThreadPoolExecutor 初始化（max_workers=4）
  - [x] SubTask 2.3: 确保进度回调在线程安全环境下调用
  - [x] SubTask 2.4: 测试并发执行不阻塞

- [x] Task 3: 添加内存清理机制
  - [x] SubTask 3.1: 修改 `websocket/manager.py`，添加最大连接数限制（100/执行ID）
  - [x] SubTask 3.2: 实现 `cleanup_stale_connections()` 方法定期清理断开连接
  - [x] SubTask 3.3: 修改 `execution_service.py` 使用 OrderedDict 限制最多 500 条记录
  - [x] SubTask 3.4: 实现 FIFO 自动清理策略
  - [x] SubTask 3.5: 测试长期运行不内存泄漏

- [x] Task 4: 添加输入验证和安全限制
  - [x] SubTask 4.1: 所有 YAML 解析使用 `yaml.safe_load()`（已存在，验证）
  - [x] SubTask 4.2: 添加 YAML 文件大小限制（10MB）
  - [x] SubTask 4.3: 添加路径遍历检查（禁止 `..`）
  - [x] SubTask 4.4: 添加 test_id 格式验证
  - [x] SubTask 4.5: 实现自定义限流中间件（滑动窗口算法）
  - [x] SubTask 4.6: 应用限流到执行接口（10次/分钟/IP）和 CRUD 接口（30次/分钟/IP）

- [x] Task 5: 前端性能优化
  - [x] SubTask 5.1: 为 `TestCaseList.tsx` 添加 React.memo 优化列表项
  - [x] SubTask 5.2: 为 `Dashboard.tsx` 添加 useMemo/useCallback 优化
  - [x] SubTask 5.3: 为 `ExecutionConsole.tsx` 优化日志状态更新
  - [x] SubTask 5.4: 为 >100 条数据实现虚拟滚动（使用 antd List virtual scroll）
  - [x] SubTask 5.5: 测试渲染性能（Chrome DevTools Performance）

- [x] Task 6: 增强日志系统
  - [x] SubTask 6.1: 修改 `gui_server.py` 的 `setup_logging()` 添加 RotatingFileHandler
  - [x] SubTask 6.2: 配置日志目录 `logs/` 自动创建
  - [x] SubTask 6.3: 配置 10MB 单文件，保留 5 个备份
  - [x] SubTask 6.4: 测试日志文件轮转功能

- [x] Task 7: 增强健康检查端点
  - [x] SubTask 7.1: 修改 `gui/__init__.py` 的 `/health` 端点
  - [x] SubTask 7.2: 添加磁盘空间使用率检查
  - [x] SubTask 7.3: 添加活跃 WebSocket 连接数
  - [x] SubTask 7.4: 添加内存使用情况（psutil 或手动计算）
  - [x] SubTask 7.5: 测试健康检查响应

- [x] Task 8: 收紧 CORS 配置
  - [x] SubTask 8.1: 修改 `gui/config.py` 的 CORS 配置
  - [x] SubTask 8.2: 允许通过环境变量配置允许的源列表
  - [x] SubTask 8.3: 测试 CORS 策略生效

- [x] Task 9: 完善 MockManager 占位功能
  - [x] SubTask 9.1: 完善 `frontend/src/pages/MockManager.tsx` 页面内容
  - [x] SubTask 9.2: 添加"开发中"提示和预计上线时间
  - [x] SubTask 9.3: 添加功能预览或演示

# Task Dependencies

- Task 2（异步修复）独立执行，无依赖
- Task 3（内存清理）独立执行，无依赖
- Task 4（输入验证）独立执行，无依赖
- Task 5（前端优化）独立执行，无依赖
- Task 6（日志增强）独立执行，无依赖
- Task 7（健康检查）依赖 Task 3（需要 WebSocket 连接数）
- Task 8（CORS）独立执行，无依赖
- Task 9（MockManager）独立执行，无依赖
- Task 1（版本号）最先执行（基础一致性）

# 执行顺序

1. Task 1: 统一版本号（基础）
2. Task 2-6: 可并行执行（独立模块）
3. Task 7: 在 Task 3 之后执行
4. Task 8-9: 可并行执行
