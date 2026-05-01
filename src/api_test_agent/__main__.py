"""
API Test Agent - 命令行入口点

支持通过 python -m api_test_agent 运行

Example:
    python -m api_test_agent run tests/
    python -m api_test_agent env list
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_dir = Path(__file__).parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# 导入并运行 CLI
if __name__ == "__main__":
    from api_test_agent.cli import main
    main()
