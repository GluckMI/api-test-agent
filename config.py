"""
API 接口自动化测试 Agent - 配置管理模块
"""
import os
import json
from pathlib import Path


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "base_url": "",
            "timeout": 30,
            "retry_times": 3,
            "retry_delay": 1,
            "headers": {
                "Content-Type": "application/json"
            },
            "test_dir": "tests",
            "report_dir": "reports",
            "log_level": "INFO",
            "log_file": "api_test.log"
        }
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    return {**self.default_config, **loaded_config}
            except Exception as e:
                print(f"警告：配置文件加载失败，使用默认配置：{e}")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """设置配置项"""
        self.config[key] = value
    
    @property
    def test_dir(self) -> Path:
        """获取测试目录路径"""
        return Path(self.config.get("test_dir", "tests"))
    
    @property
    def report_dir(self) -> Path:
        """获取报告目录路径"""
        return Path(self.config.get("report_dir", "reports"))


# 全局配置实例
config = Config()
