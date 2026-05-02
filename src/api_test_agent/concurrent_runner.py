"""
API 接口自动化测试 Agent - 并发执行器
"""
import asyncio
import sys
import time
import copy
import logging
from dataclasses import dataclass, field
from typing import List, Any, Optional, Dict
from concurrent.futures import ThreadPoolExecutor

from .runner import TestRunner, TestCaseResult


class VariableContext:
    """变量上下文，用于隔离并发测试用例的变量"""

    def __init__(self, variables: Dict[str, Any] = None):
        self.variables = variables or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def set(self, key: str, value: Any):
        self.variables[key] = value

    def copy(self) -> 'VariableContext':
        return VariableContext(copy.deepcopy(self.variables))

    def __repr__(self) -> str:
        return f"VariableContext({self.variables})"


@dataclass
class ConcurrencyResult:
    """并发测试执行结果"""
    total_tests: int
    passed: int
    failed: int
    total_time: float
    parallel_time: float
    speedup: float
    worker_count: int
    results: List[TestCaseResult] = field(default_factory=list)


class ConcurrentTestRunner:
    """并发测试执行器"""

    def __init__(self, test_runner: TestRunner, max_workers: int = 5):
        self.test_runner = test_runner
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        self.logger = logging.getLogger("ConcurrentTestRunner")

    async def _execute_single_wrapper(self, test_case: Dict) -> TestCaseResult:
        """异步包装器：在信号量控制下执行单个测试用例"""
        async with self.semaphore:
            loop = asyncio.get_event_loop()

            original_variables = copy.deepcopy(self.test_runner.variables)
            context = VariableContext(original_variables)

            try:
                result = await loop.run_in_executor(
                    None,
                    self._sync_execute_with_context,
                    test_case,
                    context
                )
                return result
            except Exception as e:
                self.logger.error(f"测试用例执行异常: {e}")
                return TestCaseResult(
                    name=test_case.get("name", "Unknown"),
                    description=test_case.get("description", ""),
                    passed=False,
                    total_steps=0,
                    passed_steps=0,
                    failed_steps=0,
                    step_results=[],
                    total_time=0.0,
                    error_message=str(e)
                )
            finally:
                pass

    def _sync_execute_with_context(self, test_case: Dict, context: VariableContext) -> TestCaseResult:
        """在线程池中同步执行测试用例（带上下文隔离）"""
        saved_vars = copy.deepcopy(self.test_runner.variables)

        try:
            if context.variables:
                self.test_runner.variables = copy.deepcopy(context.variables)

            result = self.test_runner.execute_test_case(test_case)
            return result
        finally:
            self.test_runner.variables = saved_vars

    async def execute_all(self, test_cases: List[Dict]) -> ConcurrencyResult:
        """并发执行所有测试用例"""
        start_time = time.perf_counter()

        tasks = [asyncio.create_task(self._execute_single_wrapper(tc)) for tc in test_cases]

        results_raw = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for item in results_raw:
            if isinstance(item, Exception):
                results.append(TestCaseResult(
                    name="Error",
                    description="",
                    passed=False,
                    total_steps=0,
                    passed_steps=0,
                    failed_steps=1,
                    step_results=[],
                    total_time=0.0,
                    error_message=str(item)
                ))
            elif isinstance(item, TestCaseResult):
                results.append(item)
            else:
                results.append(TestCaseResult(
                    name="Unknown",
                    description="",
                    passed=False,
                    total_steps=0,
                    passed_steps=0,
                    failed_steps=1,
                    step_results=[],
                    total_time=0.0,
                    error_message=f"Unexpected result type: {type(item)}"
                ))

        end_time = time.perf_counter()
        parallel_time = end_time - start_time

        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed

        serial_time_estimate = sum(r.total_time for r in results)
        speedup = round(serial_time_estimate / parallel_time, 2) if parallel_time > 0 else 0.0

        return ConcurrencyResult(
            total_tests=len(results),
            passed=passed,
            failed=failed,
            total_time=round(serial_time_estimate, 3),
            parallel_time=round(parallel_time, 3),
            speedup=speedup,
            worker_count=self.max_workers,
            results=results
        )

    def run_concurrent(self, test_cases: List[Dict], workers: int = None) -> ConcurrencyResult:
        """同步入口方法：运行并发测试"""
        if workers is not None:
            self.max_workers = workers
            self.semaphore = asyncio.Semaphore(workers)

        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import threading
            result_container = []

            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(self.execute_all(test_cases))
                    result_container.append(result)
                finally:
                    new_loop.close()

            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join(timeout=300)

            if result_container:
                return result_container[0]
            else:
                raise RuntimeError("Concurrent execution timeout")
        else:
            return asyncio.run(self.execute_all(test_cases))
