"""
API Test Agent GUI - 独立启动脚本

解决 Windows 下 uvicorn 热重载的 multiprocessing 模块路径问题
直接运行此脚本或通过 cli.py 的 gui start 命令启动
"""
import sys
import socket
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(verbose: bool = False):
    """
    初始化日志系统（与项目 runner.py 保持一致的格式）
    
    Args:
        verbose: 是否启用详细日志（DEBUG 级别）
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    
    logs_dir = Path.cwd() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "api_test_agent.log"
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    formatter = logging.Formatter(log_format)
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


logger = logging.getLogger(__name__)


def is_port_available(host: str, port: int) -> bool:
    """
    检测指定端口是否可用
    
    注意：不使用 SO_REUSEADDR，因为 Windows 上该选项允许
    多个 socket 绑定同一端口，会导致检测不准确。
    
    异常处理策略：
    - OSError: 端口被占用或权限不足 → 返回 False
    - socket.timeout: 连接超时 → 返回 False（可能被防火墙拦截）
    - 其他未知异常: 记录日志并返回 False（保守策略）
    
    Args:
        host: 主机地址（如 '0.0.0.0' 或 '127.0.0.1'）
        port: 端口号
        
    Returns:
        True 表示端口可用，False 表示不可用或检测失败
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.bind((host, port))
        return True
    except OSError as e:
        logger.debug(f"Port {port} on {host} unavailable (OSError): {e}")
        return False
    except socket.timeout as e:
        logger.warning(f"Port {port} on {host} check timed out: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking port {port} on {host}: {type(e).__name__}: {e}")
        return False
    finally:
        if sock:
            try:
                sock.close()
            except Exception:
                pass


def find_available_port(host: str, start_port: int = 8000, max_attempts: int = 100) -> int:
    """
    从指定端口开始查找可用端口
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(host, port):
            return port
    raise RuntimeError(f"无法找到可用端口，已尝试 {max_attempts} 个端口")


def setup_path():
    """配置 Python 路径"""
    _src_dir = Path(__file__).parent.parent  # src/

    _src_path = str(_src_dir)
    if _src_path not in sys.path:
        try:
            idx = sys.path.index("")
            sys.path.insert(idx + 1, _src_path)
        except ValueError:
            sys.path.insert(1, _src_path)


setup_path()


def main():
    """GUI 服务器主入口"""
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="API Test Agent GUI Server")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用热重载")
    parser.add_argument("--no-reload", action="store_true", help="禁用热重载")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="启用详细日志（DEBUG 级别）")

    args = parser.parse_args()

    # 初始化日志系统（在所有其他操作之前）
    setup_logging(verbose=args.verbose)
    
    logger.info("Starting API Test Agent GUI Server")
    if args.verbose:
        logger.debug("Verbose mode enabled, showing DEBUG level logs")

    # 检测端口并自动切换（在打印信息之前）
    final_port = args.port
    if not is_port_available(args.host, args.port):
        print(f"⚠️ 端口 {args.port} 已被占用，正在查找可用端口...")
        final_port = find_available_port(args.host, args.port + 1)
        print(f"✅ 找到可用端口: {final_port}")

    reload = False
    if args.reload:
        reload = True
    elif not args.no_reload:
        reload = True

    print("=" * 60)
    print("  API Test Agent GUI Server")
    print("=" * 60)
    print(f"  Address: http://{args.host}:{final_port}")
    print(f"  Docs:    http://{args.host}:{final_port}/api/docs")
    print(f"  Reload:  {'Enabled' if reload else 'Disabled'}")
    print("=" * 60)

    # 热重载需要字符串路径，非热重载可以直接传 app 对象
    if reload:
        uvicorn.run(
            "api_test_agent.gui:app",
            host=args.host,
            port=final_port,
            reload=reload,
            log_level="info",
        )
    else:
        from api_test_agent.gui import app
        uvicorn.run(
            app,
            host=args.host,
            port=final_port,
            reload=False,
            log_level="info",
        )


if __name__ == "__main__":
    main()
