"""
数据驱动引擎模块单元测试
覆盖：CSV 解析、JSON 解析、模板展开、用例生成、错误处理
"""
import os
import sys
import json
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api_test_agent.data_driver import (
    DataSourceConfig,
    DataDriver,
    TemplateExpander,
    TestCase
)


class TestDataSourceConfig:
    """测试 DataSourceConfig 数据类"""

    def test_default_values(self):
        config = DataSourceConfig(type="csv", file="test.csv")
        assert config.type == "csv"
        assert config.file == "test.csv"
        assert config.mapping == {}
        assert config.filter is None
        assert config.case_name_template == "{name}_{row_index}"

    def test_custom_values(self):
        config = DataSourceConfig(
            type="json",
            file="data.json",
            mapping={"id": "user_id"},
            filter={"status": "active"},
            case_name_template="test_{data.username}"
        )
        assert config.mapping == {"id": "user_id"}
        assert config.filter == {"status": "active"}
        assert config.case_name_template == "test_{data.username}"


class TestCSVParsing:
    """测试 CSV 数据源解析器"""

    def setup_method(self):
        self.driver = DataDriver()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_csv(self, content: str, filename: str = "test.csv", encoding: str = 'utf-8') -> str:
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding=encoding, newline='') as f:
            f.write(content)
        return filepath

    def test_normal_csv_parsing(self):
        csv_content = "username,password,expected_status\nadmin,123456,200\nguest,guest,403\n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(type="csv", file=filepath)
        rows = self.driver._load_data_source(config)
        assert len(rows) == 2
        assert rows[0] == {"username": "admin", "password": "123456", "expected_status": "200"}
        assert rows[1] == {"username": "guest", "password": "guest", "expected_status": "403"}

    def test_empty_csv_file(self):
        csv_content = ""
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(type="csv", file=filepath)
        rows = self.driver._load_data_source(config)
        assert rows == []

    def test_header_only_csv(self):
        csv_content = "col1,col2,col3\n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(type="csv", file=filepath)
        rows = self.driver._load_data_source(config)
        assert rows == []

    def test_bom_encoding_csv(self):
        filepath = os.path.join(self.temp_dir, "bom.csv")
        with open(filepath, 'wb') as f:
            f.write(b'\xef\xbb\xbfname,value\ntest1,100\n')
        config = DataSourceConfig(type="csv", file=filepath)
        rows = self.driver._load_data_source(config)
        assert len(rows) == 1
        assert rows[0]["name"] == "test1"

    def test_special_characters_in_csv(self):
        csv_content = 'name,description,value\n"test,with comma","line1\nline2","quote""inside"\n'
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(type="csv", file=filepath)
        rows = self.driver._load_data_source(config)
        assert len(rows) == 1
        assert rows[0]["name"] == "test,with comma"
        assert rows[0]["description"] == "line1\nline2"
        assert rows[0]['value'] == 'quote"inside'

    def test_whitespace_trimming(self):
        csv_content = "name,value\n  hello  ,  world  \n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(type="csv", file=filepath)
        rows = self.driver._load_data_source(config)
        assert rows[0]["name"] == "hello"
        assert rows[0]["value"] == "world"

    def test_file_not_found_error(self):
        config = DataSourceConfig(type="csv", file="/nonexistent/path/data.csv")
        with pytest.raises(FileNotFoundError) as exc_info:
            self.driver._load_data_source(config)
        assert "数据源文件不存在" in str(exc_info.value)


class TestJSONParsing:
    """测试 JSON 数据源解析器"""

    def setup_method(self):
        self.driver = DataDriver()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_json(self, data, filename: str = "test.json") -> str:
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return filepath

    def test_json_array_format(self):
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        filepath = self._create_json(data)
        config = DataSourceConfig(type="json", file=filepath)
        rows = self.driver._load_data_source(config)
        assert len(rows) == 2
        assert rows[0] == {"id": 1, "name": "Alice"}

    def test_json_object_format(self):
        data = {"users": [{"id": 1}, {"id": 2}]}
        filepath = self._create_json(data)
        config = DataSourceConfig(type="json", file=filepath)
        rows = self.driver._load_data_source(config)
        assert len(rows) == 2

    def test_empty_json_array(self):
        data = []
        filepath = self._create_json(data)
        config = DataSourceConfig(type="json", file=filepath)
        rows = self.driver._load_data_source(config)
        assert rows == []

    def test_nested_json_structure(self):
        data = [
            {
                "user": {"name": "Alice", "age": 30},
                "tags": ["admin", "tester"]
            }
        ]
        filepath = self._create_json(data)
        config = DataSourceConfig(type="json", file=filepath)
        rows = self.driver._load_data_source(config)
        assert len(rows) == 1
        assert rows[0]["user"]["name"] == "Alice"

    def test_invalid_json_syntax(self):
        filepath = os.path.join(self.temp_dir, "bad.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("{invalid json}")
        config = DataSourceConfig(type="json", file=filepath)
        with pytest.raises(ValueError) as exc_info:
            self.driver._load_data_source(config)
        assert "解析 JSON 文件失败" in str(exc_info.value)

    def test_unsupported_type_error(self):
        config = DataSourceConfig(type="xml", file="test.xml")
        with pytest.raises(ValueError) as exc_info:
            self.driver._load_data_source(config)
        assert "不支持的数据源类型" in str(exc_info.value)


class TestTemplateExpander:
    """测试模板参数化引擎"""

    def setup_method(self):
        self.expander = TemplateExpander()

    def test_simple_value_replacement(self):
        template = {"endpoint": "/api/users/${data.user_id}"}
        data_row = {"user_id": "123"}
        result = self.expander.expand_template(template, data_row)
        assert result["endpoint"] == "/api/users/123"

    def test_multiple_placeholders(self):
        template = {
            "endpoint": "/api/${data.resource}/${data.id}",
            "params": {"page": "${data.page}", "size": "${data.size}"}
        }
        data_row = {"resource": "users", "id": "456", "page": "1", "size": "10"}
        result = self.expander.expand_template(template, data_row)
        assert result["endpoint"] == "/api/users/456"
        assert result["params"] == {"page": "1", "size": "10"}

    def test_nested_dict_replacement(self):
        template = {
            "request": {
                "headers": {"Authorization": "Bearer ${data.token}"},
                "body": {"user_id": "${data.uid}"}
            }
        }
        data_row = {"token": "abc123", "uid": "789"}
        result = self.expander.expand_template(template, data_row)
        assert result["request"]["headers"]["Authorization"] == "Bearer abc123"
        assert result["request"]["body"]["user_id"] == "789"

    def test_list_replacement(self):
        template = {
            "assertions": [
                {"field": "status", "expected": "${data.expected_status}"},
                {"field": "message", "contains": "${data.keyword}"}
            ]
        }
        data_row = {"expected_status": "200", "keyword": "success"}
        result = self.expander.expand_template(template, data_row)
        assert result["assertions"][0]["expected"] == "200"
        assert result["assertions"][1]["contains"] == "success"

    def test_none_value_handling(self):
        template = {"value": "${data.missing_field}", "other": "static"}
        data_row = {}
        result = self.expander.expand_template(template, data_row)
        assert result["value"] == "${data.missing_field}"
        assert result["other"] == "static"

    def test_none_value_in_data(self):
        template = {"field": "${data.optional}"}
        data_row = {"optional": None}
        result = self.expander.expand_template(template, data_row)
        assert result["field"] == "${data.optional}"

    def test_no_placeholder_preserved(self):
        template = {"static": "no variables here"}
        data_row = {"any": "value"}
        result = self.expander.expand_template(template, data_row)
        assert result["static"] == "no variables here"

    def test_deep_copy_protection(self):
        original = {"nested": {"key": "${data.val}"}}
        data_row = {"val": "replaced"}
        result = self.expander.expand_template(original, data_row)
        assert original["nested"]["key"] == "${data.val}"
        assert result["nested"]["key"] == "replaced"

    def test_complex_test_case_template(self):
        template = {
            "name": "API Test",
            "steps": [
                {
                    "name": "Get User",
                    "method": "GET",
                    "endpoint": "/api/users/${data.user_id}",
                    "assertions": [
                        {"type": "status_code", "expected": "${data.expected_code}"}
                    ]
                }
            ]
        }
        data_row = {"user_id": "42", "expected_code": "200"}
        result = self.expander.expand_template(template, data_row)
        assert result["steps"][0]["endpoint"] == "/api/users/42"
        assert result["steps"][0]["assertions"][0]["expected"] == "200"


class TestCaseGeneration:
    """测试用例批量生成逻辑"""

    def setup_method(self):
        self.driver = DataDriver()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_csv(self, content: str) -> str:
        filepath = os.path.join(self.temp_dir, "data.csv")
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        return filepath

    def test_generate_correct_count(self):
        csv_content = "id,name\n1,Alice\n2,Bob\n3,Charlie\n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(type="csv", file=filepath)
        template = {"name": "Test"}
        cases = self.driver.generate_test_cases(config, template)
        assert len(cases) == 3

    def test_dynamic_case_names(self):
        csv_content = "username\nadmin\nguest\n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(
            type="csv",
            file=filepath,
            case_name_template="login_{data.username}"
        )
        template = {"name": "Test"}
        cases = self.driver.generate_test_cases(config, template)
        assert cases[0].name == "login_admin"
        assert cases[1].name == "login_guest"

    def test_filter_condition_applied(self):
        csv_content = "role,status\nadmin,active\nuser,inactive\nmoderator,active\n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(
            type="csv",
            file=filepath,
            filter={"status": "active"},
            case_name_template="{data.role}_{data.status}"
        )
        template = {"name": "Test"}
        cases = self.driver.generate_test_cases(config, template)
        assert len(cases) == 2
        case_names = [c.name for c in cases]
        assert "admin_active" in case_names
        assert "moderator_active" in case_names

    def test_filter_excludes_all(self):
        csv_content = "status\ninactive\ninactive\n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(
            type="csv",
            file=filepath,
            filter={"status": "active"}
        )
        template = {"name": "Test"}
        cases = self.driver.generate_test_cases(config, template)
        assert len(cases) == 0

    def test_generated_cases_contain_expanded_data(self):
        csv_content = "user_id,code\n100,201\n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(type="csv", file=filepath)
        template = {
            "endpoint": "/api/users/${data.user_id}",
            "expected": "${data.code}"
        }
        cases = self.driver.generate_test_cases(config, template)
        assert len(cases) == 1
        assert cases[0].config["endpoint"] == "/api/users/100"
        assert cases[0].config["expected"] == "201"

    def test_row_index_in_name(self):
        csv_content = "val\na\nb\nc\n"
        filepath = self._create_csv(csv_content)
        config = DataSourceConfig(
            type="csv",
            file=filepath,
            case_name_template="test_{row_index}"
        )
        template = {"name": "Test"}
        cases = self.driver.generate_test_cases(config, template)
        assert cases[0].name == "test_0"
        assert cases[1].name == "test_1"
        assert cases[2].name == "test_2"


class TestErrorHandling:
    """测试错误处理场景"""

    def setup_method(self):
        self.driver = DataDriver()

    def test_missing_csv_file_raises_file_not_found(self):
        config = DataSourceConfig(type="csv", file="/nonexistent/file.csv")
        with pytest.raises(FileNotFoundError):
            self.driver._load_data_source(config)

    def test_invalid_json_format_raises_value_error(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write('not valid json {{{')
            filepath = f.name
        try:
            config = DataSourceConfig(type="json", file=filepath)
            with pytest.raises(ValueError) as exc_info:
                self.driver._load_data_source(config)
            assert "解析 JSON 文件失败" in str(exc_info.value)
        finally:
            os.unlink(filepath)

    def test_unsupported_data_source_type(self):
        config = DataSourceConfig(type="excel", file="data.xlsx")
        with pytest.raises(ValueError) as exc_info:
            self.driver._load_data_source(config)
        assert "不支持的数据源类型" in str(exc_info.value)

    def test_template_with_invalid_placeholder_kept_as_is(self):
        expander = TemplateExpander()
        template = {"field": "${malformed}"}
        data = {"key": "value"}
        result = expander.expand_template(template, data)
        assert result["field"] == "${malformed}"

    def test_empty_data_source_returns_empty_list(self):
        import tempfile, shutil
        temp_dir = tempfile.mkdtemp()
        try:
            filepath = os.path.join(temp_dir, "empty.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)
            config = DataSourceConfig(type="json", file=filepath)
            cases = self.driver.generate_test_cases(config, {"name": "Test"})
            assert cases == []
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
