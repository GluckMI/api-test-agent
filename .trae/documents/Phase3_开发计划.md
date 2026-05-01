# Phase 3 开发计划 - API Test Agent v2.0 平台化

> 基于需求规格书，Phase 3 核心目标是**平台化**：从命令行工具升级为可视化、可扩展的测试平台。

***

## 🎯 Phase 3 核心目标

根据需求规格书 `docs/API_Test_Agent_v2.0_需求规格说明书.md`，Phase 3 包含两大核心模块：

| 模块 | 目标 | 关键功能 | 计划版本 |
|------|------|----------|----------|
| **GUI 编辑器** | 降低测试编写门槛 | Web 界面、可视化拖拽、实时调试 | Phase 3 |
| **Mock 服务** | 独立测试能力 | 内置服务器、规则配置、录制回放 | Phase 3 |

> **注意**: 插件系统已决定暂缓开发，将在后续版本中考虑。

***

## 📋 Phase 3 详细开发任务

### 模块 1: GUI 编辑器（Web 界面）

#### 1.1 技术选型与架构设计
- [ ] 确定前端技术栈（推荐：React + TypeScript + Ant Design）
- [ ] 确定后端框架（推荐：FastAPI 作为 API 网关）
- [ ] 设计前后端分离架构
- [ ] 确定数据格式（YAML ↔ JSON 双向转换）
- [ ] 设计项目目录结构管理方案

#### 1.2 后端 API 网关（FastAPI）
- [ ] 创建 FastAPI 应用骨架
- [ ] 实现项目管理 API：
  - `GET /api/projects` - 获取项目列表
  - `POST /api/projects` - 创建项目
  - `GET /api/projects/{id}` - 获取项目详情
  - `DELETE /api/projects/{id}` - 删除项目
- [ ] 实现测试用例管理 API：
  - `GET /api/tests` - 获取测试用例列表
  - `POST /api/tests` - 创建测试用例
  - `PUT /api/tests/{id}` - 更新测试用例
  - `DELETE /api/tests/{id}` - 删除测试用例
  - `GET /api/tests/{id}/yaml` - 获取 YAML 格式
- [ ] 实现执行 API：
  - `POST /api/tests/run` - 执行单个测试
  - `POST /api/tests/run-all` - 批量执行
  - `GET /api/tests/{id}/results` - 获取执行结果
  - WebSocket 实时推送执行进度
- [ ] 实现环境管理 API：
  - `GET /api/environments` - 获取环境列表
  - `POST /api/environments` - 创建/更新环境配置
- [ ] 实现报告 API：
  - `GET /api/reports` - 获取报告列表
  - `GET /api/reports/{id}` - 获取报告详情

#### 1.3 前端核心界面
- [ ] 创建 React 项目骨架（Vite + TypeScript + Ant Design）
- [ ] 实现主布局：
  - 左侧：项目/用例树
  - 中间：编辑器区域
  - 右侧：属性面板
  - 底部：日志/结果面板
- [ ] 实现用例编辑器：
  - 表单模式编辑（非纯 YAML 文本）
  - 请求配置表单（method/endpoint/headers/params/body）
  - 断言配置表单（支持 15 种断言类型的可视化配置）
  - 钩子配置表单（setup/teardown/global）
  - 数据驱动配置（数据源选择/过滤条件）
- [ ] 实现实时预览：
  - YAML 实时生成（左编辑器/右预览）
  - 语法高亮（Monaco Editor 或 CodeMirror）
- [ ] 实现执行控制台：
  - 一键运行测试
  - 实时显示进度
  - 结果可视化（成功/失败状态、响应时间）
  - 报告查看/下载

#### 1.4 高级编辑器功能
- [ ] 实现拖拽式编排（可选，使用 React Flow）：
  - 拖拽创建测试步骤
  - 连线表示执行顺序
  - 可视化展示数据流（变量提取和使用）
- [ ] 实现智能提示：
  - YAML 自动补全
  - 断言类型提示
  - JSON Path 提示
- [ ] 实现调试功能：
  - 单步执行测试步骤
  - 查看每个步骤的请求/响应
  - 变量实时监控

#### 1.5 GUI 与 YAML 双向同步
- [ ] 实现 YAML 解析器（YAML → JSON Schema → 表单数据）
- [ ] 实现表单数据序列化（表单数据 → YAML）
- [ ] 处理双向同步冲突：
  - 检测 YAML 外部修改
  - 提示用户是否覆盖
  - 支持 diff 查看

***

### 模块 2: Mock 服务

#### 2.1 Mock 服务器核心
- [ ] 创建 MockServer 类（基于 http.server 或 Flask/FastAPI）
- [ ] 实现规则引擎：
  - 基于 URL 路径匹配
  - 基于 HTTP 方法匹配
  - 基于请求头匹配
  - 基于请求体匹配（JSON 模式匹配）
- [ ] 实现响应配置：
  - 静态响应（固定 JSON）
  - 动态响应（基于请求参数生成）
  - 条件响应（根据请求返回不同结果）
- [ ] 实现状态码/延迟配置

#### 2.2 Mock 规则管理
- [ ] 创建 MockRule 数据类：
  - `method`: HTTP 方法
  - `path`: 匹配路径
  - `matchers`: 匹配条件（headers/body/query）
  - `response`: 响应配置
  - `delay`: 延迟时间（ms）
  - `times`: 匹配次数限制（可选）
- [ ] 实现规则文件加载（YAML/JSON 格式）
- [ ] 实现规则热加载（无需重启服务器）
- [ ] 实现规则优先级/排序

#### 2.3 录制回放功能
- [ ] 实现代理模式（作为中间人拦截请求）：
  - 记录真实 API 请求和响应
  - 保存为 Mock 规则文件
- [ ] 实现回放模式：
  - 加载录制的规则
  - 按规则返回模拟响应
- [ ] 实现录制过滤：
  - 排除不需要录制的请求
  - 修改敏感信息（如 token）

#### 2.4 Mock 服务集成
- [ ] 实现 CLI 命令：
  - `api_test_agent.py mock start` - 启动 Mock 服务器
  - `api_test_agent.py mock stop` - 停止 Mock 服务器
  - `api_test_agent.py mock rules list` - 列出规则
  - `api_test_agent.py mock rules add` - 添加规则
- [ ] 实现 GUI 集成：
  - Mock 规则可视化编辑
  - 实时查看匹配的请求
  - 录制/回放控制界面
- [ ] 实现与测试用例集成：
  - 测试用例可配置使用 Mock 端点
  - 支持部分 Mock（某些请求走真实 API，某些走 Mock）

***

### 模块 3: 其他增强（Phase 2 剩余）

#### 3.1 报告增强
- [ ] 历史对比功能：
  - 存储历史测试报告
  - 比较两次运行的差异
  - 高亮新增/修复的失败用例
- [ ] 趋势图表：
  - 通过率趋势图（按时间）
  - 响应时间趋势图
  - 使用 ECharts 或 Chart.js 生成
  - 导出为图片
- [ ] 失败聚合：
  - 识别相同错误模式的失败用例
  - 按错误类型分组
  - 提供根因分析提示

#### 3.2 CLI 增强
- [ ] 交互式向导模式（`api_test_agent.py init --interactive`）
- [ ] 测试用例模板生成器
- [ ] 智能补全（shell completion）
- [ ] 进度条显示（tqdm 集成）

***

## 🗺️ 实施路线

### 第一阶段：基础架构（2-3 周）
1. 确定技术栈，搭建 FastAPI + React 骨架
2. 实现基础 API 网关（项目/测试/执行管理）
3. 实现基本前端界面（用例列表、表单编辑）
4. 实现 YAML 双向同步核心逻辑

### 第二阶段：GUI 核心功能（3-4 周）
5. 完善用例编辑器（所有配置项可视化）
6. 实现执行控制台和结果展示
7. 实现报告查看和下载
8. 实现调试功能（单步执行、请求/响应查看）

### 第三阶段：Mock 服务（2-3 周）
9. 实现 Mock 服务器核心
10. 实现规则管理和热加载
11. 实现录制回放功能
12. 集成到 CLI 和 GUI

### 第四阶段：增强与优化（2-3 周）
13. 实现报告增强（历史对比/趋势图）
14. 实现 CLI 增强（交互向导/进度条）
15. 完善文档和示例
16. 性能优化和 bug 修复

***

## ⚠️ 技术风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| 前后端同步复杂性 | 开发效率降低 | 使用 OpenAPI/Swagger 自动生成前端类型 |
| GUI 编辑器复杂度 | 开发周期延长 | 分阶段交付，先表单模式，后拖拽模式 |
| Mock 录制兼容性 | 部分 API 无法录制 | 提供手动规则配置作为备选 |
| 向后兼容性 | 现有用户迁移成本 | 保持 CLI 不变，GUI 作为额外功能 |

***

## 📊 交付物清单

### 代码交付
- [ ] `src/api_test_agent/gui/` - GUI 后端（FastAPI）
- [ ] `frontend/` - GUI 前端（React + TypeScript）
- [ ] `src/api_test_agent/mock/` - Mock 服务

### 文档交付
- [ ] `docs/GUI_使用指南.md` - GUI 编辑器使用文档
- [ ] `docs/Mock_服务指南.md` - Mock 服务使用文档
- [ ] `docs/Phase3_架构设计.md` - 架构设计文档

### 示例交付
- [ ] `examples/v3_gui/` - GUI 使用示例
- [ ] `examples/v3_mock/` - Mock 服务示例

***

## ✅ 验收标准

1. **GUI 编辑器**：
   - 能通过浏览器访问
   - 能创建、编辑、执行测试用例
   - YAML 与表单双向同步
   - 实时查看测试结果
   - 报告查看和下载

2. **Mock 服务**：
   - 能启动独立 Mock 服务器
   - 能配置和管理规则
   - 能录制真实 API 响应并回放
   - CLI 和 GUI 都能控制

3. **整体质量**：
   - 单元测试覆盖率 ≥ 80%
   - 集成测试覆盖核心场景
   - 文档完整、示例可运行
   - 向后兼容（v2.0 用户无需修改测试用例）

***

> **预计完成版本**: v3.0.0
> **预计开发周期**: 9-13 周（基于单人开发）
> **优先级建议**: GUI 编辑器 > Mock 服务 > 报告增强
