"""
API Test Agent GUI - FastAPI 应用入口

提供 REST API 和 WebSocket 支持，用于前端 GUI 编辑器交互
"""
import os
import shutil
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .config import settings
from .middleware.rate_limiter import RateLimitMiddleware

# 前端构建产物目录（从 gui/__init__.py 向上4级到项目根目录）
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"


class SPAMiddleware(BaseHTTPMiddleware):
    """SPA 中间件 - 对非 API 请求返回 index.html"""
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # 跳过 API 路径、静态文件和系统路径 - 让后续中间件/路由处理
        if (path.startswith("/api/") or 
            path.startswith("/assets") or 
            path.startswith("/health") or
            path == "/favicon.svg"):
            response = await call_next(request)
            return response
        
        # 尝试查找静态文件
        file_path = FRONTEND_DIST_DIR / path.lstrip("/")
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # 其他路径返回 index.html (SPA fallback)
        return FileResponse(str(FRONTEND_DIST_DIR / "index.html"))


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title="API Test Agent GUI",
        description="API 接口自动化测试平台的后端服务",
        version="3.0.0-alpha",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 速率限制中间件
    app.add_middleware(RateLimitMiddleware)

    # 注册路由（延迟导入避免循环依赖）
    from .routes import projects, tests, execution, environments, reports

    app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
    app.include_router(tests.router, prefix="/api/tests", tags=["测试用例"])
    app.include_router(execution.router, prefix="/api/execution", tags=["测试执行"])
    app.include_router(environments.router, prefix="/api/environments", tags=["环境管理"])
    app.include_router(reports.router, prefix="/api/reports", tags=["测试报告"])

    # 健康检查（在 SPA 中间件之前注册）
    @app.get("/health")
    async def health_check():
        try:
            import psutil
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            memory_usage = {
                "rss_mb": round(mem_info.rss / (1024 * 1024), 2),
                "vms_mb": round(mem_info.vms / (1024 * 1024), 2),
            }
        except ImportError:
            import tracemalloc
            current, peak = tracemalloc.get_traced_memory()
            memory_usage = {
                "rss_mb": round(current / (1024 * 1024), 2),
                "peak_mb": round(peak / (1024 * 1024), 2),
            }
        
        disk = shutil.disk_usage(Path.cwd())
        disk_usage = {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "percent_used": round(disk.used / disk.total * 100, 1),
        }
        
        try:
            from .websocket.manager import manager as ws_manager
            ws_connections = ws_manager.get_total_connections()
        except Exception:
            ws_connections = 0
        
        return {
            "status": "healthy",
            "version": settings.app_version,
            "memory": memory_usage,
            "disk": disk_usage,
            "websocket_connections": ws_connections,
        }

    # 前端静态文件服务（如果存在 dist 目录）
    if FRONTEND_DIST_DIR.exists():
        # 挂载静态资源目录
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="static")
        
        # 根路径直接返回 index.html
        @app.get("/")
        async def root():
            return FileResponse(str(FRONTEND_DIST_DIR / "index.html"))
        
        # 添加 SPA 中间件（处理前端路由）
        app.add_middleware(SPAMiddleware)
    else:
        @app.get("/")
        async def root():
            return {
                "service": "API Test Agent GUI",
                "version": "3.0.0-alpha",
                "status": "running",
                "docs": "/api/docs"
            }

    return app


app = create_app()
