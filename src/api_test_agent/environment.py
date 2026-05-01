"""
API 接口自动化测试 Agent - 环境管理器模块

提供多环境配置管理能力，支持：
- YAML 配置文件加载与合并
- .env 文件自动加载
- 命令行参数覆盖
- 配置校验与验证
- 敏感信息脱敏显示
"""
import os
import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


@dataclass
class EnvironmentConfig:
    """环境配置数据类

    Attributes:
        name: 环境名称
        base_url: API 基础 URL
        timeout: 请求超时时间（秒）
        headers: 默认请求头
        variables: 自定义变量字典
        env_variables: 从 .env 文件加载的环境变量
    """

    name: str = ""
    base_url: str = ""
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    env_variables: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "headers": self.headers.copy(),
            "variables": self.variables.copy(),
            "env_variables": self.env_variables.copy(),
        }


class EnvironmentManager:
    """环境管理器

    负责加载、管理和切换测试环境配置。
    支持三级配置合并：defaults → environments.{env_name} → 最终结果

    优先级顺序（从低到高）：
    1. defaults 全局默认配置
    2. environments.{env_name} 环境特定配置
    3. .env 文件中的环境变量
    4. 命令行参数覆盖（最高优先级）

    Example:
        >>> manager = EnvironmentManager("configs/environments.yaml")
        >>> config = manager.load_environment("staging")
        >>> print(config.base_url)
        https://staging.example.com
    """

    DEFAULT_CONFIG_FILE = "configs/environments.yaml"
    SENSITIVE_PATTERNS = ("_KEY", "_SECRET", "_PASSWORD", "_TOKEN", "_CREDENTIAL")
    SANITIZE_MASK = "************"

    def __init__(self, config_file: Optional[str] = None):
        """初始化环境管理器

        Args:
            config_file: 配置文件路径，默认为 configs/environments.yaml

        Raises:
            FileNotFoundError: 当配置文件不存在时抛出
        """
        self.config_file = Path(config_file or self.DEFAULT_CONFIG_FILE)
        self._raw_config: Dict[str, Any] = {}
        self._current_config: Optional[EnvironmentConfig] = None
        self._overrides: Dict[str, str] = {}

        self._load_config()

    def _load_config(self) -> None:
        """加载 YAML 配置文件

        Raises:
            FileNotFoundError: 当配置文件不存在时抛出，附带友好错误提示
        """
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"环境配置文件不存在: {self.config_file}\n"
                f"请确认文件路径正确，或运行 'api_test_agent init' 创建示例配置"
            )

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._raw_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(
                f"配置文件解析失败: {self.config_file}\n"
                f"YAML 解析错误: {e}\n"
                f"请检查文件格式是否正确"
            )

    def list_environments(self) -> List[str]:
        """获取可用环境名称列表

        Returns:
            环境名称列表，按定义顺序返回
        """
        environments = self._raw_config.get("environments", {})
        if isinstance(environments, dict):
            return list(environments.keys())
        return []

    def load_environment(self, env_name: str) -> EnvironmentConfig:
        """加载指定环境的配置

        实现三级配置合并逻辑：
        1. 加载 defaults 全局默认配置
        2. 合并 environments.{env_name} 环境特定配置
        3. 加载对应的 .env 文件（如果存在）

        Args:
            env_name: 环境名称

        Returns:
            合并后的 EnvironmentConfig 对象

        Raises:
            ValueError: 当环境不存在时抛出，提示可用环境列表
        """
        available_envs = self.list_environments()

        if env_name not in available_envs:
            raise ValueError(
                f"环境 '{env_name}' 不存在\n"
                f"可用环境列表: {', '.join(available_envs) if available_envs else '(无)'}\n"
                f"请检查配置文件: {self.config_file}"
            )

        # Step 1: 加载全局默认配置
        defaults = self._raw_config.get("defaults", {})
        merged_config = self._deep_merge({}, defaults)

        # Step 2: 合并环境特定配置
        env_config = self._raw_config.get("environments", {}).get(env_name, {})
        merged_config = self._deep_merge(merged_config, env_config)

        # Step 3: 设置环境名称
        merged_config["name"] = env_name

        # Step 4: 加载 .env 文件
        env_variables = self._load_env_file_for_environment(env_name)
        merged_config["env_variables"] = env_variables

        # Step 5: 创建 EnvironmentConfig 对象
        # 分离标准字段和额外字段
        standard_fields = {
            "name": merged_config.get("name", env_name),
            "base_url": merged_config.get("base_url", ""),
            "timeout": merged_config.get("timeout", 30),
            "headers": merged_config.get("headers", {}),
            "variables": merged_config.get("variables", {}),
            "env_variables": merged_config.get("env_variables", {}),
        }

        # 将非标准字段合并到 variables 中
        extra_fields = {
            k: v
            for k, v in merged_config.items()
            if k not in ("name", "base_url", "timeout", "headers", "variables", "env_variables")
        }
        if extra_fields:
            standard_fields["variables"] = {**standard_fields["variables"], **extra_fields}

        config = EnvironmentConfig(**standard_fields)

        # Step 6: 应用命令行覆盖（如果有）
        if self._overrides:
            config = self._apply_overrides_to_config(config, self._overrides)

        self._current_config = config
        return config

    def _load_env_file_for_environment(self, env_name: str) -> Dict[str, str]:
        """为指定环境加载 .env 文件

        按以下顺序查找并加载：
        1. .env.{env_name} （环境特定的 .env 文件）
        2. .env （通用 .env 文件）

        Args:
            env_name: 环境名称

        Returns:
            加载的环境变量字典
        """
        env_variables: Dict[str, str] = {}
        config_dir = self.config_file.parent

        # 尝试加载环境特定的 .env 文件
        env_specific_file = config_dir / f".env.{env_name}"
        if env_specific_file.exists():
            env_vars = self._load_env_file(env_specific_file)
            env_variables.update(env_vars)

        # 尝试加载通用的 .env 文件
        generic_env_file = config_dir / ".env"
        if generic_env_file.exists() and generic_env_file != env_specific_file:
            env_vars = self._load_env_file(generic_env_file)
            # 通用 .env 文件的优先级较低，只在键不存在时才添加
            for key, value in env_vars.items():
                if key not in env_variables:
                    env_variables[key] = value

        return env_variables

    def _load_env_file(self, env_file_path: Path) -> Dict[str, str]:
        """加载 .env 文件

        支持 .env 格式规范：
        - KEY=VALUE 格式
        - 支持注释行（以 # 开头）
        - 支持空行
        - 支持引号包裹的值（单引号和双引号）
        - 支持等号两侧的空格

        Args:
            env_file_path: .env 文件路径

        Returns:
            解析后的键值对字典
        """
        env_variables: Dict[str, str] = {}

        try:
            with open(env_file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 跳过空行和注释行
                    if not line or line.startswith("#"):
                        continue

                    # 解析 KEY=VALUE
                    if "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip()

                        # 移除值两端的引号
                        if (value.startswith('"') and value.endswith('"')) or (
                            value.startswith("'") and value.endswith("'")
                        ):
                            value = value[1:-1]

                        if key:
                            env_variables[key] = value
        except Exception as e:
            warnings.warn(
                f"加载 .env 文件失败: {env_file_path}\n错误: {e}",
                UserWarning,
            )

        return env_variables

    def apply_overrides(self, overrides: Dict[str, str]) -> None:
        """应用命令行覆盖参数

        支持两种覆盖模式：
        1. 简单键值对：timeout=60
        2. 嵌套键：headers.Authorization=Bearer xxx

        覆盖具有最高优先级，会在 load_environment 时自动应用。

        Args:
            overrides: 覆盖参数字典
        """
        self._overrides.update(overrides)

        # 如果已经加载了配置，立即重新应用覆盖
        if self._current_config:
            self._current_config = self._apply_overrides_to_config(
                self._current_config, overrides
            )

    def _apply_overrides_to_config(
        self, config: EnvironmentConfig, overrides: Dict[str, str]
    ) -> EnvironmentConfig:
        """将覆盖参数应用到配置对象

        Args:
            config: 当前配置对象
            overrides: 覆盖参数字典

        Returns:
            应用覆盖后的新配置对象
        """
        config_dict = config.to_dict()
        extra_fields: Dict[str, Any] = {}

        for key, value in overrides.items():
            # 处理嵌套键（如 headers.Authorization）
            if "." in key:
                parts = key.split(".", 1)
                parent_key = parts[0]
                child_key = parts[1]

                # 检查是否是标准字段
                if parent_key in ("headers", "variables", "env_variables"):
                    if parent_key not in config_dict or not isinstance(
                        config_dict[parent_key], dict
                    ):
                        config_dict[parent_key] = {}

                    config_dict[parent_key][child_key] = value
                else:
                    # 非标准字段存入 extra_fields
                    if parent_key not in extra_fields:
                        extra_fields[parent_key] = {}
                    extra_fields[parent_key][child_key] = value
            else:
                # 处理简单键值对
                if key == "timeout":
                    try:
                        config_dict[key] = int(value)
                    except ValueError:
                        config_dict[key] = value
                elif key in ("name", "base_url"):
                    config_dict[key] = value
                else:
                    # 其他字段存入 variables 或 extra_fields
                    extra_fields[key] = value

        # 将额外字段合并到 variables 中
        if extra_fields:
            config_dict["variables"] = {**config_dict.get("variables", {}), **extra_fields}

        return EnvironmentConfig(**config_dict)

    def validate_environment(self, env_name: str) -> List[str]:
        """校验环境配置的有效性

        校验项目：
        1. 必填字段检查（base_url）
        2. URL 格式有效性
        3. 变量引用完整性（无未定义的 ${var}）

        Args:
            env_name: 环境名称

        Returns:
            错误消息列表，空列表表示校验通过
        """
        errors: List[str] = []

        try:
            config = self.load_environment(env_name)
        except (ValueError, FileNotFoundError) as e:
            return [str(e)]

        # 校验必填字段 base_url
        if not config.base_url:
            errors.append(f"环境 '{env_name}' 缺少必填字段: base_url")

        # 校验 URL 格式
        if config.base_url and not self._validate_url(config.base_url):
            errors.append(f"环境 '{env_name}' 的 URL 格式无效: {config.base_url}")

        # 校验变量引用完整性
        undefined_vars = self._find_undefined_variables(config)
        if undefined_vars:
            errors.append(
                f"环境 '{env_name}' 存在未定义的变量引用: "
                f"{', '.join(undefined_vars)}"
            )

        return errors

    def _validate_url(self, url: str) -> bool:
        """验证 URL 格式有效性

        Args:
            url: 待验证的 URL 字符串

        Returns:
            True 如果 URL 格式有效，否则 False
        """
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, url))

    def _find_undefined_variables(self, config: EnvironmentConfig) -> List[str]:
        """查找配置中未定义的变量引用

        检测 ${var_name} 格式的变量引用是否在 variables 或 env_variables 中定义。

        Args:
            config: 环境配置对象

        Returns:
            未定义的变量名列表
        """
        all_variables = set(config.variables.keys()) | set(config.env_variables.keys())
        undefined_vars: List[str] = []

        # 在所有字符串值中查找变量引用
        config_dict = config.to_dict()
        var_pattern = re.compile(r"\$\{([^}]+)\}")

        def search_in_dict(d: Dict[str, Any], path: str = "") -> None:
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key

                if isinstance(value, str):
                    matches = var_pattern.findall(value)
                    for match in matches:
                        if match not in all_variables and match not in undefined_vars:
                            undefined_vars.append(match)
                elif isinstance(value, dict):
                    search_in_dict(value, current_path)

        search_in_dict(config_dict)
        return undefined_vars

    def show_config(self, sanitize: bool = True) -> Dict[str, Any]:
        """显示当前生效的配置

        Args:
            sanitize: 是否脱敏敏感信息，默认为 True

        Returns:
            当前配置字典（敏感信息已脱敏）
        """
        if not self._current_config:
            return {"error": "未加载任何环境配置"}

        config_dict = self._current_config.to_dict()

        if sanitize:
            config_dict = self._sanitize_config(config_dict)

        return config_dict

    def _sanitize_value(self, key: str, value: Any) -> Any:
        """对敏感信息进行脱敏处理

        检测后缀模式：_KEY, _SECRET, _PASSWORD, _TOKEN, _CREDENTIAL
        将匹配的值替换为固定长度的 * 号。

        Args:
            key: 键名
            value: 值

        Returns:
            脱敏后的值（保留前缀便于识别类型）
        """
        if not isinstance(value, str):
            return value

        upper_key = key.upper()
        is_sensitive = any(
            upper_key.endswith(pattern) for pattern in self.SENSITIVE_PATTERNS
        )

        if is_sensitive and value:
            # 保留前缀（如 sk_live_, Bearer ）便于识别类型
            prefix_match = re.match(r"^(\w{0,8}[_\-]?)", value)
            prefix = prefix_match.group(1) if prefix_match else ""
            return f"{prefix}{self.SANITIZE_MASK}"

        return value

    def _sanitize_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """递归脱敏配置中的所有敏感信息

        Args:
            config_dict: 原始配置字典

        Returns:
            脱敏后的配置字典
        """
        sanitized: Dict[str, Any] = {}

        for key, value in config_dict.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_config(value)
            else:
                sanitized[key] = self._sanitize_value(key, value)

        return sanitized

    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并两个字典

        对于嵌套字典，递归合并；对于其他类型，直接覆盖。

        Args:
            base: 基础字典
            override: 覆盖字典

        Returns:
            合并后的新字典
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = EnvironmentManager._deep_merge(result[key], value)
            else:
                result[key] = value

        return result
