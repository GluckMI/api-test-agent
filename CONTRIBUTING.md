# 🤝 贡献指南

欢迎为 API Test Agent 项目做出贡献！

## 📋 快速开始

### 1. Fork 仓库

点击页面右上角的 "Fork" 按钮，将仓库克隆到你的 GitHub 账户。

### 2. Clone 本地

```bash
git clone https://github.com/YOUR_USERNAME/api-test-agent.git
cd api-test-agent
pip install -r requirements.txt
```

### 3. 创建功能分支

```bash
git checkout -b feature/my-new-feature
```

## 🛠️ 开发环境设置

### 依赖安装

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有的话
```

### 代码风格

本项目遵循以下代码规范：

- **PEP 8**: Python 代码风格指南
- **类型注解**: 重要函数建议添加类型提示
- **注释**: 公共 API 需要 docstring

### 运行测试

```bash
# 单元测试
python -m pytest tests/unit/ -v

# 集成测试
python -m pytest tests/integration/ -v

# 覆盖率报告
python -m pytest --cov=. --cov-report=html
```

## 📝 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type（必须）

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式调整 |
| `refactor` | 重构 |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建过程或辅助工具变动 |

#### Scope（可选）

指明影响的模块范围，如：`assertion`, `cli`, `report`, `core` 等

#### Subject（必须）

简短描述，不超过 50 个字符

#### Body（可选）

详细描述改动内容

#### Footer（可选）

- 关闭的 Issue ID: `Closes #123`
- Breaking Changes: `BREAKING CHANGE: description`

### 示例

```
feat(assertion): 添加 status_code_in 断言类型

支持检查状态码是否在指定范围内，例如：
```yaml
assertions:
  - type: status_code_in
    expected: [200, 201]
```

Closes #42
```

## 🔀 Pull Request 流程

1. 在 GitHub 上创建 PR
2. 填写清晰的 PR 描述
3. 确保所有 CI 检查通过
4. 等待维护者 Review
5. 根据反馈修改后重新提交
6. 合并到主分支

### PR 模板

```markdown
## 变更描述

简要描述这次 PR 做了什么

## 相关 Issue

Closes #issue_number

## 测试情况

- [ ] 添加了单元测试
- [ ] 测试通过率 100%
- [ ] 手动测试通过
- [ ] 更新了相关文档

## 截图（如有）

展示效果变化（可选）

## 后续工作

列出可能的改进方向（可选）
```

## 🐛 报告 Bug

使用 GitHub Issues 报告 Bug，包含：

1. **标题**: 清晰的问题描述
2. **复现步骤**: 详细的操作步骤
3. **预期行为**: 应该发生什么
4. **实际行为**: 实际发生了什么
5. **环境信息**: OS、Python 版本等
6. **日志/截图**: 错误堆栈或截图

## 💡 功能请求

使用 GitHub Discussions 讨论新功能：

1. 先搜索是否有类似提议
2. 说明使用场景和动机
3. 提供具体的实现思路
4. 等待社区反馈

## 👥 团队角色

### Maintainers（维护者）

- QwenPaw Team
- 负责核心架构和代码审查

### Contributors（贡献者）

- 提交 PR 并接受指导
- 可以成为 Maintainer

### Community（社区用户）

- 提出问题和建议
- 分享使用案例

## ⚖️ 许可证

贡献的代码将遵循 MIT License

---

**感谢每一位贡献者！** 🎉
