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
