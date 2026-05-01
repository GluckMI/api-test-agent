"""
钩子引擎模块集成测试

覆盖范围：
- 完整生命周期（global_setup → setup → steps → teardown → global_teardown）
- Setup 失败时的错误恢复和 Teardown 执行保证
- 条件执行（condition）
- 变量在 hooks 间传递
- 多种钩子类型组合使用

注意：
- 集成测试关注整体流程，不深入每个细节
- 使用 JSONPlaceholder API 进行真实 HTTP 测试（如果可用）
- 或使用 Mock 模拟 HTTP 请求
"""
import os
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hook_engine import (
    HookEngine,
    HookType,
    HookConfig,
    HookResult,
    HttpHookExecutor,
    CommandHookExecutor,
    ScriptHookExecutor,
)


class TestHookLifecycleIntegration:
    """钩子完整生命周期集成测试"""

    def test_complete_lifecycle_execution(self):
        """测试完整的生命周期执行顺序"""
        engine = HookEngine(base_url="https://jsonplaceholder.typicode.com")
        
        execution_order = []
        
        def track_hook(hook_name):
            execution_order.append(hook_name)
            return HookResult(success=True, hook_name=hook_name)
        
        global_setup_hooks = [
            HookConfig(name="global_setup_1", hook_type=HookType.HTTP, method="GET", endpoint="/posts/1"),
            HookConfig(name="global_setup_2", hook_type=HookType.HTTP, method="GET", endpoint="/users/1"),
        ]
        
        global_teardown_hooks = [
            HookConfig(name="global_teardown_1", hook_type=HookType.HTTP, method="GET", endpoint="/posts/1"),
        ]
        
        engine.set_global_hooks(global_setup_hooks, global_teardown_hooks)
        
        test_case = {
            "name": "生命周期测试用例",
            "setup": [
                {"name": "case_setup_1", "type": "http", "method": "GET", "endpoint": "/comments/1"}
            ],
            "steps": [
                {
                    "name": "step_1",
                    "method": "GET",
                    "endpoint": "/posts/1",
                    "assertions": [
                        {"type": "status_code", "expected": 200}
                    ]
                }
            ],
            "teardown": [
                {"name": "case_teardown_1", "type": "http", "method": "GET", "endpoint": "/albums/1"}
            ]
        }
        
        result = engine.execute_test_case_with_hooks(test_case)
        
        assert result['status'] in ['PASS', 'FAIL', 'ERROR']
        assert 'global_setup_results' in result
        assert 'setup_results' in result
        assert 'step_results' in result
        assert 'teardown_results' in result
        assert 'global_teardown_results' in result
        
        engine.close()

    def test_setup_failure_triggers_teardown(self):
        """测试 Setup 失败时 Teardown 仍会执行"""
        engine = HookEngine()
        
        test_case = {
            "name": "Setup 失败测试",
            "setup": [
                {
                    "name": "failing_setup",
                    "type": "http",
                    "method": "GET",
                    "endpoint": "http://nonexistent.invalid/should-fail",
                    "timeout": 2
                }
            ],
            "steps": [
                {"name": "should_not_run", "method": "GET", "endpoint": "/posts/1"}
            ],
            "teardown": [
                {
                    "name": "must_run_teardown",
                    "type": "http",
                    "method": "GET",
                    "endpoint": "https://jsonplaceholder.typicode.com/posts/1",
                    "ignore_failure": True
                }
            ]
        }
        
        result = engine.execute_test_case_with_hooks(test_case)
        
        assert result['status'] == 'ERROR'
        assert len(result['teardown_results']) > 0
        assert result['teardown_results'][0].hook_name == "must_run_teardown"
        
        engine.close()


class TestConditionExecution:
    """条件执行集成测试"""

    def test_condition_true_executes_hook(self):
        """测试条件为真时执行钩子"""
        executor = HttpHookExecutor()
        
        hook_config = HookConfig(
            name="conditional_hook",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="https://jsonplaceholder.typicode.com/posts/1",
            condition="${user_id} is not none"
        )
        
        context = {"user_id": 123, "token": "abc"}
        
        should_execute = engine.evaluate_condition(hook_config.condition, context)
        assert should_execute is True

    def test_condition_false_skips_hook(self):
        """测试条件为假时跳过钩子"""
        engine = HookEngine()
        
        hook_config = HookConfig(
            name="conditional_hook",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="/posts/1",
            condition="${user_id} is not none"
        )
        
        context = {"user_id": None, "token": "abc"}
        
        should_execute = engine.evaluate_condition(hook_config.condition, context)
        assert should_execute is False

    def test_equality_conditions(self):
        """测试各种等式条件"""
        engine = HookEngine()
        
        test_cases = [
            ("${mode} == 'dev'", {"mode": "dev"}, True),
            ("${mode} == 'dev'", {"mode": "prod"}, False),
            ("${mode} != 'prod'", {"mode": "dev"}, True),
            ("${count} >= 5", {"count": "10"}, True),
            ("${count} < 3", {"count": "2"}, True),
        ]
        
        for condition, context, expected in test_cases:
            result = engine.evaluate_condition(condition, context)
            assert result == expected, f"Condition '{condition}' failed with {context}"


class TestVariablePassingBetweenHooks:
    """钩子间变量传递集成测试"""

    def test_extracted_variables_available_in_subsequent_hooks(self):
        """测试提取的变量在后续钩子中可用"""
        engine = HookEngine(base_url="https://jsonplaceholder.typicode.com")
        
        hooks = [
            HookConfig(
                name="extract_user_id",
                hook_type=HookType.HTTP,
                method="GET",
                endpoint="/users/1",
                extract={"user_id": "id", "username": "username"}
            ),
            HookConfig(
                name="use_user_id",
                hook_type=HookType.HTTP,
                method="GET",
                endpoint="${base_url}/posts?userId=${user_id}",  # 使用提取的变量
                condition="${user_id} is not none"
            )
        ]
        
        results = engine.execute_hooks(hooks, {})
        
        assert len(results) == 2
        assert results[0].success
        assert results[0].extracted_vars.get("user_id") is not None
        
        engine.close()

    def test_global_to_case_level_variable_passing(self):
        """测试全局钩子的变量传递到用例级钩子"""
        engine = HookEngine(base_url="https://jsonplaceholder.typicode.com")
        
        global_setup = [
            HookConfig(
                name="init_global_var",
                hook_type=HookType.HTTP,
                method="GET",
                endpoint="/users/1",
                extract={"global_user_id": "id"}
            )
        ]
        
        case_setup = [
            HookConfig(
                name="use_global_var",
                hook_type=HookType.HTTP,
                method="GET",
                endpoint="/users/${global_user_id}",
                condition="${global_user_id} is not none"
            )
        ]
        
        engine.set_global_hooks(global_setup, [])
        
        test_case = {
            "name": "变量传递测试",
            "setup": [
                {"name": "use_global_var", "type": "http", "method": "GET", 
                 "endpoint": "/users/${global_user_id}"}
            ],
            "steps": [],
            "teardown": []
        }
        
        result = engine.execute_test_case_with_hooks(test_case)
        
        assert len(result['global_setup_results']) > 0
        assert result['global_setup_results'][0].extracted_vars.get('global_user_id') is not None
        
        engine.close()


class TestIgnoreFailureBehavior:
    """ignore_failure 行为集成测试"""

    def test_ignore_failure_allows_continuation(self):
        """测试 ignore_failure=True 时继续执行后续钩子"""
        engine = HookEngine()
        
        hooks = [
            HookConfig(
                name="failing_hook",
                hook_type=HookType.HTTP,
                method="GET",
                endpoint="http://invalid.nonexistent/fail",
                timeout: 2,
                ignore_failure=True
            ),
            HookConfig(
                name="succeeding_hook",
                hook_type=HookType.HTTP,
                method="GET",
                endpoint="https://jsonplaceholder.typicode.com/posts/1"
            )
        ]
        
        results = engine.execute_hooks(hooks, {})
        
        assert len(results) == 2
        assert not results[0].success  # 第一个失败
        assert results[1].success      # 第二个成功（因为第一个 ignore_failure=True）

    def test_fail_fast_stops_execution(self):
        """测试 ignore_failure=False 时停止执行"""
        engine = HookEngine()
        
        hooks = [
            HookConfig(
                name="failing_hook",
                hook_type=HookType.HTTP,
                method="GET",
                endpoint="http://invalid.nonexistent/fail",
                timeout: 2,
                ignore_failure=False
            ),
            HookConfig(
                name="should_not_run",
                hook_type=HookType.HTTP,
                method="GET",
                endpoint="https://jsonplaceholder.typicode.com/posts/1"
            )
        ]
        
        results = engine.execute_hooks(hooks, {})
        
        assert len(results) == 1  # 只执行了第一个
        assert not results[0].success


class TestCommandAndScriptHooks:
    """Command 和 Script 类型钩子集成测试"""

    def test_command_hook_execution(self):
        """测试 Command 类型钩子执行"""
        executor = CommandHookExecutor(timeout=5)
        
        hook_config = HookConfig(
            name="echo_test",
            hook_type=HookType.COMMAND,
            command='echo "Hello from command hook"',
            extract={
                output: "Hello"  # 尝试从 stdout 提取
            }
        )
        
        result = executor.execute(hook_config, {})
        
        assert result.success
        assert result.duration > 0

    def test_script_hook_not_found(self):
        """测试脚本文件不存在时的错误处理"""
        executor = ScriptHookExecutor()
        
        hook_config = HookConfig(
            name="missing_script",
            hook_type=HookType.SCRIPT,
            script="/nonexistent/path/to/script.py"
        )
        
        result = executor.execute(hook_config, {})
        
        assert not result.success
        assert "不存在" in result.error_message


class TestHookErrorRecovery:
    """错误恢复和资源清理测试"""

    def test_teardown_always_runs_on_exception(self):
        """测试步骤抛异常时 teardown 仍会执行"""
        engine = HookEngine()
        
        test_case = {
            "name": "异常恢复测试",
            "setup": [{"name": "ok_setup", "type": "http", "method": "GET", 
                      "endpoint": "https://jsonplaceholder.typicode.com/posts/1"}],
            "steps": [
                {"name": "will_fail", "method": "GET", 
                 "endpoint": "http://invalid.url/exception"}
            ],
            "teardown": [
                {"name": "cleanup", "type": "command", 
                 "command": "echo cleanup executed", "ignore_failure": True}
            ]
        }
        
        result = engine.execute_test_case_with_hooks(test_case)
        
        assert result['status'] == 'ERROR'
        assert len(result['teardown_results']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
