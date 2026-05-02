"""
API Test Agent GUI - 独立启动脚本

解决 Windows 下 uvicorn 热重载的 multiprocessing 模块路径问题
直接运行此脚本或通过 cli.py 的 gui start 命令启动
"""
import sys
import socket
from pathlib import Path


def is_port_available(host: str, port: int) -> bool:
    """
    检测指定端口是否可用
    
    注意：不使用 SO_REUSEADDR，因为 Windows 上该选项允许
    多个 socket 绑定同一端口，会导致检测不准确。
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.bind((host, port))
        return True
    except OSError:
        return False
    except Exception:
        return True
    finally:
        if sock:
            sock.close()


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

    args = parser.parse_args()

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
