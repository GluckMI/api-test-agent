"""
API Test Agent v2.0 - 性能测试执行器

支持负载测试模式：
- RPS 控制（每秒请求数限制）
- 持续时间控制
- 并发用户模拟
- 实时指标监控
"""
import time
import threading
import logging
import math
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from .client import APIClient
from .perf_collector import PerfCollector, PerfMetrics


@dataclass
class LoadTestConfig:
    """负载测试配置"""
    endpoint: str
    method: str = "GET"
    params: Dict = field(default_factory=dict)
    headers: Dict = field(default_factory=dict)
    json_data: Any = None
    data: Any = None
    
    # 性能测试参数
    duration: float = 60.0  # 测试持续时间（秒）
    rps: Optional[float] = None  # 目标 RPS（None 表示不限速）
    concurrent_users: int = 10  # 并发用户数
    ramp_up_time: float = 0.0  # 爬坡时间（秒）
    
    # 阈值配置
    thresholds: List[Dict] = field(default_factory=list)


@dataclass
class LoadTestResult:
    """负载测试结果"""
    config: LoadTestConfig
    metrics: PerfMetrics
    actual_duration: float
    actual_rps: float
    total_requests: int
    errors: List[str] = field(default_factory=list)


class RateLimiter:
    """速率限制器 - 用于控制 RPS"""
    
    def __init__(self, max_rps: float):
        self.max_rps = max_rps
        self.min_interval = 1.0 / max_rps  # 最小请求间隔
        self.last_request_time = 0.0
        self.lock = threading.Lock()
    
    def wait(self):
        """等待直到可以发送下一个请求"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_request_time
            
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()


class LoadTester:
    """负载测试执行器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = logging.getLogger("LoadTester")
        self.collector = PerfCollector()
        self.stop_flag = threading.Event()
    
    def run_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """
        执行负载测试
        
        Args:
            config: 负载测试配置
        
        Returns:
            LoadTestResult 测试结果
        """
        self.logger.info(f"开始负载测试: {config.method} {config.endpoint}")
        self.logger.info(f"配置: duration={config.duration}s, rps={config.rps}, users={config.concurrent_users}")
        
        # 初始化收集器
        self.collector.start_collection()
        self.collector.set_thresholds(config.thresholds)
        self.stop_flag.clear()
        
        # 创建速率限制器
        rate_limiter = RateLimiter(config.rps) if config.rps else None
        
        # 执行测试
        start_time = time.time()
        total_requests = [0]  # 使用列表以便在线程中修改
        errors = []
        error_lock = threading.Lock()
        
        def worker_task(worker_id: int):
            """Worker 线程任务"""
            client = APIClient(base_url=self.base_url)
            request_count = 0
            
            try:
                while not self.stop_flag.is_set():
                    # 检查持续时间
                    elapsed = time.time() - start_time
                    if elapsed >= config.duration:
                        break
                    
                    # RPS 控制
                    if rate_limiter:
                        rate_limiter.wait()
                    
                    # 发送请求并记录性能
                    req_start = time.time()
                    try:
                        method_func = getattr(client, config.method.lower())
                        response = method_func(
                            endpoint=config.endpoint,
                            params=config.params,
                            headers=config.headers,
                            json_data=config.json_data,
                            data=config.data
                        )
                        
                        req_end = time.time()
                        response_time = req_end - req_start
                        
                        self.collector.record_request(
                            endpoint=config.endpoint,
                            method=config.method,
                            response_time=response_time,
                            status_code=response.status_code,
                            success=response.success,
                            error_message=response.error_message,
                            response_size=len(response.text) if hasattr(response, 'text') and response.text else 0
                        )
                        
                        request_count += 1
                        
                    except Exception as e:
                        req_end = time.time()
                        response_time = req_end - req_start
                        
                        self.collector.record_request(
                            endpoint=config.endpoint,
                            method=config.method,
                            response_time=response_time,
                            status_code=0,
                            success=False,
                            error_message=str(e)
                        )
                        
                        with error_lock:
                            errors.append(f"Worker {worker_id}: {str(e)}")
            
            finally:
                client.close()
                total_requests[0] += request_count
        
        # 启动并发 Workers
        with ThreadPoolExecutor(max_workers=config.concurrent_users) as executor:
            futures = []
            
            # 如果使用爬坡模式，逐渐增加并发用户
            if config.ramp_up_time > 0:
                self._run_ramp_up(executor, config, worker_task, futures)
            else:
                for i in range(config.concurrent_users):
                    future = executor.submit(worker_task, i)
                    futures.append(future)
            
            # 等待持续时间结束或所有任务完成
            try:
                time.sleep(config.duration)
            except KeyboardInterrupt:
                self.logger.info("收到中断信号，停止测试")
            
            self.stop_flag.set()
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result(timeout=5)
                except Exception as e:
                    self.logger.error(f"Worker 异常: {e}")
        
        # 停止收集
        self.collector.stop_collection()
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # 计算指标
        metrics = self.collector.calculate_metrics()
        
        result = LoadTestResult(
            config=config,
            metrics=metrics,
            actual_duration=actual_duration,
            actual_rps=total_requests[0] / actual_duration if actual_duration > 0 else 0,
            total_requests=total_requests[0],
            errors=errors
        )
        
        self.logger.info(f"负载测试完成: {total_requests[0]} 请求, {actual_duration:.2f}s, {result.actual_rps:.2f} RPS")
        
        return result
    
    def _run_ramp_up(self, executor: ThreadPoolExecutor, config: LoadTestConfig,
                    worker_task: Callable, futures: List):
        """爬坡模式 - 逐渐增加并发用户"""
        ramp_steps = min(10, config.concurrent_users)
        users_per_step = max(1, config.concurrent_users // ramp_steps)
        ramp_interval = config.ramp_up_time / ramp_steps
        
        current_users = 0
        for step in range(ramp_steps):
            if self.stop_flag.is_set():
                break
            
            for i in range(users_per_step):
                if current_users >= config.concurrent_users:
                    break
                future = executor.submit(worker_task, current_users)
                futures.append(future)
                current_users += 1
            
            if step < ramp_steps - 1:
                time.sleep(ramp_interval)
    
    def run_single_endpoint_perf_test(self, endpoint: str, method: str = "GET",
                                     iterations: int = 100, **kwargs) -> PerfMetrics:
        """
        对单个端点进行性能测试（固定次数模式）
        
        Args:
            endpoint: API 端点
            method: HTTP 方法
            iterations: 执行次数
            **kwargs: 传递给请求的参数
        
        Returns:
            PerfMetrics 性能指标
        """
        self.logger.info(f"开始性能测试: {method} {endpoint} ({iterations} 次迭代)")
        
        self.collector.start_collection()
        client = APIClient(base_url=self.base_url)
        
        try:
            for i in range(iterations):
                req_start = time.time()
                try:
                    method_func = getattr(client, method.lower())
                    response = method_func(endpoint=endpoint, **kwargs)
                    req_end = time.time()
                    
                    self.collector.record_request(
                        endpoint=endpoint,
                        method=method,
                        response_time=req_end - req_start,
                        status_code=response.status_code,
                        success=response.success,
                        error_message=response.error_message,
                        response_size=len(response.text) if hasattr(response, 'text') and response.text else 0
                    )
                except Exception as e:
                    req_end = time.time()
                    self.collector.record_request(
                        endpoint=endpoint,
                        method=method,
                        response_time=req_end - req_start,
                        status_code=0,
                        success=False,
                        error_message=str(e)
                    )
        finally:
            client.close()
            self.collector.stop_collection()
        
        return self.collector.calculate_metrics()
