"""
API 接口自动化测试 Agent - 断言引擎

支持 15 种断言类型，包括：
- 基础断言：equal, not_equal, status_code, response_time
- 包含断言：contains, not_contains, contains_key
- 类型断言：type_check, length, regex_match
- 空值断言：is_not_none, is_none
- 范围断言：in_range
- v2.0 新增：json_schema, custom, database
"""
import re
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass

from .client import APIResponse


@dataclass
class AssertionResult:
    """断言结果"""
    name: str
    passed: bool
    message: str
    expected: Any = None
    actual: Any = None


class AssertionError(Exception):
    """自定义断言错误"""
    pass


class AssertEngine:
    """断言引擎类"""
    
    @staticmethod
    def equal(actual: Any, expected: Any, name: str = "相等性检查") -> AssertionResult:
        """检查值是否相等"""
        passed = actual == expected
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"期望 {expected}, 实际 {actual}" if not passed else "通过",
            expected=expected,
            actual=actual
        )
    
    @staticmethod
    def not_equal(actual: Any, expected: Any, name: str = "不相等检查") -> AssertionResult:
        """检查值是否不相等"""
        passed = actual != expected
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"期望不等于 {expected}, 但实际等于它" if not passed else "通过",
            expected=f"!={expected}",
            actual=actual
        )
    
    @staticmethod
    def status_code(response: APIResponse, expected_code: int, 
                   name: str = "状态码检查") -> AssertionResult:
        """检查 HTTP 状态码"""
        passed = response.status_code == expected_code
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"期望状态码 {expected_code}, 实际 {response.status_code}" if not passed else "通过",
            expected=expected_code,
            actual=response.status_code
        )
    
    @staticmethod
    def in_range(actual: float, min_val: float = None, max_val: float = None,
                name: str = "范围检查") -> AssertionResult:
        """检查值是否在范围内"""
        passed = True
        if min_val is not None and actual < min_val:
            passed = False
        if max_val is not None and actual > max_val:
            passed = False
        
        range_str = f"[{min_val}, {max_val}]" if min_val and max_val else \
                   f">={min_val}" if min_val else f"<={max_val}"
        
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"期望在{range_str}内，实际 {actual}" if not passed else "通过",
            expected=range_str,
            actual=actual
        )
    
    @staticmethod
    def contains(container: Any, item: Any, name: str = "包含检查") -> AssertionResult:
        """检查容器是否包含某项"""
        try:
            passed = item in container
        except TypeError:
            passed = False
        
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"期望 {container} 包含 {item}" if not passed else "通过",
            expected=item,
            actual=container
        )
    
    @staticmethod
    def not_contains(container: Any, item: Any, name: str = "不包含检查") -> AssertionResult:
        """检查容器是否不包含某项"""
        try:
            passed = item not in container
        except TypeError:
            passed = False
        
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"期望 {container} 不包含 {item}" if not passed else "通过",
            expected=f"!({item})",
            actual=container
        )
    
    @staticmethod
    def contains_key(container: Dict, key: str, name: str = "键检查") -> AssertionResult:
        """检查字典是否包含某个键"""
        passed = key in container
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"期望字典包含键 '{key}'" if not passed else "通过",
            expected=key,
            actual=list(container.keys()) if isinstance(container, dict) else container
        )
    
    @staticmethod
    def type_check(actual: Any, expected_type: type, 
                  name: str = "类型检查") -> AssertionResult:
        """检查类型"""
        passed = isinstance(actual, expected_type)
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"期望类型 {expected_type.__name__}, 实际 {type(actual).__name__}" if not passed else "通过",
            expected=expected_type.__name__,
            actual=type(actual).__name__
        )
    
    @staticmethod
    def length(container: Any, expected_length: int, 
             name: str = "长度检查") -> AssertionResult:
        """检查长度"""
        try:
            actual_length = len(container)
            passed = actual_length == expected_length
            return AssertionResult(
                name=name,
                passed=passed,
                message=f"期望长度 {expected_length}, 实际 {actual_length}" if not passed else "通过",
                expected=expected_length,
                actual=actual_length
            )
        except (TypeError, AttributeError):
            return AssertionResult(
                name=name,
                passed=False,
                message="对象没有长度属性",
                expected=expected_length,
                actual=None
            )
    
    @staticmethod
    def regex_match(text: str, pattern: str, name: str = "正则匹配") -> AssertionResult:
        """正则表达式匹配"""
        match = re.search(pattern, text)
        passed = match is not None
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"文本不匹配模式 '{pattern}'" if not passed else "通过",
            expected=pattern,
            actual=text
        )
    
    @staticmethod
    def is_not_none(value: Any, name: str = "非空检查") -> AssertionResult:
        """检查值不为 None"""
        passed = value is not None
        return AssertionResult(
            name=name,
            passed=passed,
            message="值为 None" if not passed else "通过",
            expected="not None",
            actual=value
        )
    
    @staticmethod
    def is_none(value: Any, name: str = "为空检查") -> AssertionResult:
        """检查值为 None"""
        passed = value is None
        return AssertionResult(
            name=name,
            passed=passed,
            message=f"值不为 None: {value}" if not passed else "通过",
            expected=None,
            actual=value
        )
    
    @staticmethod
    def json_schema(actual: Any, schema: Dict, name: str = "JSON Schema 检查") -> AssertionResult:
        """
        验证 JSON 数据是否符合指定的 Schema
        
        支持基本类型验证，无需安装 jsonschema 库
        
        Args:
            actual: 实际 JSON 数据
            schema: JSON Schema 定义
            name: 断言名称
        
        Returns:
            AssertionResult 断言结果
        """
        try:
            errors = AssertEngine._validate_schema(actual, schema)
            passed = len(errors) == 0
            
            if passed:
                return AssertionResult(
                    name=name,
                    passed=True,
                    message="JSON Schema 验证通过",
                    expected="schema valid",
                    actual="matched"
                )
            else:
                return AssertionResult(
                    name=name,
                    passed=False,
                    message=f"JSON Schema 验证失败: {'; '.join(errors)}",
                    expected="schema valid",
                    actual="; ".join(errors)
                )
        except Exception as e:
            return AssertionResult(
                name=name,
                passed=False,
                message=f"Schema 验证异常: {str(e)}",
                expected="schema valid",
                actual=str(e)
            )
    
    @staticmethod
    def _validate_schema(data: Any, schema: Dict, path: str = "$") -> List[str]:
        """
        递归验证 JSON 数据是否符合 Schema
        
        Args:
            data: 实际数据
            schema: Schema 定义
            path: 当前路径（用于错误信息）
        
        Returns:
            错误信息列表
        """
        errors = []
        
        # 类型检查
        if "type" in schema:
            type_errors = AssertEngine._check_type(data, schema["type"], path)
            errors.extend(type_errors)
            if type_errors:
                return errors  # 类型不匹配，跳过后续检查
        
        # 对象类型检查
        if isinstance(data, dict):
            # required 字段检查
            if "required" in schema:
                for req_field in schema["required"]:
                    if req_field not in data:
                        errors.append(f"{path}: 缺少必填字段 '{req_field}'")
            
            # properties 检查
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    if prop_name in data:
                        prop_errors = AssertEngine._validate_schema(
                            data[prop_name], prop_schema, f"{path}.{prop_name}"
                        )
                        errors.extend(prop_errors)
        
        # 数组类型检查
        elif isinstance(data, list):
            if "items" in schema:
                for i, item in enumerate(data):
                    item_errors = AssertEngine._validate_schema(
                        item, schema["items"], f"{path}[{i}]"
                    )
                    errors.extend(item_errors)
            
            # 数组长度检查
            if "minItems" in schema and len(data) < schema["minItems"]:
                errors.append(f"{path}: 数组长度 {len(data)} < 最小值 {schema['minItems']}")
            if "maxItems" in schema and len(data) > schema["maxItems"]:
                errors.append(f"{path}: 数组长度 {len(data)} > 最大值 {schema['maxItems']}")
        
        # 字符串类型检查
        elif isinstance(data, str):
            if "minLength" in schema and len(data) < schema["minLength"]:
                errors.append(f"{path}: 字符串长度 {len(data)} < 最小值 {schema['minLength']}")
            if "maxLength" in schema and len(data) > schema["maxLength"]:
                errors.append(f"{path}: 字符串长度 {len(data)} > 最大值 {schema['maxLength']}")
            if "pattern" in schema and not re.match(schema["pattern"], data):
                errors.append(f"{path}: 字符串不匹配模式 '{schema['pattern']}'")
        
        # 数字类型检查
        elif isinstance(data, (int, float)):
            if "minimum" in schema and data < schema["minimum"]:
                errors.append(f"{path}: 值 {data} < 最小值 {schema['minimum']}")
            if "maximum" in schema and data > schema["maximum"]:
                errors.append(f"{path}: 值 {data} > 最大值 {schema['maximum']}")
            if "enum" in schema and data not in schema["enum"]:
                errors.append(f"{path}: 值 {data} 不在枚举值 {schema['enum']} 中")
        
        return errors
    
    @staticmethod
    def _check_type(data: Any, expected_type: str, path: str) -> List[str]:
        """检查数据类型"""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return [f"{path}: 未知的 Schema 类型 '{expected_type}'"]
        
        # 特殊处理：JSON 的 number 包含 int 和 float
        if expected_type == "number":
            if not isinstance(data, (int, float)) or isinstance(data, bool):
                return [f"{path}: 期望类型 {expected_type}，实际 {type(data).__name__}"]
        elif expected_type == "integer":
            if not isinstance(data, int) or isinstance(data, bool):
                return [f"{path}: 期望类型 {expected_type}，实际 {type(data).__name__}"]
        elif not isinstance(data, expected_python_type):
            return [f"{path}: 期望类型 {expected_type}，实际 {type(data).__name__}"]
        
        return []
    
    @staticmethod
    def custom(actual: Any, check_func: Callable[[Any], tuple], name: str = "自定义断言") -> AssertionResult:
        """
        自定义断言函数
        
        Args:
            actual: 实际值
            check_func: 自定义检查函数，签名：(actual) -> (passed: bool, message: str)
            name: 断言名称
        
        Returns:
            AssertionResult 断言结果
        """
        try:
            passed, message = check_func(actual)
            return AssertionResult(
                name=name,
                passed=passed,
                message=message,
                expected="custom check",
                actual=str(actual)[:100]
            )
        except Exception as e:
            return AssertionResult(
                name=name,
                passed=False,
                message=f"自定义断言执行异常: {str(e)}",
                expected="custom check",
                actual=str(e)
            )
    
    @staticmethod
    def database(query_result: Any, expected_rows: int = None, 
                expected_value: Any = None, path: str = None,
                name: str = "数据库断言") -> AssertionResult:
        """
        数据库查询结果断言
        
        Args:
            query_result: SQL 查询结果（列表或单个值）
            expected_rows: 期望的行数
            expected_value: 期望的值
            path: 从结果中提取值的路径
            name: 断言名称
        
        Returns:
            AssertionResult 断言结果
        """
        try:
            # 行数检查
            if expected_rows is not None:
                if isinstance(query_result, (list, tuple)):
                    actual_rows = len(query_result)
                    if actual_rows != expected_rows:
                        return AssertionResult(
                            name=name,
                            passed=False,
                            message=f"期望 {expected_rows} 行，实际 {actual_rows} 行",
                            expected=expected_rows,
                            actual=actual_rows
                        )
                else:
                    return AssertionResult(
                        name=name,
                        passed=False,
                        message="查询结果不是列表/元组，无法检查行数",
                        expected=expected_rows,
                        actual=type(query_result).__name__
                    )
            
            # 值检查
            if expected_value is not None:
                value = query_result
                if path:
                    value = AssertEngine._get_value_by_path(query_result, path)
                
                if value != expected_value:
                    return AssertionResult(
                        name=name,
                        passed=False,
                        message=f"期望值 {expected_value}，实际 {value}",
                        expected=expected_value,
                        actual=value
                    )
            
            return AssertionResult(
                name=name,
                passed=True,
                message="数据库断言通过",
                expected="query result valid",
                actual="matched"
            )
        except Exception as e:
            return AssertionResult(
                name=name,
                passed=False,
                message=f"数据库断言执行异常: {str(e)}",
                expected="query result valid",
                actual=str(e)
            )
    
    @classmethod
    def validate_response(cls, response: APIResponse, assertions: List[Dict]) -> List[AssertionResult]:
        """
        根据配置验证响应
        
        Args:
            response: API 响应对象
            assertions: 断言配置列表，例如：
                [
                    {"type": "status_code", "expected": 200},
                    {"type": "contains_key", "key": "data"},
                    {"type": "response_time", "max": 1.0}
                ]
        """
        results = []
        
        for assertion in assertions:
            assert_type = assertion.get("type")
            
            # 通用断言（基于响应体）
            if assert_type == "equal":
                # 需要从 JSON 路径提取值
                value = cls._get_value_by_path(response.body, assertion.get("path"))
                result = cls.equal(value, assertion.get("expected"), assertion.get("name", "值检查"))
            elif assert_type == "not_equal":
                value = cls._get_value_by_path(response.body, assertion.get("path"))
                result = cls.not_equal(value, assertion.get("expected"), assertion.get("name", "不等检查"))
            elif assert_type == "contains":
                value = cls._get_value_by_path(response.body, assertion.get("path"))
                result = cls.contains(value, assertion.get("value"), assertion.get("name", "包含检查"))
            elif assert_type == "not_contains":
                value = cls._get_value_by_path(response.body, assertion.get("path"))
                result = cls.not_contains(value, assertion.get("value"), assertion.get("name", "不包含检查"))
            elif assert_type == "contains_key":
                value = cls._get_value_by_path(response.body, assertion.get("path"))
                result = cls.contains_key(value, assertion.get("key"), assertion.get("name", "键检查"))
            elif assert_type == "type_check":
                value = cls._get_value_by_path(response.body, assertion.get("path"))
                type_map = {"str": str, "int": int, "float": float, "bool": bool, "list": list, "dict": dict, "None": type(None)}
                expected_type = type_map.get(assertion.get("expected_type"), str)
                result = cls.type_check(value, expected_type, assertion.get("name", "类型检查"))
            elif assert_type == "length":
                value = cls._get_value_by_path(response.body, assertion.get("path"))
                result = cls.length(value, assertion.get("expected"), assertion.get("name", "长度检查"))
            elif assert_type == "regex_match":
                value = cls._get_value_by_path(response.body, assertion.get("path"))
                value = str(value) if value else ""
                result = cls.regex_match(value, assertion.get("pattern"), assertion.get("name", "正则检查"))
            # 响应相关断言
            elif assert_type == "status_code":
                result = cls.status_code(response, assertion.get("expected"), assertion.get("name", "状态码检查"))
            elif assert_type == "response_time":
                if "max" in assertion:
                    result = cls.in_range(response.response_time, max_val=assertion["max"], 
                                        name=assertion.get("name", "响应时间检查"))
                elif "min" in assertion:
                    result = cls.in_range(response.response_time, min_val=assertion["min"],
                                        name=assertion.get("name", "响应时间检查"))
                else:
                    result = cls.in_range(response.response_time, 
                                        min_val=assertion.get("min"), 
                                        max_val=assertion.get("max"),
                                        name=assertion.get("name", "响应时间检查"))
            # v2.0 新增断言类型
            elif assert_type == "json_schema":
                value = cls._get_value_by_path(response.body, assertion.get("path", "$"))
                schema = assertion.get("schema", {})
                result = cls.json_schema(value, schema, assertion.get("name", "JSON Schema 检查"))
            elif assert_type == "custom":
                value = cls._get_value_by_path(response.body, assertion.get("path", "$"))
                script = assertion.get("script", "")
                
                # 从脚本字符串中执行自定义逻辑
                try:
                    local_vars = {"response": response.body, "value": value, "result": None}
                    exec(script, {}, local_vars)
                    check_result = local_vars.get("result")
                    
                    if check_result is None:
                        result = AssertionResult(
                            name=assertion.get("name", "自定义断言"),
                            passed=False,
                            message="自定义脚本未返回结果（需设置 result 变量）"
                        )
                    elif isinstance(check_result, tuple) and len(check_result) == 2:
                        passed, message = check_result
                        result = cls.custom(value, lambda v: (passed, message), assertion.get("name", "自定义断言"))
                    elif isinstance(check_result, bool):
                        result = AssertionResult(
                            name=assertion.get("name", "自定义断言"),
                            passed=check_result,
                            message=f"自定义断言{'通过' if check_result else '失败'}",
                            expected=True,
                            actual=check_result
                        )
                    else:
                        result = AssertionResult(
                            name=assertion.get("name", "自定义断言"),
                            passed=False,
                            message=f"自定义脚本返回了无效的结果类型: {type(check_result)}"
                        )
                except Exception as e:
                    result = AssertionResult(
                        name=assertion.get("name", "自定义断言"),
                        passed=False,
                        message=f"自定义脚本执行异常: {str(e)}"
                    )
            elif assert_type == "database":
                # 数据库断言：需要外部提供查询结果
                query_result = assertion.get("query_result")
                if query_result is None:
                    result = AssertionResult(
                        name=assertion.get("name", "数据库断言"),
                        passed=False,
                        message="数据库断言需要提供 query_result 参数"
                    )
                else:
                    expected_rows = assertion.get("expected_rows")
                    expected_value = assertion.get("expected_value")
                    db_path = assertion.get("path")
                    result = cls.database(query_result, expected_rows, expected_value, db_path, 
                                        assertion.get("name", "数据库断言"))
            else:
                # 未知断言类型，跳过
                result = AssertionResult(
                    name=assertion.get("name", "未知断言"),
                    passed=False,
                    message=f"未知断言类型：{assert_type}"
                )
            
            results.append(result)
        
        return results
    
    @staticmethod
    def _get_value_by_path(data: Any, path: str) -> Any:
        """
        根据路径从嵌套数据结构中获取值
        支持：data['key']、data[0]、data.key 等格式
        特殊路径：'$' 表示根路径（返回整个数据）
        """
        # 处理根路径或空路径
        if not path or path == '$':
            return data
        
        if data is None:
            return None
        
        # 解析路径
        parts = re.split(r'\.\s*|\[|\]', path)
        parts = [p for p in parts if p]  # 移除空字符串
        
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, (list, tuple)):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    return None
            else:
                # 尝试属性访问
                try:
                    current = getattr(current, part)
                except AttributeError:
                    return None
        
        return current
