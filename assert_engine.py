"""
API 接口自动化测试 Agent - 断言引擎
"""
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from api_client import APIResponse


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
