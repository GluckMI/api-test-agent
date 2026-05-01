"""
API Test Agent v2.0 - 性能指标收集器

负责收集和计算性能测试指标：
- 响应时间分布（P50/P90/P95/P99）
- 吞吐量（RPS）
- 错误率
- 阈值告警
"""
import math
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class RequestRecord:
    """单次请求的性能记录"""
    timestamp: float
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    response_size: int = 0


@dataclass
class ThresholdConfig:
    """性能阈值配置"""
    name: str
    metric: str  # 'p95', 'p99', 'error_rate', 'avg', 'rps'
    operator: str  # '<', '<=', '>', '>=', '=='
    value: float
    severity: str = 'warning'  # 'warning' or 'critical'


@dataclass
class ThresholdViolation:
    """阈值违规记录"""
    threshold: ThresholdConfig
    actual_value: float
    message: str
    timestamp: str = ""


@dataclass
class PerfMetrics:
    """性能指标汇总"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time: float = 0.0
    start_time: str = ""
    end_time: str = ""
    
    # 响应时间指标
    response_times: List[float] = field(default_factory=list)
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    avg_response_time: float = 0.0
    median_response_time: float = 0.0
    p90_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # 吞吐量指标
    rps: float = 0.0  # Requests Per Second
    throughput: float = 0.0  # bytes per second
    
    # 错误指标
    error_rate: float = 0.0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    # 状态码分布
    status_code_distribution: Dict[int, int] = field(default_factory=dict)
    
    # 端点性能
    endpoint_metrics: Dict[str, Dict] = field(default_factory=dict)
    
    # 阈值违规
    threshold_violations: List[ThresholdViolation] = field(default_factory=list)
    
    # 时间序列数据（用于趋势图）
    time_series: List[Dict] = field(default_factory=list)


class PerfCollector:
    """性能指标收集器"""
    
    def __init__(self):
        self.logger = logging.getLogger("PerfCollector")
        self.records: List[RequestRecord] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.thresholds: List[ThresholdConfig] = []
        self.violations: List[ThresholdViolation] = []
    
    def start_collection(self):
        """开始收集性能指标"""
        self.start_time = time.time()
        self.records.clear()
        self.violations.clear()
    
    def stop_collection(self):
        """停止收集性能指标"""
        self.end_time = time.time()
    
    def record_request(self, endpoint: str, method: str, response_time: float,
                      status_code: int, success: bool, error_message: str = None,
                      response_size: int = 0):
        """
        记录单次请求的性能数据
        
        Args:
            endpoint: API 端点
            method: HTTP 方法
            response_time: 响应时间（秒）
            status_code: HTTP 状态码
            success: 是否成功
            error_message: 错误信息（如果失败）
            response_size: 响应大小（字节）
        """
        record = RequestRecord(
            timestamp=time.time(),
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            success=success,
            error_message=error_message,
            response_size=response_size
        )
        self.records.append(record)
    
    def set_thresholds(self, thresholds: List[Dict]):
        """
        设置性能阈值
        
        Args:
            thresholds: 阈值配置列表，例如：
                [
                    {"metric": "p95", "operator": "<", "value": 2.0, "severity": "critical"},
                    {"metric": "error_rate", "operator": "<", "value": 0.05, "severity": "warning"}
                ]
        """
        self.thresholds.clear()
        for i, t in enumerate(thresholds):
            threshold = ThresholdConfig(
                name=t.get("name", f"threshold_{i}"),
                metric=t["metric"],
                operator=t["operator"],
                value=t["value"],
                severity=t.get("severity", "warning")
            )
            self.thresholds.append(threshold)
    
    def calculate_metrics(self) -> PerfMetrics:
        """
        计算性能指标汇总
        
        Returns:
            PerfMetrics 对象
        """
        metrics = PerfMetrics()
        
        if not self.records:
            return metrics
        
        # 基本信息
        metrics.total_requests = len(self.records)
        metrics.successful_requests = sum(1 for r in self.records if r.success)
        metrics.failed_requests = metrics.total_requests - metrics.successful_requests
        metrics.start_time = datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S") if self.start_time else ""
        metrics.end_time = datetime.fromtimestamp(self.end_time).strftime("%Y-%m-%d %H:%M:%S") if self.end_time else ""
        
        # 响应时间指标
        response_times = sorted([r.response_time for r in self.records])
        metrics.response_times = response_times
        metrics.min_response_time = response_times[0]
        metrics.max_response_time = response_times[-1]
        metrics.avg_response_time = sum(response_times) / len(response_times)
        metrics.median_response_time = self._percentile(response_times, 50)
        metrics.p90_response_time = self._percentile(response_times, 90)
        metrics.p95_response_time = self._percentile(response_times, 95)
        metrics.p99_response_time = self._percentile(response_times, 99)
        
        # 吞吐量指标
        total_duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0
        if total_duration > 0:
            metrics.total_time = total_duration
            metrics.rps = metrics.total_requests / total_duration
            total_bytes = sum(r.response_size for r in self.records)
            metrics.throughput = total_bytes / total_duration
        
        # 错误指标
        metrics.error_rate = metrics.failed_requests / metrics.total_requests if metrics.total_requests > 0 else 0.0
        
        # 错误类型统计
        error_messages = defaultdict(int)
        for r in self.records:
            if not r.success and r.error_message:
                error_messages[r.error_message] += 1
        metrics.errors_by_type = dict(error_messages)
        
        # 状态码分布
        status_codes = defaultdict(int)
        for r in self.records:
            status_codes[r.status_code] += 1
        metrics.status_code_distribution = dict(status_codes)
        
        # 端点性能
        endpoint_data = defaultdict(list)
        for r in self.records:
            endpoint_data[r.endpoint].append(r.response_time)
        
        for endpoint, times in endpoint_data.items():
            times_sorted = sorted(times)
            metrics.endpoint_metrics[endpoint] = {
                "count": len(times),
                "avg": sum(times) / len(times),
                "min": times_sorted[0],
                "max": times_sorted[-1],
                "p95": self._percentile(times_sorted, 95),
                "error_count": sum(1 for r in self.records if r.endpoint == endpoint and not r.success)
            }
        
        # 生成时间序列数据（每秒聚合）
        if self.start_time and self.end_time:
            time_buckets = defaultdict(lambda: {"count": 0, "errors": 0, "total_time": 0.0})
            for r in self.records:
                bucket = int(r.timestamp - self.start_time)
                time_buckets[bucket]["count"] += 1
                time_buckets[bucket]["total_time"] += r.response_time
                if not r.success:
                    time_buckets[bucket]["errors"] += 1
            
            for second in sorted(time_buckets.keys()):
                bucket = time_buckets[second]
                metrics.time_series.append({
                    "second": second,
                    "timestamp": datetime.fromtimestamp(self.start_time + second).strftime("%H:%M:%S"),
                    "requests": bucket["count"],
                    "errors": bucket["errors"],
                    "avg_response_time": bucket["total_time"] / bucket["count"] if bucket["count"] > 0 else 0,
                    "rps": bucket["count"]
                })
        
        # 检查阈值
        if self.thresholds:
            metrics.threshold_violations = self._check_thresholds(metrics)
        
        return metrics
    
    def _percentile(self, sorted_data: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not sorted_data:
            return 0.0
        
        k = (len(sorted_data) - 1) * (percentile / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        
        if f == c:
            return sorted_data[int(k)]
        
        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return d0 + d1
    
    def _check_thresholds(self, metrics: PerfMetrics) -> List[ThresholdViolation]:
        """
        检查性能阈值
        
        Args:
            metrics: 性能指标
        
        Returns:
            违规列表
        """
        violations = []
        
        for threshold in self.thresholds:
            actual_value = self._get_metric_value(metrics, threshold.metric)
            
            if self._compare(actual_value, threshold.operator, threshold.value):
                violation = ThresholdViolation(
                    threshold=threshold,
                    actual_value=actual_value,
                    message=f"{threshold.metric}={actual_value:.3f} {threshold.operator} {threshold.value}",
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                violations.append(violation)
        
        return violations
    
    def _get_metric_value(self, metrics: PerfMetrics, metric: str) -> float:
        """获取指标值"""
        metric_map = {
            'p50': metrics.median_response_time,
            'p90': metrics.p90_response_time,
            'p95': metrics.p95_response_time,
            'p99': metrics.p99_response_time,
            'avg': metrics.avg_response_time,
            'min': metrics.min_response_time,
            'max': metrics.max_response_time,
            'error_rate': metrics.error_rate,
            'rps': metrics.rps,
            'total_time': metrics.total_time,
        }
        return metric_map.get(metric, 0.0)
    
    def _compare(self, actual: float, operator: str, expected: float) -> bool:
        """比较操作"""
        comparison_map = {
            '<': lambda a, e: a < e,
            '<=': lambda a, e: a <= e,
            '>': lambda a, e: a > e,
            '>=': lambda a, e: a >= e,
            '==': lambda a, e: abs(a - e) < 0.001,
        }
        comparator = comparison_map.get(operator)
        if comparator is None:
            raise ValueError(f"未知的比较运算符：{operator}")
        return comparator(actual, expected)
    
    def has_critical_violations(self, metrics: PerfMetrics) -> bool:
        """检查是否有严重违规"""
        if not metrics.threshold_violations:
            return False
        return any(v.threshold.severity == 'critical' for v in metrics.threshold_violations)
    
    def get_summary_text(self, metrics: PerfMetrics) -> str:
        """生成性能测试摘要文本"""
        lines = [
            "=" * 70,
            "性能测试报告",
            "=" * 70,
            f"\n执行时间: {metrics.start_time} - {metrics.end_time}",
            f"总耗时: {metrics.total_time:.2f}s",
            f"\n请求统计:",
            f"  总请求数: {metrics.total_requests}",
            f"  成功: {metrics.successful_requests}",
            f"  失败: {metrics.failed_requests}",
            f"  错误率: {metrics.error_rate * 100:.2f}%",
            f"\n响应时间分布:",
            f"  最小: {metrics.min_response_time * 1000:.2f}ms",
            f"  平均: {metrics.avg_response_time * 1000:.2f}ms",
            f"  中位数 (P50): {metrics.median_response_time * 1000:.2f}ms",
            f"  P90: {metrics.p90_response_time * 1000:.2f}ms",
            f"  P95: {metrics.p95_response_time * 1000:.2f}ms",
            f"  P99: {metrics.p99_response_time * 1000:.2f}ms",
            f"  最大: {metrics.max_response_time * 1000:.2f}ms",
            f"\n吞吐量:",
            f"  RPS: {metrics.rps:.2f}",
            f"  吞吐量: {metrics.throughput / 1024:.2f} KB/s",
            f"\n状态码分布:",
        ]
        
        for code, count in sorted(metrics.status_code_distribution.items()):
            lines.append(f"  {code}: {count}")
        
        if metrics.threshold_violations:
            lines.append(f"\n⚠️ 阈值违规 ({len(metrics.threshold_violations)} 个):")
            for v in metrics.threshold_violations:
                severity_icon = "🔴" if v.threshold.severity == 'critical' else "🟡"
                lines.append(f"  {severity_icon} {v.message} [{v.threshold.severity.upper()}]")
        else:
            lines.append("\n✅ 所有阈值检查通过")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
