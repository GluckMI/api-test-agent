"""
API Test Agent v3.0 - API 接口自动化测试框架

一个现代化的、功能丰富的 API 自动化测试框架，支持：
- 多环境配置管理
- 数据驱动测试（CSV/JSON）
- 钩子机制（HTTP/Command/Script）
- 并发执行
- 多种断言类型（15种，含 JSON Schema / Custom / Database）
- HTML/Markdown/JSON 报告生成
- 性能测试（负载测试、RPS 控制、阈值告警）
- 认证管理（OAuth 2.0 / JWT / API Key / HMAC）
- 可视化 GUI 编辑器（React 19 + Ant Design 6）

Usage:
    # CLI 方式运行
    python -m api_test_agent run tests/
    
    # 作为库使用
    from api_test_agent import TestRunner, EnvironmentManager
"""

__version__ = "3.0.0-alpha"
__author__ = "API Test Agent Team"

# 导出核心类和函数
from .config import Config, config
from .client import APIClient, APIResponse
from .runner import TestRunner, TestSuiteResult, TestCaseResult, TestStep
from .assertions import AssertEngine, AssertionResult
from .reports import ReportGenerator
from .environment import EnvironmentManager, EnvironmentConfig
from .hooks import HookEngine, HookType, HookConfig, HookResult
from .data_driver import DataDriver, DataSourceConfig, TemplateExpander
from .concurrent_runner import ConcurrentTestRunner, ConcurrencyResult, VariableContext

# Phase 2 新增模块
from .perf_collector import (
    PerfCollector,
    PerfMetrics,
    ThresholdConfig,
    ThresholdViolation,
    RequestRecord
)
from .perf_tester import LoadTester, LoadTestConfig, LoadTestResult
from .auth_manager import (
    AuthManager,
    OAuth2Client,
    JWTManager,
    TokenInfo
)

from .utils import (
    print_banner,
    print_success,
    print_error,
    print_warning,
    print_info,
    colored,
    Color,
    load_config_file,
    save_config_file,
    generate_test_id,
    calculate_hash,
    merge_dicts,
    format_duration,
    safe_get,
    validate_url,
    create_environment_template,
    create_test_case_template,
)

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    
    # 核心类
    "Config",
    "config",
    "APIClient",
    "APIResponse",
    "TestRunner",
    "TestSuiteResult",
    "TestCaseResult",
    "TestStep",
    "AssertEngine",
    "AssertionResult",
    "ReportGenerator",
    
    # v2.0 Phase 1 模块
    "EnvironmentManager",
    "EnvironmentConfig",
    "HookEngine",
    "HookType",
    "HookConfig",
    "HookResult",
    "DataDriver",
    "DataSourceConfig",
    "TemplateExpander",
    "ConcurrentTestRunner",
    "ConcurrencyResult",
    "VariableContext",
    
    # v2.0 Phase 2 模块
    "PerfCollector",
    "PerfMetrics",
    "ThresholdConfig",
    "ThresholdViolation",
    "RequestRecord",
    "LoadTester",
    "LoadTestConfig",
    "LoadTestResult",
    "AuthManager",
    "OAuth2Client",
    "JWTManager",
    "TokenInfo",
    
    # 工具函数
    "print_banner",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "colored",
    "Color",
    "load_config_file",
    "save_config_file",
    "generate_test_id",
    "calculate_hash",
    "merge_dicts",
    "format_duration",
    "safe_get",
    "validate_url",
    "create_environment_template",
    "create_test_case_template",
]
