"""
环境管理器模块单元测试

覆盖范围：
- Task 1.1: 模块骨架和初始化
- Task 1.2: 环境列表与加载逻辑
- Task 1.3: .env 文件加载器
- Task 1.4: 命令行覆盖机制
- Task 1.5: 配置校验功能
- Task 1.6: 敏感信息脱敏显示
- 边界情况和异常处理
"""
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from api_test_agent.environment import EnvironmentConfig, EnvironmentManager


class TestEnvironmentConfig:
    """EnvironmentConfig 数据类测试"""

    def test_default_values(self):
        """测试默认值初始化"""
        config = EnvironmentConfig()
        assert config.name == ""
        assert config.base_url == ""
        assert config.timeout == 30
        assert config.headers == {}
        assert config.variables == {}
        assert config.env_variables == {}

    def test_custom_values(self):
        """测试自定义值初始化"""
        config = EnvironmentConfig(
            name="staging",
            base_url="https://staging.example.com",
            timeout=60,
            headers={"Authorization": "Bearer token"},
            variables={"api_version": "v2"},
            env_variables={"API_KEY": "secret"},
        )
        assert config.name == "staging"
        assert config.base_url == "https://staging.example.com"
        assert config.timeout == 60
        assert config.headers == {"Authorization": "Bearer token"}
        assert config.variables == {"api_version": "v2"}
        assert config.env_variables == {"API_KEY": "secret"}

    def test_to_dict(self):
        """测试转换为字典"""
        config = EnvironmentConfig(
            name="test",
            base_url="http://localhost",
            timeout=10,
        )
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["name"] == "test"
        assert config_dict["base_url"] == "http://localhost"
        assert config_dict["timeout"] == 10

    def test_to_dict_independence(self):
        """测试 to_dict 返回的字典是独立的副本"""
        config = EnvironmentConfig(variables={"key": "value"})
        config_dict = config.to_dict()

        # 修改返回的字典不应影响原对象
        config_dict["variables"]["new_key"] = "new_value"
        assert "new_key" not in config.variables


class TestEnvironmentManagerInit:
    """Task 1.1: 初始化和配置加载测试"""

    def test_init_with_valid_config(self, tmp_path):
        """测试使用有效配置文件初始化"""
        config_file = self._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        assert manager.config_file == config_file
        assert manager._raw_config is not None
        assert manager._current_config is None

    def test_init_with_default_path(self, tmp_path, monkeypatch):
        """测试使用默认路径初始化"""
        # 在默认路径创建配置文件
        default_config_dir = tmp_path / "configs"
        default_config_dir.mkdir()
        config_file = default_config_dir / "environments.yaml"
        self._write_sample_config(config_file)

        monkeypatch.chdir(tmp_path)
        manager = EnvironmentManager()

        assert manager.config_file.name == "environments.yaml"

    def test_init_with_nonexistent_file(self, tmp_path):
        """测试配置文件不存在时抛出 FileNotFoundError"""
        nonexistent_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError) as exc_info:
            EnvironmentManager(str(nonexistent_file))

        assert "环境配置文件不存在" in str(exc_info.value)
        assert str(nonexistent_file) in str(exc_info.value)

    def test_init_with_invalid_yaml(self, tmp_path):
        """测试无效 YAML 格式抛出 ValueError"""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: [", encoding="utf-8")

        with pytest.raises(ValueError) as exc_info:
            EnvironmentManager(str(invalid_yaml))

        assert "配置文件解析失败" in str(exc_info.value)
        assert "YAML 解析错误" in str(exc_info.value)

    def test_init_with_empty_file(self, tmp_path):
        """测试空配置文件正常加载"""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("", encoding="utf-8")

        manager = EnvironmentManager(str(empty_file))
        assert manager._raw_config == {}
        assert manager.list_environments() == []

    @staticmethod
    def _create_sample_config(tmp_path: Path) -> Path:
        """创建示例配置文件"""
        config_file = tmp_path / "environments.yaml"
        TestEnvironmentManagerInit._write_sample_config(config_file)
        return config_file

    @staticmethod
    def _write_sample_config(config_file: Path) -> None:
        """写入示例配置内容"""
        sample_config = {
            "defaults": {
                "timeout": 30,
                "headers": {"Content-Type": "application/json"},
                "variables": {"default_var": "default_value"},
            },
            "environments": {
                "dev": {
                    "base_url": "http://localhost:8080",
                    "timeout": 10,
                    "headers": {"X-Env": "dev"},
                },
                "staging": {
                    "base_url": "https://staging.example.com",
                    "headers": {"X-Env": "staging"},
                },
                "prod": {
                    "base_url": "https://api.example.com",
                    "timeout": 60,
                },
            },
        }
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(sample_config, f, allow_unicode=True)


class TestListEnvironments:
    """Task 1.2: 环境列表功能测试"""

    def test_list_multiple_environments(self, tmp_path):
        """测试列出多个环境"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        envs = manager.list_environments()

        assert isinstance(envs, list)
        assert len(envs) == 3
        assert "dev" in envs
        assert "staging" in envs
        assert "prod" in envs

    def test_list_empty_environments(self, tmp_path):
        """测试空环境列表"""
        config_file = tmp_path / "empty_envs.yaml"
        config_file.write_text("{}", encoding="utf-8")

        manager = EnvironmentManager(str(config_file))
        envs = manager.list_environments()

        assert envs == []

    def test_list_preserves_order(self, tmp_path):
        """测试保持定义顺序"""
        config_data = {
            "environments": {
                "alpha": {"base_url": "http://a"},
                "beta": {"base_url": "http://b"},
                "gamma": {"base_url": "http://g"},
            }
        }
        config_file = tmp_path / "ordered.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        envs = manager.list_environments()

        assert envs == ["alpha", "beta", "gamma"]


class TestLoadEnvironment:
    """Task 1.2: 环境加载逻辑测试"""

    def test_load_valid_environment(self, tmp_path):
        """测试加载有效环境"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        config = manager.load_environment("dev")

        assert isinstance(config, EnvironmentConfig)
        assert config.name == "dev"
        assert config.base_url == "http://localhost:8080"

    def test_load_nonexistent_environment(self, tmp_path):
        """测试加载不存在的环境抛出 ValueError"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        with pytest.raises(ValueError) as exc_info:
            manager.load_environment("nonexistent")

        error_msg = str(exc_info.value)
        assert "环境 'nonexistent' 不存在" in error_msg
        assert "dev" in error_msg
        assert "可用环境列表" in error_msg

    def test_three_level_merge_defaults_to_env(self, tmp_path):
        """测试三级合并：defaults → environment"""
        config_data = {
            "defaults": {
                "timeout": 30,
                "headers": {
                    "Content-Type": "application/json",
                    "X-Default": "yes",
                },
                "variables": {"common": "value"},
            },
            "environments": {
                "test": {
                    "base_url": "http://test.com",
                    "timeout": 45,
                    "headers": {"X-Specific": "override"},
                }
            },
        }
        config_file = tmp_path / "merge_test.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("test")

        # 环境特定值应覆盖默认值
        assert config.timeout == 45
        # 默认值应被继承
        assert "Content-Type" in config.headers
        assert "X-Default" in config.headers
        # 环境特定 header 应添加到默认 headers
        assert "X-Specific" in config.headers
        # 变量应被继承
        assert config.variables.get("common") == "value"

    def test_environment_with_only_defaults(self, tmp_path):
        """测试仅使用默认值的环境"""
        config_data = {
            "defaults": {
                "base_url": "http://default.com",
                "timeout": 20,
            },
            "environments": {
                "minimal": {},
            },
        }
        config_file = tmp_path / "minimal.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("minimal")

        assert config.base_url == "http://default.com"
        assert config.timeout == 20

    def test_graceful_degradation_missing_fields(self, tmp_path):
        """测试缺失字段的优雅降级"""
        config_data = {
            "environments": {
                "partial": {
                    "base_url": "http://partial.com",
                    # 缺少 timeout, headers, variables
                }
            },
        }
        config_file = tmp_path / "partial.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("partial")

        assert config.base_url == "http://partial.com"
        assert config.timeout == 30  # 使用默认值
        assert config.headers == {}  # 空字典
        assert config.variables == {}  # 空字典


class TestEnvFileLoading:
    """Task 1.3: .env 文件加载测试"""

    def test_load_env_specific_file(self, tmp_path):
        """测试加载环境特定的 .env 文件"""
        config_file = tmp_path / "configs" / "environments.yaml"
        config_file.parent.mkdir()
        config_file.write_text(
            """
environments:
  staging:
    base_url: https://staging.example.com
""",
            encoding="utf-8",
        )

        # 创建 .env.staging 文件
        env_file = tmp_path / "configs" / ".env.staging"
        env_file.write_text(
            """# Staging environment variables
STAGING_API_KEY=sk_live_12345
STAGING_DB_HOST=db.staging.com
# This is a comment
EMPTY_VALUE=
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("staging")

        assert "STAGING_API_KEY" in config.env_variables
        assert config.env_variables["STAGING_API_KEY"] == "sk_live_12345"
        assert config.env_variables["STAGING_DB_HOST"] == "db.staging.com"
        assert config.env_variables.get("EMPTY_VALUE") == ""

    def test_load_generic_env_file(self, tmp_path):
        """测试加载通用的 .env 文件"""
        config_file = tmp_path / "configs" / "environments.yaml"
        config_file.parent.mkdir()
        config_file.write_text(
            """
environments:
  dev:
    base_url: http://localhost:8080
""",
            encoding="utf-8",
        )

        # 创建通用 .env 文件
        env_file = tmp_path / "configs" / ".env"
        env_file.write_text(
            """COMMON_VAR=common_value
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("dev")

        assert "COMMON_VAR" in config.env_variables
        assert config.env_variables["COMMON_VAR"] == "common_value"

    def test_env_specific_overrides_generic(self, tmp_path):
        """测试环境特定 .env 覆盖通用 .env"""
        config_file = tmp_path / "configs" / "environments.yaml"
        config_file.parent.mkdir()
        config_file.write_text(
            """
environments:
  prod:
    base_url: https://prod.example.com
""",
            encoding="utf-8",
        )

        # 创建通用 .env
        generic_env = tmp_path / "configs" / ".env"
        generic_env.write_text("SHARED_KEY=shared_value\n", encoding="utf-8")

        # 创建环境特定 .env
        specific_env = tmp_path / "configs" / ".env.prod"
        specific_env.write_text(
            "SHARED_KEY=prod_specific\nPROD_ONLY=prod_value\n", encoding="utf-8"
        )

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("prod")

        # 环境特定值应覆盖通用值
        assert config.env_variables["SHARED_KEY"] == "prod_specific"
        # 仅在环境特定文件中的值也应存在
        assert config.env_variables["PROD_ONLY"] == "prod_value"

    def test_missing_env_file_not_blocking(self, tmp_path):
        """测试 .env 文件不存在时不阻塞"""
        config_file = tmp_path / "no_env.yaml"
        config_file.write_text(
            """
environments:
  test:
    base_url: http://test.com
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("test")

        # 应正常返回配置，只是没有环境变量
        assert config.base_url == "http://test.com"
        assert config.env_variables == {}

    def test_parse_quoted_values(self, tmp_path):
        """测试解析带引号的值"""
        config_file = tmp_path / "quoted.yaml"
        config_file.write_text(
            """
environments:
  test:
    base_url: http://test.com
""",
            encoding="utf-8",
        )

        env_file = tmp_path / ".env.test"
        env_file.write_text(
            """QUOTED_DOUBLE="double quoted value"
QUOTED_SINGLE='single quoted value'
UNQUOTED=no quotes
WITH_SPACES=value with spaces
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager(str(config_file))

        # 直接调用 _load_env_file 测试解析
        parsed = manager._load_env_file(env_file)

        assert parsed["QUOTED_DOUBLE"] == "double quoted value"
        assert parsed["QUOTED_SINGLE"] == "single quoted value"
        assert parsed["UNQUOTED"] == "no quotes"
        assert parsed["WITH_SPACES"] == "value with spaces"

    def test_skip_comments_and_empty_lines(self, tmp_path):
        """测试跳过注释行和空行"""
        env_file = tmp_path / "comments.env"
        env_file.write_text(
            """# Comment line 1
# Comment line 2

VALID_KEY=value1

  # Indented comment
VALID_KEY2=value2
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager.__new__(EnvironmentManager)
        parsed = manager._load_env_file(env_file)

        assert len(parsed) == 2
        assert "VALID_KEY" in parsed
        assert "VALID_KEY2" in parsed

    def test_equals_in_value(self, tmp_path):
        """测试值中包含等号的情况"""
        env_file = tmp_path / "equals.env"
        env_file.write_text("EQUATION=1+1=2\n", encoding="utf-8")

        manager = EnvironmentManager.__new__(EnvironmentManager)
        parsed = manager._load_env_file(env_file)

        assert parsed["EQUATION"] == "1+1=2"


class TestApplyOverrides:
    """Task 1.4: 命令行覆盖机制测试"""

    def test_simple_key_override(self, tmp_path):
        """测试简单键值对覆盖"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        config = manager.load_environment("staging")
        original_timeout = config.timeout

        manager.apply_overrides({"timeout": "60"})
        updated_config = manager.show_config(sanitize=False)

        assert updated_config["timeout"] == 60
        assert updated_config["timeout"] != original_timeout

    def test_nested_key_override(self, tmp_path):
        """测试嵌套键覆盖（如 headers.Authorization）"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        manager.load_environment("dev")
        manager.apply_overrides({"headers.Authorization": "Bearer new_token"})

        config = manager.show_config(sanitize=False)
        assert config["headers"]["Authorization"] == "Bearer new_token"

    def test_highest_priority_overrides(self, tmp_path):
        """测试命令行覆盖具有最高优先级"""
        config_data = {
            "defaults": {"timeout": 30},
            "environments": {
                "test": {
                    "base_url": "http://test.com",
                    "timeout": 50,
                },
            },
        }
        config_file = tmp_path / "priority.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        manager.apply_overrides({"timeout": "99"})

        config = manager.load_environment("test")

        # 命令行覆盖 > 环境配置 > defaults
        assert config.timeout == 99

    def test_multiple_overrides(self, tmp_path):
        """测试同时应用多个覆盖"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        manager.load_environment("dev")
        manager.apply_overrides(
            {
                "timeout": "100",
                "base_url": "http://overridden.com",
                "headers.X-Custom": "custom_value",
            }
        )

        config = manager.show_config(sanitize=False)
        assert config["timeout"] == 100
        assert config["base_url"] == "http://overridden.com"
        assert config["headers"]["X-Custom"] == "custom_value"

    def test_override_creates_new_nested_dict(self, tmp_path):
        """测试覆盖创建新的嵌套字典"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        manager.load_environment("staging")
        # staging 没有 extra 字段
        manager.apply_overrides({"extra.new_key": "new_value"})

        config = manager.show_config(sanitize=False)
        # 非标准嵌套字段会被存入 variables 中
        assert "variables" in config
        assert "extra" in config["variables"]
        assert config["variables"]["extra"]["new_key"] == "new_value"

    def test_timeout_type_conversion(self, tmp_path):
        """测试 timeout 的类型转换"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        manager.load_environment("dev")
        manager.apply_overrides({"timeout": "45"})

        config = manager._current_config
        assert isinstance(config.timeout, int)
        assert config.timeout == 45

    def test_invalid_timeout_keeps_string(self, tmp_path):
        """测试无效 timeout 值保持为字符串"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        manager.load_environment("dev")
        manager.apply_overrides({"timeout": "not_a_number"})

        config = manager._current_config
        assert config.timeout == "not_a_number"


class TestValidateEnvironment:
    """Task 1.5: 配置校验功能测试"""

    def test_validate_valid_environment(self, tmp_path):
        """测试校验通过的有效环境"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        errors = manager.validate_environment("dev")

        assert errors == []

    def test_validate_missing_base_url(self, tmp_path):
        """测试缺少 base_url 的校验"""
        config_data = {
            "environments": {
                "no_url": {
                    # 缺少 base_url
                    "timeout": 30,
                }
            }
        }
        config_file = tmp_path / "no_url.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        errors = manager.validate_environment("no_url")

        assert len(errors) > 0
        assert any("base_url" in error for error in errors)

    def test_validate_invalid_url_format(self, tmp_path):
        """测试无效 URL 格式的校验"""
        config_data = {
            "environments": {
                "bad_url": {
                    "base_url": "not-a-valid-url",
                }
            }
        }
        config_file = tmp_path / "bad_url.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        errors = manager.validate_environment("bad_url")

        assert len(errors) > 0
        assert any("URL 格式无效" in error for error in errors)

    def test_validate_undefined_variable_reference(self, tmp_path):
        """测试未定义变量引用的校验"""
        config_data = {
            "environments": {
                "undef_var": {
                    "base_url": "http://${undefined_var}.com",
                    "variables": {"defined_var": "value"},
                }
            }
        }
        config_file = tmp_path / "undef_var.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        errors = manager.validate_environment("undef_var")

        assert len(errors) > 0
        assert any("undefined_var" in error for error in errors)

    def test_validate_defined_variable_passes(self, tmp_path):
        """测试已定义变量的校验通过"""
        config_data = {
            "environments": {
                "def_var": {
                    "base_url": "http://${defined_var}.com",
                    "variables": {"defined_var": "api"},
                }
            }
        }
        config_file = tmp_path / "def_var.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        errors = manager.validate_environment("def_var")

        # 应该没有未定义变量的错误
        assert not any("未定义的变量引用" in error for error in errors)

    def test_validate_nonexistent_environment(self, tmp_path):
        """测试校验不存在的环境"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        errors = manager.validate_environment("ghost")

        assert len(errors) > 0
        assert any("不存在" in error for error in errors)

    def test_validate_multiple_errors(self, tmp_path):
        """测试多个错误的累积报告"""
        config_data = {
            "environments": {
                "multi_error": {
                    # 缺少 base_url
                    "timeout": "${undefined_timeout}",
                }
            }
        }
        config_file = tmp_path / "multi_error.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        errors = manager.validate_environment("multi_error")

        # 应该有至少2个错误：缺少base_url + 未定义变量
        assert len(errors) >= 2


class TestSanitization:
    """Task 1.6: 敏感信息脱敏显示测试"""

    def test_sanitize_api_key(self):
        """测试 API_KEY 后缀脱敏"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        result = manager._sanitize_value("MY_API_KEY", "sk_live_abcdef123456")

        assert "************" in result
        assert result.startswith("sk_live_")

    def test_sanitize_secret(self):
        """测试 SECRET 后缀脱敏"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        result = manager._sanitize_value("DB_SECRET", "super_secret_password")

        assert "************" in result

    def test_sanitize_password(self):
        """测试 PASSWORD 后缀脱敏"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        result = manager._sanitize_value("ADMIN_PASSWORD", "admin123")

        assert "************" in result

    def test_sanitize_token(self):
        """测试 TOKEN 后缀脱敏"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        result = manager._sanitize_value("AUTH_TOKEN", "bearer_token_xyz")

        assert "************" in result

    def test_sanitize_credential(self):
        """测试 CREDENTIAL 后缀脱敏"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        result = manager._sanitize_value("AWS_CREDENTIAL", "access_key+secret")

        assert "************" in result

    def test_no_sanitize_normal_value(self):
        """测试普通值不脱敏"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        result = manager._sanitize_value("BASE_URL", "http://example.com")

        assert result == "http://example.com"

    def test_no_sanitize_empty_value(self):
        """测试空值不脱敏"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        result = manager._sanitize_value("API_KEY", "")

        assert result == ""

    def test_no_sanitize_non_string(self):
        """测试非字符串值不脱敏"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        result = manager._sanitize_value("TIMEOUT", 30)

        assert result == 30

    def test_show_config_with_sanitization(self, tmp_path):
        """测试 show_config 自动应用脱敏"""
        config_data = {
            "environments": {
                "secure": {
                    "base_url": "https://secure.com",
                    "variables": {
                        "API_KEY": "secret_key_12345",
                        "PUBLIC_VAR": "public_value",
                    },
                }
            }
        }
        config_file = tmp_path / "secure.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        manager.load_environment("secure")
        sanitized = manager.show_config(sanitize=True)

        # API_KEY 应被脱敏
        assert "************" in sanitized["variables"]["API_KEY"]
        # PUBLIC_VAR 不应被脱敏
        assert sanitized["variables"]["PUBLIC_VAR"] == "public_value"

    def test_show_config_without_sanitization(self, tmp_path):
        """测试 show_config 可选择不脱敏"""
        config_data = {
            "environments": {
                "raw": {
                    "base_url": "https://raw.com",
                    "variables": {
                        "SECRET_KEY": "my_super_secret",
                    },
                }
            }
        }
        config_file = tmp_path / "raw.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        manager.load_environment("raw")
        raw_config = manager.show_config(sanitize=False)

        # 应显示原始值
        assert raw_config["variables"]["SECRET_KEY"] == "my_super_secret"

    def test_recursive_sanitization(self, tmp_path):
        """测试递归脱敏嵌套字典"""
        config_data = {
            "environments": {
                "nested": {
                    "base_url": "https://nested.com",
                    "variables": {
                        "DB_PASSWORD": "db_pass_123",
                        "NORMAL_VAR": "normal",
                    },
                }
            }
        }
        config_file = tmp_path / "nested.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        manager.load_environment("nested")
        sanitized = manager.show_config(sanitize=True)

        # variables 中的敏感字段应被脱敏
        assert "************" in sanitized["variables"]["DB_PASSWORD"]
        # 非敏感字段不应被脱敏
        assert sanitized["variables"]["NORMAL_VAR"] == "normal"

    def test_show_config_before_loading(self):
        """测试未加载配置时 show_config 返回错误"""
        manager = EnvironmentManager.__new__(EnvironmentManager)
        manager._current_config = None

        result = manager.show_config()

        assert "error" in result
        assert "未加载" in result["error"]


class TestDeepMerge:
    """深度合并工具方法测试"""

    def test_simple_merge(self):
        """测试简单字典合并"""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = EnvironmentManager._deep_merge(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self):
        """测试嵌套字典合并"""
        base = {"outer": {"inner1": "a", "inner2": "b"}}
        override = {"outer": {"inner2": "c", "inner3": "d"}}
        result = EnvironmentManager._deep_merge(base, override)

        assert result["outer"]["inner1"] == "a"
        assert result["outer"]["inner2"] == "c"
        assert result["outer"]["inner3"] == "d"

    def test_merge_does_not_mutate_original(self):
        """测试合并不修改原始字典"""
        base = {"a": {"x": 1}}
        override = {"a": {"y": 2}}

        result = EnvironmentManager._deep_merge(base, override)

        assert "y" not in base["a"]
        assert "x" not in override["a"]

    def test_merge_empty_override(self):
        """测试空覆盖字典"""
        base = {"a": 1, "b": 2}
        result = EnvironmentManager._deep_merge(base, {})

        assert result == base

    def test_merge_empty_base(self):
        """测试空基础字典"""
        override = {"a": 1}
        result = EnvironmentManager._deep_merge({}, override)

        assert result == override


class TestEdgeCases:
    """边界情况和异常处理测试"""

    def test_unicode_in_config(self, tmp_path):
        """测试配置中的 Unicode 字符"""
        config_data = {
            "environments": {
                "中文环境": {
                    "base_url": "http://中文.com",
                    "headers": {"X-描述": "这是一个测试"},
                }
            }
        }
        config_file = tmp_path / "unicode.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("中文环境")

        assert config.name == "中文环境"
        assert config.base_url == "http://中文.com"
        assert "X-描述" in config.headers

    test_unicode_in_config

    def test_special_characters_in_env_file(self, tmp_path):
        """测试 .env 文件中的特殊字符"""
        env_file = tmp_path / "special.env"
        env_file.write_text(
            """SPECIAL_CHARS=!@#$%^&*()
URL_WITH_PARAMS=http://example.com?foo=bar&baz=qux
JSON_VALUE={"key": "value"}
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager.__new__(EnvironmentManager)
        parsed = manager._load_env_file(env_file)

        assert "!" in parsed["SPECIAL_CHARS"]
        assert "?" in parsed["URL_WITH_PARAMS"]
        assert "{" in parsed["JSON_VALUE"]

    def test_large_number_of_environments(self, tmp_path):
        """测试大量环境的性能"""
        config_data = {
            "environments": {f"env_{i}": {"base_url": f"http://env{i}.com"} for i in range(100)}
        }
        config_file = tmp_path / "large.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        envs = manager.list_environments()

        assert len(envs) == 100
        config = manager.load_environment("env_50")
        assert config.base_url == "http://env50.com"

    def test_deeply_nested_configuration(self, tmp_path):
        """测试深度嵌套的配置"""
        config_data = {
            "defaults": {
                "level1": {
                    "level2": {
                        "level3": {
                            "value": "deep_default",
                        }
                    }
                }
            },
            "environments": {
                "deep": {
                    "base_url": "http://deep.com",
                    "level1": {
                        "level2": {
                            "level3": {
                                "value": "deep_override",
                                "extra": "added",
                            }
                        }
                    },
                }
            },
        }
        config_file = tmp_path / "deep_nest.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("deep")

        config_dict = config.to_dict()
        # 验证深度嵌套的合并结果（非标准字段会存入 variables）
        assert "variables" in config_dict
        assert "level1" in config_dict["variables"]
        nested_level1 = config_dict["variables"]["level1"]
        assert nested_level1["level2"]["level3"]["value"] == "deep_override"
        assert nested_level1["level2"]["level3"]["extra"] == "added"

    test_deeply_nested_configuration

    def test_reload_after_overrides(self, tmp_path):
        """测试重新加载后覆盖仍然有效"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        manager.load_environment("dev")
        manager.apply_overrides({"timeout": "999"})

        # 重新加载同一环境
        config = manager.load_environment("dev")

        assert config.timeout == 999

    def test_switch_environment_clears_previous(self, tmp_path):
        """测试切换环境后配置正确更新"""
        config_file = TestEnvironmentManagerInit._create_sample_config(tmp_path)
        manager = EnvironmentManager(str(config_file))

        dev_config = manager.load_environment("dev")
        staging_config = manager.load_environment("staging")

        assert dev_config.base_url != staging_config.base_url
        assert manager._current_config == staging_config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
