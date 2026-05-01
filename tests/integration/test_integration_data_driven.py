"""
数据驱动引擎模块集成测试

覆盖范围：
- CSV 数据源加载和用例生成
- JSON 数据源加载（包括嵌套结构）
- 参数化替换正确性
- 错误处理（文件缺失、格式错误等）
- 过滤条件和用例命名模板
"""
import os
import sys
import json
import csv
from pathlib import Path
from io import StringIO

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_driver import DataDriver, DataSourceConfig, TemplateExpander, TestCase


class TestCSVDataLoading:
    """CSV 数据源加载集成测试"""

    def test_load_csv_and_generate_test_cases(self, tmp_path):
        """测试加载 CSV 文件并生成测试用例"""
        csv_content = """username,password,expected_status,test_name
admin,Admin123,200,正常登录
testuser,WrongPass,401,密码错误
empty,,400,空密码
"""
        
        csv_file = tmp_path / "test_cases.csv"
        csv_file.write_text(csv_content, encoding="utf-8")
        
        driver = DataDriver()
        config = DataSourceConfig(
            type="csv",
            file=str(csv_file),
            case_name_template="登录_{data.test_name}"
        )
        
        template = {
            "name": "登录测试",
            "steps": [
                {
                    "name": "执行登录",
                    "method": "POST",
                    "endpoint": "/auth/login",
                    "json": {
                        "username": "${data.username}",
                        "password": "${data.password}"
                    },
                    "assertions": [
                        {"type": "status_code", "expected": "${data.expected_status}"}
                    ]
                }
            ]
        }
        
        test_cases = driver.generate_test_cases(config, template)
        
        assert len(test_cases) == 3
        
        # 验证第一个用例
        assert test_cases[0].name == "登录_正常登录"
        assert test_cases[0].config["steps"][0]["json"]["username"] == "admin"
        assert test_cases[0].config["steps"][0]["json"]["password"] == "Admin123"
        
        # 验证第二个用例
        assert test_cases[1].name == "登录_密码错误"
        assert test_cases[1].config["steps"][0]["json"]["password"] == "WrongPass"

    def test_csv_with_unicode_and_special_chars(self, tmp_path):
        """测试包含 Unicode 和特殊字符的 CSV"""
        csv_file = tmp_path / "unicode.csv"
        
        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'value', 'expected'])
            writer.writerow(['中文测试', '值1', 200])
            writer.writerow(['Special!@#%', '"quoted"', 201])
            writer.writerow(['Emoji😀', 'test🎉', 202])
        
        driver = DataDriver()
        config = DataSourceConfig(type="csv", file=str(csv_file))
        template = {"steps": [{"method": "GET", "endpoint": "/${data.name}"}]}
        
        test_cases = driver.generate_test_cases(config, template)
        
        assert len(test_cases) == 3
        assert '中文测试' in test_cases[0].config['steps'][0]['endpoint']
        assert 'Special!@#%' in test_cases[1].config['steps'][0]['endpoint']
        assert 'Emoji' in test_cases[2].config['steps'][0]['endpoint']


class TestJSONDataLoading:
    """JSON 数据源加载集成测试"""

    def test_load_json_array_and_generate_cases(self, tmp_path):
        """测试加载 JSON 数组格式的数据源"""
        data = [
            {
                "username": "user1",
                "email": "user1@test.com",
                "role": "admin",
                "expected_status": 201,
                "profile": {
                    "nickname": "管理员",
                    "avatar": "admin.png"
                }
            },
            {
                "username": "user2",
                "email": "user2@test.com",
                "role": "user",
                "expected_status": 201,
                "profile": {
                    "nickname": "普通用户",
                    "avatar": "user.png"
                }
            }
        ]
        
        json_file = tmp_path / "register_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        driver = DataDriver()
        config = DataSourceConfig(
            type="json",
            file=str(json_file),
            case_name_template="注册_{data.username}"
        )
        
        template = {
            "name": "注册测试",
            "steps": [
                {
                    "name": "提交注册",
                    "method": "POST",
                    "endpoint": "/auth/register",
                    "json": {
                        "username": "${data.username}",
                        "email": "${data.email}",
                        "role": "${data.role}",
                        "profile": {
                            "nickname": "${data.profile.nickname}",
                            "avatar": "${data.profile.avatar}"
                        }
                    },
                    "assertions": [
                        {"type": "status_code", "expected": "${data.expected_status}"}
                    ]
                }
            ]
        }
        
        test_cases = driver.generate_test_cases(config, template)
        
        assert len(test_cases) == 2
        assert test_cases[0].name == "注册_user1"
        assert test_cases[1].name == "注册_user2"
        
        # 验证嵌套字段替换
        case1_step = test_cases[0].config['steps'][0]
        assert case1_step['json']['profile']['nickname'] == '管理员'
        assert case1_step['json']['profile']['avatar'] == 'admin.png'

    def test_load_json_object_with_array_field(self, tmp_path):
        """测试加载包含数组字段的 JSON 对象"""
        data = {
            "metadata": {
                "version": "1.0",
                "author": "test"
            },
            "test_cases": [
                {"id": 1, "input": "a", "expected": "A"},
                {"id": 2, "input": "b", "expected": "B"}
            ]
        }
        
        json_file = tmp_path / "object_format.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        driver = DataDriver()
        config = DataSourceConfig(type="json", file=str(json_file))
        template = {"steps": [{"method": "GET", "endpoint": "/${data.id}"}]}
        
        test_cases = driver.generate_test_cases(config, template)
        
        # 应该自动找到 test_cases 数组
        assert len(test_cases) == 2
        assert test_cases[0].config['steps'][0]['endpoint'] == '/1'
        assert test_cases[1].config['steps'][0]['endpoint'] == '/2'


class TestParameterReplacement:
    """参数化替换正确性测试"""

    def test_basic_placeholder_replacement(self):
        """测试基本的占位符替换"""
        expander = TemplateExpander()
        
        template = {
            "name": "测试模板",
            "endpoint": "/users/${data.user_id}",
            "params": {
                "page": "${data.page}",
                "size": "${data.size}"
            },
            "headers": {
                "X-Token": "${data.token}"
            }
        }
        
        data_row = {
            "user_id": 42,
            "page": 1,
            "size": 20,
            "token": "abc123xyz"
        }
        
        result = expander.expand_template(template, data_row)
        
        assert result["endpoint"] == "/users/42"
        assert result["params"]["page"] == "1"
        assert result["params"]["size"] == "20"
        assert result["headers"]["X-Token"] == "abc123xyz"

    def test_nested_structure_replacement(self):
        """测试嵌套结构的递归替换"""
        expander = TemplateExpander()
        
        template = {
            "request": {
                "method": "POST",
                "url": "${data.base_url}/api/${data.version}/users",
                "body": {
                    "user": {
                        "name": "${data.username}",
                        "profile": {
                            "age": "${data.age}",
                            "city": "${data.city}"
                        }
                    },
                    "metadata": {
                        "timestamp": "${data.timestamp}"
                    }
                }
            }
        }
        
        data_row = {
            "base_url": "https://api.example.com",
            "version": "v2",
            "username": "张三",
            "age": 25,
            "city": "北京",
            "timestamp": "2026-01-01T00:00:00Z"
        }
        
        result = expander.expand_template(template, data_row)
        
        assert result["request"]["url"] == "https://api.example.com/api/v2/users"
        assert result["request"]["body"]["user"]["name"] == "张三"
        assert result["request"]["body"]["user"]["profile"]["city"] == "北京"

    def test_list_replacement(self):
        """测试列表中的占位符替换"""
        expander = TemplateExpander()
        
        template = {
            "tags": ["${data.tag1}", "${data.tag2}", "${data.tag3}"],
            "ids": [1, 2, "${data.dynamic_id}"]
        }
        
        data_row = {
            "tag1": "python",
            "tag2": "testing",
            "tag3": "api",
            "dynamic_id": 99
        }
        
        result = expander.expand_template(template, data_row)
        
        assert result["tags"] == ["python", "testing", "api"]
        assert result["ids"] == [1, 2, "99"]

    def test_undefined_variable_preserved(self):
        """测试未定义变量保留原占位符"""
        expander = TemplateExpander()
        
        template = {
            "endpoint": "/${data.defined}/${data.undefined}"
        }
        
        data_row = {"defined": "value"}
        
        result = expander.expand_template(template, data_row)
        
        assert result["endpoint"] == "/value/${data.undefined}"


class TestErrorHandling:
    """错误处理集成测试"""

    def test_missing_csv_file_error(self, tmp_path):
        """测试 CSV 文件不存在时的错误"""
        driver = DataDriver()
        config = DataSourceConfig(
            type="csv",
            file=str(tmp_path / "nonexistent.csv")
        )
        
        with pytest.raises(FileNotFoundError) as exc_info:
            driver.generate_test_cases(config, {})
        
        assert "数据源文件不存在" in str(exc_info.value)

    def test_invalid_json_format_error(self, tmp_path):
        """测试无效 JSON 格式的错误"""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{invalid json content", encoding="utf-8")
        
        driver = DataDriver()
        config = DataSourceConfig(type="json", file=str(invalid_json))
        
        with pytest.raises(ValueError) as exc_info:
            driver.generate_test_cases(config, {})
        
        assert "解析失败" in str(exc_info.value)

    def test_unsupported_data_source_type(self, tmp_path):
        """测试不支持的数据源类型"""
        driver = DataDriver()
        config = DataSourceConfig(type="xml", file="test.xml")
        
        with pytest.raises(ValueError) as exc_info:
            driver.generate_test_cases(config, {})
        
        assert "不支持的数据源类型" in str(exc_info.value)

    def test_empty_csv_generates_no_cases(self, tmp_path):
        """测试空 CSV 文件不生成用例"""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("header1,header2\n", encoding="utf-8")
        
        driver = DataDriver()
        config = DataSourceConfig(type="csv", file=str(csv_file))
        
        test_cases = driver.generate_test_cases(config, {})
        
        assert len(test_cases) == 0


class TestCaseNameTemplate:
    """用例命名模板测试"""

    def test_dynamic_naming_with_variables(self, tmp_path):
        """测试使用数据变量动态命名"""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,status\ntest_a,200\ntest_b,404\n", encoding="utf-8")
        
        driver = DataDriver()
        config = DataSourceConfig(
            type="csv",
            file=str(csv_file),
            case_name_template="Case_{data.name}_Status{data.status}_{row_index}"
        )
        
        test_cases = driver.generate_test_cases(config, {})
        
        assert test_cases[0].name == "Case_test_a_Status200_0"
        assert test_cases[1].name == "Case_test_b_Status404_1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
