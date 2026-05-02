"""
并发执行器模块集成测试

覆盖范围：
- 并发执行模式（-w 参数）
- 结果聚合正确性
- 加速比计算验证
- 变量隔离性
- 并发错误处理

注意：
- 并发测试可能受限于系统资源
- 使用较小的 worker 数量避免资源耗尽
"""
import os
import sys
import time
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api_test_agent.concurrent_runner import ConcurrentTestRunner, ConcurrencyResult, VariableContext
from api_test_agent.runner import TestRunner, TestCaseResult


class TestConcurrencyBasicExecution:
    """并发执行基本功能测试"""

    def test_sequential_execution_single_worker(self):
        """测试单工作线程（串行）执行"""
        runner = TestRunner(base_url="https://jsonplaceholder.typicode.com")
        concurrent = ConcurrentTestRunner(runner, max_workers=1)
        
        async def run_tests():
            test_cases = [
                {"name": "Test 1", "steps": [
                    {"name": "Get Post 1", "method": "GET", "endpoint": "/posts/1",
                     "assertions": [{"type": "status_code", "expected": 200}]}
                ]},
                {"name": "Test 2", "steps": [
                    {"name": "Get User 1", "method": "GET", "endpoint": "/users/1",
                     "assertions": [{"type": "status_code", "expected": 200}]}
                ]}
            ]
            
            results = await asyncio.gather(*[
                concurrent._execute_single_wrapper(case) for case in test_cases
            ])
            
            return results
        
        results = asyncio.run(run_tests())
        
        assert len(results) == 2
        for result in results:
            assert isinstance(result, TestCaseResult)

    def test_parallel_execution_multiple_workers(self):
        """测试多工作线程并行执行"""
        runner = TestRunner(base_url="https://jsonplaceholder.typicode.com")
        concurrent = ConcurrentTestRunner(runner, max_workers=3)
        
        async def run_tests():
            test_cases = [
                {"name": f"Test {i}", "steps": [
                    {"name": f"Get Resource {i}", "method": "GET", 
                     "endpoint": f"/posts/{i+1}",
                     "assertions": [{"type": "status_code", "expected": 200}]}
                ]} for i in range(5)
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*[
                concurrent._execute_single_wrapper(case) for case in test_cases
            ])
            elapsed = time.time() - start_time
            
            return results, elapsed
        
        results, elapsed = asyncio.run(run_tests())
        
        assert len(results) == 5
        assert all(isinstance(r, TestCaseResult) for r in results)


class TestConcurrencyResultAggregation:
    """结果聚合和统计测试"""

    def test_result_aggregation_correctness(self):
        """测试结果聚合的正确性"""
        total_tests = 10
        passed_count = 7
        failed_count = 3
        
        mock_results = []
        for i in range(total_tests):
            passed = i < passed_count
            mock_results.append(TestCaseResult(
                name=f"Test {i}",
                description=f"Description {i}",
                passed=passed,
                total_steps=3,
                passed_steps=3 if passed else 1,
                failed_steps=0 if passed else 2,
                error_steps=0,
                duration=0.5 + i * 0.1,
                error_message=None if passed else "Assertion failed"
            ))
        
        start_time = time.time() - 5.0
        parallel_time = 2.0
        
        result = ConcurrencyResult(
            total_tests=total_tests,
            passed=passed_count,
            failed=failed_count,
            total_time=start_time + parallel_time,
            parallel_time=parallel_time,
            speedup=(start_time + parallel_time) / parallel_time if parallel_time > 0 else 1.0,
            worker_count=4,
            results=mock_results
        )
        
        assert result.total_tests == total_tests
        assert result.passed == passed_count
        assert result.failed == failed_count
        assert len(result.results) == total_tests
        assert result.worker_count == 4
        assert result.speedup > 1.0  # 应该有加速效果

    def test_speedup_calculation(self):
        """测试加速比计算"""
        serial_time = 10.0
        parallel_time = 3.0
        expected_speedup = serial_time / parallel_time
        
        result = ConcurrencyResult(
            total_tests=5,
            passed=5,
            failed=0,
            total_time=serial_time,
            parallel_time=parallel_time,
            speedup=expected_speedup,
            worker_count=3,
            results=[]
        )
        
        assert abs(result.speedup - expected_speedup) < 0.001
        assert result.speedup > 1.0


class TestVariableIsolation:
    """变量上下文隔离测试"""

    def test_variable_context_isolation(self):
        """测试不同测试用例的变量相互隔离"""
        ctx1 = VariableContext({"var1": "value1", "shared": "original"})
        ctx2 = ctx1.copy()
        
        ctx2.set("var2", "value2")
        ctx2.set("shared", "modified")
        
        assert ctx1.get("var1") == "value1"
        assert ctx1.get("var2") is None
        assert ctx1.get("shared") == "original"
        
        assert ctx2.get("var1") == "value1"
        assert ctx2.get("var2") == "value2"
        assert ctx2.get("shared") == "modified"

    def test_concurrent_variable_independence(self):
        """测试并发执行时变量的独立性"""
        contexts = []
        
        def create_context(index):
            ctx = VariableContext({"index": index, "unique_var": f"value_{index}"})
            contexts.append(ctx)
            return ctx
        
        for i in range(5):
            create_context(i)
        
        for i, ctx in enumerate(contexts):
            assert ctx.get("index") == i
            assert ctx.get("unique_var") == f"value_{i}"


class TestConcurrencyErrorHandling:
    """并发错误处理测试"""

    def test_partial_failure_handling(self):
        """测试部分用例失败的处理"""
        runner = TestRunner(base_url="https://jsonplaceholder.typicode.com")
        concurrent = ConcurrentTestRunner(runner, max_workers=2)
        
        async def run_mixed_tests():
            test_cases = [
                {"name": "Success Case", "steps": [
                    {"name": "Valid Request", "method": "GET", "endpoint": "/posts/1",
                     "assertions": [{"type": "status_code", "expected": 200}]}
                ]},
                {"name": "Failure Case", "steps": [
                    {"name": "Invalid Assertion", "method": "GET", "endpoint": "/posts/1",
                     "assertions": [{"type": "status_code", "expected": 999}]}
                ]},
                {"name": "Another Success", "steps": [
                    {"name": "Another Valid", "method": "GET", "endpoint": "/users/1",
                     "assertions": [{"type": "status_code", "expected": 200}]}
                ]}
            ]
            
            results = await asyncio.gather(*[
                concurrent._execute_single_wrapper(case) for case in test_cases
            ], return_exceptions=True)
            
            return results
        
        results = asyncio.run(run_mixed_tests())
        
        assert len(results) == 3
        success_count = sum(1 for r in results if isinstance(r, TestCaseResult) and r.passed)
        fail_count = sum(1 for r in results if isinstance(r, TestCaseResult) and not r.passed)
        
        assert success_count >= 1
        assert fail_count >= 1


class TestWorkerCountScaling:
    """工作线程数扩展性测试"""

    def test_different_worker_counts(self):
        """测试不同工作线程数的影响"""
        runner = TestRunner(base_url="https://jsonplaceholder.typicode.com")
        
        test_case = {
            "name": "Simple Test",
            "steps": [{
                "name": "Get Post", "method": "GET", "endpoint": "/posts/1",
                "assertions": [{"type": "status_code", "expected": 200}]
            }]
        }
        
        for workers in [1, 2, 4]:
            concurrent = ConcurrentTestRunner(runner, max_workers=workers)
            
            async def single_run():
                result = await concurrent._execute_single_wrapper(test_case)
                return result
            
            result = asyncio.run(single_run())
            assert isinstance(result, TestCaseResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
