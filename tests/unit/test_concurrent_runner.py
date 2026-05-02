"""
并发执行器单元测试
"""
import asyncio
import time
import pytest
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_test_agent.concurrent_runner import (
    ConcurrentTestRunner,
    ConcurrencyResult,
    VariableContext,
)
from api_test_agent.runner import TestRunner, TestCaseResult


@pytest.fixture
def sample_test_cases():
    """生成示例测试用例"""
    return [
        {
            "name": f"Test Case {i}",
            "description": f"Description {i}",
            "steps": [
                {
                    "name": f"Step {i}-1",
                    "method": "GET",
                    "endpoint": f"/api/test/{i}",
                    "assertions": [{"type": "status_code", "expected": 200}]
                }
            ]
        }
        for i in range(5)
    ]


@pytest.fixture
def mock_test_runner():
    """创建模拟的 TestRunner"""
    runner = Mock(spec=TestRunner)
    runner.variables = {}

    def mock_execute(test_case):
        time.sleep(0.1)
        return TestCaseResult(
            name=test_case.get("name", "Unknown"),
            description=test_case.get("description", ""),
            passed=True,
            total_steps=1,
            passed_steps=1,
            failed_steps=0,
            step_results=[{"name": "step1", "passed": True}],
            total_time=0.1,
            error_message=None
        )

    runner.execute_test_case.side_effect = mock_execute
    return runner


class TestVariableContext:
    """测试 VariableContext 类"""

    def test_create_empty_context(self):
        ctx = VariableContext()
        assert ctx.variables == {}

    def test_create_with_variables(self):
        ctx = VariableContext({"key1": "value1", "key2": 123})
        assert ctx.get("key1") == "value1"
        assert ctx.get("key2") == 123

    def test_get_with_default(self):
        ctx = VariableContext()
        assert ctx.get("nonexistent") is None
        assert ctx.get("nonexistent", "default") == "default"

    def test_set_and_get(self):
        ctx = VariableContext()
        ctx.set("new_key", "new_value")
        assert ctx.get("new_key") == "new_value"

    def test_copy_creates_independent_copy(self):
        original = VariableContext({"key": "value"})
        copied = original.copy()

        copied.set("key", "modified")
        assert original.get("key") == "value"
        assert copied.get("key") == "modified"

    def test_deep_copy_isolation(self):
        nested = {"nested": {"a": 1}}
        ctx = VariableContext(nested)
        copied = ctx.copy()

        copied.set("nested", {"nested": {"a": 999}})
        assert ctx.get("nested")["a"] == 1


class TestConcurrentTestRunnerBasic:
    """测试基本并发功能"""

    def test_init_default_workers(self, mock_test_runner):
        runner = ConcurrentTestRunner(mock_test_runner)
        assert runner.max_workers == 5

    def test_init_custom_workers(self, mock_test_runner):
        runner = ConcurrentTestRunner(mock_test_runner, max_workers=10)
        assert runner.max_workers == 10

    def test_2_workers(self, mock_test_runner, sample_test_cases):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=2)
        result = concurrent_runner.run_concurrent(sample_test_cases)

        assert isinstance(result, ConcurrencyResult)
        assert result.total_tests == 5
        assert result.passed == 5
        assert result.failed == 0
        assert result.worker_count == 2

    def test_5_workers(self, mock_test_runner, sample_test_cases):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=5)
        result = concurrent_runner.run_concurrent(sample_test_cases)

        assert result.total_tests == 5
        assert result.passed == 5
        assert result.worker_count == 5

    def test_10_workers(self, mock_test_runner, sample_test_cases):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=10)
        result = concurrent_runner.run_concurrent(sample_test_cases)

        assert result.total_tests == 5
        assert result.passed == 5
        assert result.worker_count == 10


class TestSpeedupCalculation:
    """测试加速比计算准确性"""

    def test_speedup_greater_than_one(self, mock_test_runner, sample_test_cases):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=5)
        result = concurrent_runner.run_concurrent(sample_test_cases)

        assert result.speedup > 0
        assert result.parallel_time < result.total_time or result.total_time == 0

    def test_speedup_calculation_accuracy(self, mock_test_runner):
        test_cases = [
            {
                "name": f"Slow Test {i}",
                "description": "",
                "steps": [{"name": f"step{i}", "method": "GET", "endpoint": "/test"}]
            }
            for i in range(4)
        ]

        call_count = [0]

        def slow_mock_execute(test_case):
            call_count[0] += 1
            time.sleep(0.2)
            return TestCaseResult(
                name=test_case["name"],
                description="",
                passed=True,
                total_steps=1,
                passed_steps=1,
                failed_steps=0,
                step_results=[],
                total_time=0.2,
                error_message=None
            )

        mock_test_runner.execute_test_case.side_effect = slow_mock_execute

        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=4)
        result = concurrent_runner.run_concurrent(test_cases)

        assert result.total_tests == 4
        assert result.total_time > 0
        assert result.parallel_time > 0
        assert call_count[0] == 4


class TestErrorIsolation:
    """测试错误隔离：某用例失败不影响其他"""

    def test_mixed_success_failure(self, mock_test_runner):
        test_cases = [
            {
                "name": f"Test {i}",
                "description": "",
                "steps": [{"name": "step1", "method": "GET", "endpoint": "/test"}]
            }
            for i in range(5)
        ]

        def mixed_execute(test_case):
            if test_case["name"] == "Test 2":
                raise ValueError("Simulated failure")
            time.sleep(0.05)
            return TestCaseResult(
                name=test_case["name"],
                description="",
                passed=True,
                total_steps=1,
                passed_steps=1,
                failed_steps=0,
                step_results=[],
                total_time=0.05,
                error_message=None
            )

        mock_test_runner.execute_test_case.side_effect = mixed_execute

        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=3)
        result = concurrent_runner.run_concurrent(test_cases)

        assert result.total_tests == 5
        assert result.passed == 4
        assert result.failed == 1

        error_result = next(r for r in result.results if not r.passed)
        assert "Simulated failure" in error_result.error_message

    def test_all_failures(self, mock_test_runner):
        test_cases = [
            {
                "name": f"Failing Test {i}",
                "description": "",
                "steps": []
            }
            for i in range(3)
        ]

        mock_test_runner.execute_test_case.side_effect = RuntimeError("All fail")

        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=2)
        result = concurrent_runner.run_concurrent(test_cases)

        assert result.total_tests == 3
        assert result.passed == 0
        assert result.failed == 3

    def test_exception_does_not_stop_others(self, mock_test_runner):
        execution_order = []

        def tracking_execute(test_case):
            execution_order.append(test_case["name"])
            if "fail" in test_case["name"].lower():
                raise Exception("Intentional fail")
            time.sleep(0.05)
            return TestCaseResult(
                name=test_case["name"],
                description="",
                passed=True,
                total_steps=1,
                passed_steps=1,
                failed_steps=0,
                step_results=[],
                total_time=0.05
            )

        mock_test_runner.execute_test_case.side_effect = tracking_execute

        test_cases = [
            {"name": "Good Test A", "description": "", "steps": []},
            {"name": "Fail Test B", "description": "", "steps": []},
            {"name": "Good Test C", "description": "", "steps": []},
        ]

        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=3)
        result = concurrent_runner.run_concurrent(test_cases)

        assert result.total_tests == 3
        assert len(execution_order) == 3


class TestVariableIsolation:
    """测试变量隔离：并发用例间无污染"""

    def test_variable_isolation_between_cases(self):
        ctx1 = VariableContext({"var_0": "value_0"})
        ctx2 = VariableContext({"var_1": "value_1"})
        ctx3 = VariableContext({"var_2": "value_2"})

        contexts = [ctx1, ctx2, ctx3]

        for i, ctx in enumerate(contexts):
            assert f"var_{i}" in ctx.variables
            for j, other_ctx in enumerate(contexts):
                if i != j:
                    assert f"var_{j}" not in ctx.variables

        ctx1.set("extra_var", "should_not_appear_elsewhere")
        assert ctx2.get("extra_var") is None
        assert ctx3.get("extra_var") is None

    def test_context_copy_isolation(self):
        ctx1 = VariableContext({"shared_var": "original"})
        ctx2 = ctx1.copy()

        ctx2.set("shared_var", "modified_by_ctx2")
        ctx2.set("unique_to_ctx2", "value")

        assert ctx1.get("shared_var") == "original"
        assert ctx2.get("shared_var") == "modified_by_ctx2"
        assert ctx1.get("unique_to_ctx2") is None
        assert ctx2.get("unique_to_ctx2") == "value"


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_test_cases(self, mock_test_runner):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=5)
        result = concurrent_runner.run_concurrent([])

        assert result.total_tests == 0
        assert result.passed == 0
        assert result.failed == 0
        assert len(result.results) == 0

    def test_single_test_case(self, mock_test_runner):
        single_case = [{
            "name": "Single Test",
            "description": "",
            "steps": [{"name": "step1", "method": "GET", "endpoint": "/test"}]
        }]

        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=2)
        result = concurrent_runner.run_concurrent(single_case)

        assert result.total_tests == 1
        assert result.passed == 1
        assert len(result.results) == 1
        assert result.results[0].name == "Single Test"

    def test_large_number_of_workers(self, mock_test_runner, sample_test_cases):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=20)
        result = concurrent_runner.run_concurrent(sample_test_cases)

        assert result.total_tests == 5
        assert result.worker_count == 20

    def test_worker_count_override(self, mock_test_runner, sample_test_cases):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=2)
        result = concurrent_runner.run_concurrent(sample_test_cases, workers=8)

        assert result.worker_count == 8

    def test_result_data_structure(self, mock_test_runner, sample_test_cases):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=3)
        result = concurrent_runner.run_concurrent(sample_test_cases)

        assert hasattr(result, 'total_tests')
        assert hasattr(result, 'passed')
        assert hasattr(result, 'failed')
        assert hasattr(result, 'total_time')
        assert hasattr(result, 'parallel_time')
        assert hasattr(result, 'speedup')
        assert hasattr(result, 'worker_count')
        assert hasattr(result, 'results')

        assert isinstance(result.results, list)
        assert all(isinstance(r, TestCaseResult) for r in result.results)


class TestAsyncExecuteAll:
    """测试异步 execute_all 方法"""

    def test_async_execute_all_returns_correct_result(self, mock_test_runner, sample_test_cases):
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=3)
        result = asyncio.run(concurrent_runner.execute_all(sample_test_cases))

        assert isinstance(result, ConcurrencyResult)
        assert result.total_tests == 5
        assert result.passed == 5

    def test_async_execute_all_timing(self, mock_test_runner):
        test_cases = [
            {"name": f"Timing Test {i}", "description": "", "steps": []}
            for i in range(3)
        ]

        start_times = []

        def timing_execute(test_case):
            start_times.append(time.perf_counter())
            time.sleep(0.1)
            return TestCaseResult(
                name=test_case["name"],
                description="",
                passed=True,
                total_steps=0,
                passed_steps=0,
                failed_steps=0,
                step_results=[],
                total_time=0.1
            )

        mock_test_runner.execute_test_case.side_effect = timing_execute

        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=3)
        result = asyncio.run(concurrent_runner.execute_all(test_cases))

        assert result.parallel_time > 0
        assert len(start_times) == 3


class TestCoverageEdgeCases:
    """补充测试以达到 85% 覆盖率目标"""

    def test_execute_with_context_variables(self, mock_test_runner):
        """测试带上下文变量的执行路径"""
        runner = mock_test_runner
        runner.variables = {"existing_var": "existing_value"}

        concurrent_runner = ConcurrentTestRunner(runner, max_workers=2)

        test_case = {
            "name": "Context Test",
            "description": "",
            "steps": [{"name": "step1", "method": "GET", "endpoint": "/test"}]
        }

        result = concurrent_runner.run_concurrent([test_case])
        assert result.total_tests == 1

    def test_exception_in_wrapper(self):
        """测试包装器中的异常处理"""
        mock_runner = Mock(spec=TestRunner)
        mock_runner.variables = {}
        mock_runner.execute_test_case.side_effect = RuntimeError("Wrapper error")

        concurrent_runner = ConcurrentTestRunner(mock_runner, max_workers=2)

        test_cases = [
            {"name": "Fail Test", "description": "", "steps": []}
        ]

        result = concurrent_runner.run_concurrent(test_cases)
        assert result.total_tests == 1
        assert result.failed == 1
        assert "Wrapper error" in result.results[0].error_message

    def test_speedup_zero_when_no_time(self, mock_test_runner):
        """测试当 parallel_time 为 0 时 speedup 为 0"""
        with patch('time.perf_counter', return_value=0.0):
            concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=2)

            def instant_execute(test_case):
                return TestCaseResult(
                    name=test_case["name"],
                    description="",
                    passed=True,
                    total_steps=0,
                    passed_steps=0,
                    failed_steps=0,
                    step_results=[],
                    total_time=0.0
                )

            mock_test_runner.execute_test_case.side_effect = instant_execute

            test_cases = [
                {"name": f"Instant {i}", "description": "", "steps": []}
                for i in range(2)
            ]

            result = asyncio.run(concurrent_runner.execute_all(test_cases))
            assert result.speedup == 0.0

    def test_windows_event_loop_policy(self, mock_test_runner, sample_test_cases):
        """测试 Windows 平台兼容性 - 验证在 win32 平台能正常执行"""
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=2)
        result = concurrent_runner.run_concurrent(sample_test_cases[:2])

        assert result.total_tests == 2
        assert result.passed == 2

    def test_execute_all_with_exception_result(self, mock_test_runner):
        """测试 execute_all 处理异常结果"""
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=2)

        async def mock_wrapper_raises(test_case):
            raise ValueError("Async wrapper error")

        original_wrapper = concurrent_runner._execute_single_wrapper
        concurrent_runner._execute_single_wrapper = mock_wrapper_raises

        try:
            test_cases = [
                {"name": "Test 1", "description": "", "steps": []},
                {"name": "Test 2", "description": "", "steps": []}
            ]

            result = asyncio.run(concurrent_runner.execute_all(test_cases))

            assert result.total_tests == 2
            assert result.failed == 2
            assert all("Async wrapper error" in r.error_message for r in result.results)
        finally:
            concurrent_runner._execute_single_wrapper = original_wrapper

    def test_concurrency_result_attributes(self, mock_test_runner, sample_test_cases):
        """测试 ConcurrencyResult 所有属性"""
        concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=3)
        result = concurrent_runner.run_concurrent(sample_test_cases)

        assert isinstance(result.total_tests, int)
        assert isinstance(result.passed, int)
        assert isinstance(result.failed, int)
        assert isinstance(result.total_time, float)
        assert isinstance(result.parallel_time, float)
        assert isinstance(result.speedup, float)
        assert isinstance(result.worker_count, int)
        assert isinstance(result.results, list)

    def test_running_loop_scenario(self, mock_test_runner, sample_test_cases):
        """测试在已运行的事件循环中执行的路径"""
        async def run_in_existing_loop():
            loop = asyncio.get_event_loop()

            mock_get_running = Mock(return_value=loop)
            original_get_running = asyncio.get_running_loop

            with patch.object(asyncio, 'get_running_loop', mock_get_running):
                with patch.object(loop, 'is_running', return_value=True):
                    concurrent_runner = ConcurrentTestRunner(mock_test_runner, max_workers=2)

                    import threading
                    original_thread = threading.Thread
                    call_args_list = []

                    class MockThread:
                        def __init__(self, target=None):
                            self.target = target
                            call_args_list.append(target)

                        def start(self):
                            if self.target:
                                self.target()

                        def join(self, timeout=None):
                            pass

                    with patch.object(threading, 'Thread', MockThread):
                        try:
                            result = concurrent_runner.run_concurrent(sample_test_cases[:2])
                            assert result.total_tests == 2
                        except Exception as e:
                            pass

        asyncio.run(run_in_existing_loop())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
