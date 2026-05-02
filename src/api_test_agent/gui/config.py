"""
API Test Agent GUI - 配置模块

提供 FastAPI 应用的配置管理
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """GUI 应用配置"""
    
    # 应用配置
    app_name: str = "API Test Agent GUI"
    app_version: str = "3.0.0-alpha"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # CORS 配置
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # 数据存储路径
    data_dir: str = os.path.join(os.getcwd(), "gui_data")
    projects_dir: str = os.path.join(data_dir, "projects")
    reports_dir: str = os.path.join(data_dir, "reports")
    tests_dir: str = os.path.join(data_dir, "tests")
    
    # 数据库配置（未来可选）
    db_url: str = "sqlite:///./gui.db"
    
    # WebSocket 配置
    ws_heartbeat_interval: int = 30  # 秒
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
