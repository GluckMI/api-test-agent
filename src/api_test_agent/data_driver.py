"""
API 接口自动化测试 Agent - 数据驱动引擎模块
支持 CSV/JSON 数据源解析、模板参数化、用例批量生成
"""
import csv
import json
import re
import copy
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class DataSourceConfig:
    """数据源配置"""
    type: str  # 'csv' or 'json'
    file: str  # 数据文件路径
    mapping: Dict[str, str] = field(default_factory=dict)  # 列名映射（可选）
    filter: Optional[Dict[str, Any]] = None  # 过滤条件（可选）
    case_name_template: str = "{name}_{row_index}"  # 用例名称模板


@dataclass
class TestCase:
    """生成的测试用例"""
    name: str
    config: Dict[str, Any]


class TemplateExpander:
    """模板参数化引擎 - 负责将数据行中的值替换到模板中的占位符"""

    PLACEHOLDER_PATTERN = re.compile(r'\$\{data\.(\w+)\}')

    def expand_template(self, template: Dict, data_row: Dict) -> Dict:
        """
        展开模板，替换 ${data.column_name} 占位符

        Args:
            template: 测试用例模板（dict）
            data_row: 单行数据（dict）

        Returns:
            展开后的测试用例字典
        """
        result = copy.deepcopy(template)
        return self._replace_placeholders(result, data_row)

    def _replace_placeholders(self, obj: Any, data_row: Dict) -> Any:
        """递归替换占位符"""
        if isinstance(obj, str):
            return self._replace_in_string(obj, data_row)
        elif isinstance(obj, dict):
            return {k: self._replace_placeholders(v, data_row) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_placeholders(item, data_row) for item in obj]
        return obj

    def _replace_in_string(self, text: str, data_row: Dict) -> str:
        """替换单个字符串中的占位符"""

        def replacer(match):
            column_name = match.group(1)
            value = data_row.get(column_name)
            if value is None:
                return match.group(0)  # 保留原占位符
            return str(value)

        return self.PLACEHOLDER_PATTERN.sub(replacer, text)


class DataDriver:
    """数据驱动引擎 - 负责加载外部数据源并批量生成测试用例"""

    SUPPORTED_TYPES = {'csv', 'json', 'yaml', 'yml'}

    def __init__(self):
        self.logger = logging.getLogger("DataDriver")
        self.expander = TemplateExpander()

    def generate_test_cases(
        self,
        data_source_config: DataSourceConfig,
        template: Dict
    ) -> List[TestCase]:
        """
        根据数据源配置和模板批量生成测试用例

        Args:
            data_source_config: 数据源配置
            template: 测试用例模板

        Returns:
            生成的测试用例列表
        """
        data_rows = self._load_data_source(data_source_config)
        test_cases = []

        for index, row in enumerate(data_rows):
            if not self._apply_filter(row, data_source_config.filter):
                continue

            expanded_case = self.expander.expand_template(template, row)
            case_name = self._generate_case_name(
                data_source_config.case_name_template,
                row,
                index
            )

            if "name" not in expanded_case:
                expanded_case["name"] = case_name

            test_cases.append(TestCase(name=case_name, config=expanded_case))

        return test_cases

    def _load_data_source(self, config: DataSourceConfig) -> List[Dict]:
        """根据类型加载数据源"""
        source_type = config.type.lower()

        if source_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"不支持的数据源类型：{config.type}，支持的类型：{self.SUPPORTED_TYPES}")

        file_path = Path(config.file)

        if not file_path.exists():
            raise FileNotFoundError(f"数据源文件不存在：{file_path.absolute()}")

        if source_type == 'csv':
            return self._parse_csv(file_path)
        else:
            return self._parse_json(file_path)

    def _parse_csv(self, file_path: Path) -> List[Dict]:
        """
        解析 CSV 文件

        Args:
            file_path: CSV 文件路径

        Returns:
            解析后的数据列表（每行为一个 dict）
        """
        rows = []
        encodings_to_try = ['utf-8-sig', 'utf-8', 'gbk', 'latin-1']

        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as f:
                    reader = csv.DictReader(f)

                    if reader.fieldnames is None:
                        return []

                    headers = [h.strip() for h in reader.fieldnames]

                    for row_num, row in enumerate(reader, start=2):
                        cleaned_row = {}
                        for header in headers:
                            value = row.get(header, '')
                            cleaned_row[header] = value.strip() if isinstance(value, str) else value
                        rows.append(cleaned_row)

                self.logger.info(f"成功解析 CSV 文件：{file_path}（编码：{encoding}）")
                return rows

            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise ValueError(f"解析 CSV 文件失败 {file_path}：{e}")

        raise ValueError(f"无法解析 CSV 文件 {file_path}，尝试了所有编码均失败")

    def _parse_json(self, file_path: Path) -> List[Dict]:
        """
        解析 JSON/YAML 文件

        支持两种格式：
        - JSON 数组：直接使用每个元素
        - JSON 对象：使用某个 key 对应的数组

        Args:
            file_path: JSON/YAML 文件路径

        Returns:
            解析后的数据列表
        """
        content = file_path.read_text(encoding='utf-8')

        suffix = file_path.suffix.lower()
        if suffix in ('.yaml', '.yml'):
            import yaml
            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"解析 YAML 文件失败 {file_path}：{e}")
        else:
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"解析 JSON 文件失败 {file_path}（位置 {e.lineno}:{e.colno}）：{e.msg}")

        if data is None:
            return []

        if isinstance(data, list):
            if len(data) == 0:
                return []

            if not all(isinstance(item, dict) for item in data):
                first_non_dict = next((item for item in data if not isinstance(item, dict)), None)
                raise ValueError(
                    f"JSON 数组中的元素必须是字典类型，"
                    f"但发现 {type(first_non_dict).__name__} 类型"
                )

            return data

        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    if all(isinstance(item, dict) for item in value):
                        self.logger.info(f"使用 JSON 对象的 '{key}' 键作为数据源")
                        return value

            raise ValueError(
                f"JSON 对象格式错误：未找到可用的数组字段。"
                f"期望格式为 {{\"data\": [...]}} 或直接使用数组格式 [...]"
            )
        else:
            raise ValueError(
                f"不支持的 JSON 格式：期望数组或对象，但得到 {type(data).__name__}"
            )

    def _apply_filter(self, row: Dict, filter_config: Optional[Dict]) -> bool:
        """
        应用过滤条件

        Args:
            row: 数据行
            filter_config: 过滤条件配置

        Returns:
            是否通过过滤
        """
        if filter_config is None:
            return True

        for key, expected_value in filter_config.items():
            actual_value = row.get(key)
            if actual_value != expected_value:
                return False

        return True

    def _generate_case_name(
        self,
        template_str: str,
        row: Dict,
        index: int
    ) -> str:
        """
        根据模板生成用例名称

        支持的变量：
        - {name}: 原始名称
        - {row_index}: 行索引（从 0 开始）
        - {data.xxx}: 数据列的值

        Args:
            template_str: 名称模板字符串
            row: 数据行
            index: 行索引

        Returns:
            生成的用例名称
        """
        name = template_str.replace("{row_index}", str(index))

        for key, value in row.items():
            if value is not None:
                name = name.replace(f"{{data.{key}}}", str(value))

        name = name.replace("{name}", "")

        return name.strip(" _-")
