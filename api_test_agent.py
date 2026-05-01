#!/usr/bin/env python
"""
API 接口自动化测试 Agent - 入口脚本（向后兼容）

这个文件作为向后兼容的入口点，实际逻辑已迁移到 src/api_test_agent/cli.py

Usage:
    # 传统方式运行
    python api_test_agent.py run tests/
    
    # 新方式（推荐）
    python -m api_test_agent run tests/
    
    # 作为库使用
    from api_test_agent import TestRunner, EnvironmentManager
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# 导入并运行 CLI
from api_test_agent.cli import main

if __name__ == "__main__":
    main()
