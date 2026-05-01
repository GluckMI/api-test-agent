"""
API Test Agent v2.0 - API 接口自动化测试框架

一个现代化的、功能丰富的 API 自动化测试框架，支持：
- 多环境配置管理
- 数据驱动测试（CSV/JSON）
- 钩子机制（HTTP/Command/Script）
- 并发执行
- 多种断言类型
- HTML/Markdown/JSON 报告生成

Usage:
    # CLI 方式运行
    python -m api_test_agent run tests/
    
    # 作为库使用
    from api_test_agent import TestRunner, EnvironmentManager
"""

__version__ = "2.0.0"
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
from .concurrent import ConcurrentTestRunner, ConcurrencyResult, VariableContext

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
    
    # v2.0 模块
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
