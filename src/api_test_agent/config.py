"""
API 接口自动化测试 Agent - 配置管理模块
支持环境配置管理，可加载多环境配置文件
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """配置管理类

    支持两种模式：
    1. 基础模式：仅加载 config.json 配置文件（向后兼容）
    2. 环境模式：额外加载环境配置（configs/environments.yaml），支持多环境切换

    Example:
        # 基础模式（向后兼容）
        config = Config()

        # 环境模式
        config = Config(environment="staging")
    """

    def __init__(self, config_file: str = "config.json", environment: Optional[str] = None):
        self.config_file = config_file
        self.environment = environment
        self._environment_manager = None
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

        if environment:
            self._init_environment_manager(environment)
    
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

    def _init_environment_manager(self, env_name: str):
        """初始化环境管理器并加载环境配置

        Args:
            env_name: 环境名称（如 dev, staging, prod）
        """
        try:
            from .environment import EnvironmentManager
            self._environment_manager = EnvironmentManager()
            env_config = self._environment_manager.load_environment(env_name)

            # 将环境配置合并到主配置中（环境配置优先级更高）
            env_dict = env_config.to_dict()

            # 合并标准字段
            if env_dict.get("base_url"):
                self.config["base_url"] = env_dict["base_url"]
            if env_dict.get("timeout"):
                self.config["timeout"] = env_dict["timeout"]
            if env_dict.get("headers"):
                self.config["headers"] = {**self.config["headers"], **env_dict["headers"]}

            # 将 variables 和 env_variables 存储到配置中供使用
            self.config["environment_variables"] = {
                **env_dict.get("variables", {}),
                **env_dict.get("env_variables", {})
            }
            self.config["current_environment"] = env_name

            print(f"✓ 已加载环境配置: {env_name}")

        except FileNotFoundError as e:
            print(f"⚠ 环境配置文件未找到：{e}")
            print("  提示：运行 'python api_test_agent.py init' 创建示例配置")
        except ValueError as e:
            print(f"✗ 环境配置错误：{e}")
        except ImportError:
            print("⚠ environment 模块不可用，跳过环境配置加载")
        except Exception as e:
            print(f"⚠ 加载环境配置失败：{e}")
    
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

    @property
    def environment_manager(self):
        """获取环境管理器实例（如果已初始化）"""
        return self._environment_manager

    def get_environment_config(self) -> Optional[Dict[str, Any]]:
        """获取当前环境的完整配置

        Returns:
            环境配置字典，如果未启用环境模式则返回 None
        """
        if self._environment_manager and self._environment_manager._current_config:
            return self._environment_manager.show_config(sanitize=False)
        return None

    def get_environment_variables(self) -> Dict[str, Any]:
        """获取当前环境的环境变量

        Returns:
            环境变量字典
        """
        return self.config.get("environment_variables", {})


# 全局配置实例
config = Config()
