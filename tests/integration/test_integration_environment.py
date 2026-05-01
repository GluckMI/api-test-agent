"""
环境管理模块集成测试

覆盖范围：
- 端到端的环境切换流程
- --env 参数加载正确配置
- --var 覆盖生效验证
- --show-config 输出格式验证
- 配置文件与 .env 文件的协同工作

使用 pytest + tmp_path fixture 进行隔离测试
"""
import os
import sys
import json
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from environment import EnvironmentManager, EnvironmentConfig


class TestEnvironmentIntegration:
    """环境管理端到端集成测试"""

    def test_full_environment_loading_workflow(self, tmp_path):
        """测试完整的环境加载工作流：创建配置 → 加载环境 → 使用配置"""
        # Step 1: 创建完整的配置文件
        config_data = {
            "defaults": {
                "timeout": 30,
                "headers": {"Content-Type": "application/json"},
                "variables": {"common_var": "common_value"},
            },
            "environments": {
                "dev": {
                    "base_url": "http://localhost:8080/api",
                    "timeout": 10,
                    "headers": {"X-Env": "development"},
                    "variables": {"debug_mode": True},
                },
                "staging": {
                    "base_url": "https://staging.example.com/api",
                    "timeout": 30,
                    "headers": {"X-Env": "staging"},
                    "variables": {"debug_mode": False},
                },
            },
        }
        
        config_file = tmp_path / "configs" / "environments.yaml"
        config_file.parent.mkdir()
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)

        # Step 2: 初始化并加载 dev 环境
        manager = EnvironmentManager(str(config_file))
        dev_config = manager.load_environment("dev")

        assert isinstance(dev_config, EnvironmentConfig)
        assert dev_config.name == "dev"
        assert dev_config.base_url == "http://localhost:8080/api"
        assert dev_config.timeout == 10
        assert dev_config.variables["debug_mode"] is True
        assert dev_config.headers["X-Env"] == "development"

        # Step 3: 切换到 staging 环境
        staging_config = manager.load_environment("staging")

        assert staging_config.name == "staging"
        assert staging_config.base_url == "https://staging.example.com/api"
        assert staging_config.timeout == 30
        assert staging_config.variables["debug_mode"] is False

        # Step 4: 验证切换后配置完全独立
        assert dev_config.base_url != staging_config.base_url
        assert manager._current_config == staging_config

    def test_env_parameter_loading_with_env_file(self, tmp_path):
        """测试 --env 参数配合 .env 文件加载"""
        config_file = tmp_path / "configs" / "environments.yaml"
        config_file.parent.mkdir()
        config_file.write_text(
            """
environments:
  test_env:
    base_url: http://test.com
""",
            encoding="utf-8",
        )

        env_file = tmp_path / "configs" / ".env.test_env"
        env_file.write_text(
            """TEST_API_KEY=test_secret_123
TEST_DB_HOST=db.test.com
DEBUG_MODE=true
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("test_env")

        assert config.base_url == "http://test.com"
        assert config.env_variables.get("TEST_API_KEY") == "test_secret_123"
        assert config.env_variables.get("TEST_DB_HOST") == "db.test.com"
        assert config.env_variables.get("DEBUG_MODE") == "true"

    def test_command_line_override_effectiveness(self, tmp_path):
        """测试 --var 命令行参数覆盖是否正确生效"""
        config_file = tmp_path / "environments.yaml"
        config_file.write_text(
            """
defaults:
  timeout: 30
environments:
  prod:
    base_url: https://api.prod.com
    timeout: 60
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager(str(config_file))

        # 加载原始配置
        original_config = manager.load_environment("prod")
        assert original_config.timeout == 60

        # 应用命令行覆盖
        manager.apply_overrides({
            "timeout": "120",
            "base_url": "https://override.prod.com",
            "headers.X-Custom": "custom_value",
        })

        overridden_config = manager.show_config(sanitize=False)

        assert overridden_config["timeout"] == 120
        assert overridden_config["base_url"] == "https://override.prod.com"
        assert overridden_config["headers"]["X-Custom"] == "custom_value"

    def test_show_config_output_format(self, tmp_path):
        """测试 --show-config 输出的格式和内容完整性"""
        config_data = {
            "environments": {
                "demo": {
                    "base_url": "http://demo.com",
                    "timeout": 45,
                    "headers": {"Authorization": "Bearer secret_token"},
                    "variables": {
                        "PUBLIC_VAR": "public_value",
                        "SECRET_KEY": "super_secret_password",
                    },
                }
            }
        }
        
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        manager.load_environment("demo")

        # 测试脱敏输出
        sanitized = manager.show_config(sanitize=True)
        
        assert isinstance(sanitized, dict)
        assert "name" in sanitized
        assert "base_url" in sanitized
        assert "timeout" in sanitized
        assert "headers" in sanitized
        assert "variables" in sanitized
        assert "env_variables" in sanitized
        
        # 敏感信息应被脱敏
        assert "************" in sanitized["headers"]["Authorization"]
        assert "************" in sanitized["variables"]["SECRET_KEY"]
        
        # 公开信息应保持原样
        assert sanitized["variables"]["PUBLIC_VAR"] == "public_value"

        # 测试未脱敏输出
        raw = manager.show_config(sanitize=False)
        assert raw["headers"]["Authorization"] == "Bearer secret_token"
        assert raw["variables"]["SECRET_KEY"] == "super_secret_password"

    def test_environment_switching_preserves_overrides(self, tmp_path):
        """测试环境切换时命令行覆盖是否保持有效"""
        config_file = tmp_path / "multi_env.yaml"
        config_file.write_text(
            """
defaults:
  timeout: 30
environments:
  env_a:
    base_url: http://a.com
    timeout: 20
  env_b:
    base_url: http://b.com
    timeout: 40
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager(str(config_file))

        # 加载 env_a 并应用覆盖
        manager.load_environment("env_a")
        manager.apply_overrides({"timeout": "99"})
        
        assert manager._current_config.timeout == 99

        # 切换到 env_b，覆盖应该仍然存在
        config_b = manager.load_environment("env_b")
        assert config_b.timeout == 99

    def test_complex_variable_references_in_configuration(self, tmp_path):
        """测试配置中复杂的变量引用场景"""
        config_data = {
            "defaults": {
                "variables": {
                    "api_host": "api",
                    "version": "v2",
                    "domain": "example.com",
                }
            },
            "environments": {
                "complex": {
                    "base_url": "https://${api_host}.${domain}/${version}",
                    "variables": {
                        "full_url": "${api_host}.${domain}",
                        "endpoint_prefix": "/${version}/users",
                    }
                }
            }
        }
        
        config_file = tmp_path / "complex.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("complex")

        assert config.base_url == "https://${api_host}.${domain}/${version}"
        assert config.variables["full_url"] == "${api_host}.${domain}"
        assert config.variables["endpoint_prefix"] == "/${version}/users"

    def test_validation_integration(self, tmp_path):
        """测试配置校验功能的实际使用"""
        valid_config = {
            "environments": {
                "valid_env": {
                    "base_url": "https://valid.example.com/api",
                    "timeout": 30,
                    "variables": {"defined_var": "value"},
                }
            }
        }
        
        invalid_config = {
            "environments": {
                "invalid_url_env": {
                    "base_url": "not-a-url",
                },
                "missing_url_env": {
                    "timeout": 30,
                },
                "undef_var_env": {
                    "base_url": "http://${undefined}.com",
                }
            }
        }

        # 测试通过校验的环境
        valid_file = tmp_path / "valid.yaml"
        with open(valid_file, "w", encoding="utf-8") as f:
            yaml.dump(valid_config, f)
        
        manager_valid = EnvironmentManager(str(valid_file))
        errors = manager_valid.validate_environment("valid_env")
        assert errors == []

        # 测试未通过校验的环境
        invalid_file = tmp_path / "invalid.yaml"
        with open(invalid_file, "w", encoding="utf-8") as f:
            yaml.dump(invalid_config, f)
        
        manager_invalid = EnvironmentManager(str(invalid_file))

        url_errors = manager_invalid.validate_environment("invalid_url_env")
        assert any("URL 格式无效" in e for e in url_errors)

        missing_errors = manager_invalid.validate_environment("missing_url_env")
        assert any("base_url" in e for e in missing_errors)

        var_errors = manager_invalid.validate_environment("undef_var_env")
        assert any("未定义的变量引用" in e for e in var_errors)


class TestEnvironmentConfigFileFormats:
    """不同配置文件格式的兼容性测试"""

    def test_yaml_with_unicode_content(self, tmp_path):
        """测试包含 Unicode 内容的 YAML 配置"""
        config_data = {
            "environments": {
                "中文环境": {
                    "base_url": "http://中文测试.com/api",
                    "headers": {
                        "X-描述": "这是一个测试环境",
                        "X-作者": "张三",
                    },
                    "variables": {
                        "说明": "用于演示 Unicode 支持",
                    }
                }
            }
        }
        
        config_file = tmp_path / "unicode.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("中文环境")

        assert config.name == "中文环境"
        assert "中文测试.com" in config.base_url
        assert config.headers["X-描述"] == "这是一个测试环境"

    def test_minimal_configuration(self, tmp_path):
        """测试最小化配置（仅必需字段）"""
        config_file = tmp_path / "minimal.yaml"
        config_file.write_text(
            """
environments:
  minimal:
    base_url: http://minimal.com
""",
            encoding="utf-8",
        )

        manager = EnvironmentManager(str(config_file))
        config = manager.load_environment("minimal")

        assert config.base_url == "http://minimal.com"
        assert config.timeout == 30  # 默认值
        assert config.headers == {}  # 空


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
