"""
API Test Agent v2.0 - 钩子引擎模块
支持 HTTP/Command/Script 三种钩子类型，提供测试生命周期管理
"""
import subprocess
import time
import importlib.util
import sys
import re
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

from .client import APIClient


class HookType(Enum):
    """钩子类型枚举"""
    HTTP = "http"
    COMMAND = "command"
    SCRIPT = "script"


@dataclass
class HookConfig:
    """钩子配置数据类"""
    name: str
    hook_type: HookType
    method: Optional[str] = None
    endpoint: Optional[str] = None
    command: Optional[str] = None
    script: Optional[str] = None
    condition: Optional[str] = None
    extract: Dict[str, Any] = field(default_factory=dict)
    ignore_failure: bool = False
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    json_data: Any = None
    timeout: Optional[int] = None


@dataclass
class HookResult:
    """钩子执行结果数据类"""
    success: bool
    error_message: Optional[str] = None
    duration: float = 0.0
    extracted_vars: Dict[str, Any] = field(default_factory=dict)
    hook_name: str = ""


class BaseHookExecutor(ABC):
    """抽象执行器基类"""

    def __init__(self, api_client: Optional[APIClient] = None, timeout: int = 30):
        self.api_client = api_client or APIClient()
        self.timeout = timeout
        self.logger = logging.getLogger("HookEngine")

    @abstractmethod
    def execute(self, hook_config: HookConfig, context: Dict[str, Any]) -> HookResult:
        """执行钩子，返回结果"""
        pass

    def _extract_variables(self, response_body: Any, extract_config: Dict[str, Any]) -> Dict[str, Any]:
        """从响应中提取变量"""
        extracted = {}
        for var_name, path in extract_config.items():
            try:
                value = self._get_value_by_path(response_body, path)
                extracted[var_name] = value
            except (KeyError, TypeError, IndexError) as e:
                self.logger.warning(f"提取变量 {var_name} 失败：{e}")
        return extracted

    def _get_value_by_path(self, obj: Any, path: str) -> Any:
        """通过路径获取嵌套值（支持点号分隔）"""
        keys = path.split('.')
        current = obj
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                current = current[int(key)]
            else:
                raise KeyError(f"无法访问路径 {path}")
        return current


class HttpHookExecutor(BaseHookExecutor):
    """HTTP 类型钩子执行器"""

    def execute(self, hook_config: HookConfig, context: Dict[str, Any]) -> HookResult:
        start_time = time.time()

        try:
            method = hook_config.method or "GET"
            endpoint = self._replace_vars(hook_config.endpoint or "", context)
            headers = self._replace_vars_dict(hook_config.headers, context)
            params = self._replace_vars_dict(hook_config.params, context)
            json_data = self._replace_vars(hook_config.json_data, context)

            self.logger.info(f"执行 HTTP 钩子: {method} {endpoint}")

            response = self.api_client.request(
                method=method,
                endpoint=endpoint,
                params=params if params else None,
                headers=headers if headers else None,
                json_data=json_data
            )

            duration = time.time() - start_time
            extracted_vars = {}

            if response.success and hook_config.extract:
                extracted_vars = self._extract_variables(response.body, hook_config.extract)

            if not response.success:
                return HookResult(
                    success=False,
                    error_message=f"HTTP 请求失败: status={response.status_code}, error={response.error_message}, body={response.body}",
                    duration=duration,
                    hook_name=hook_config.name
                )

            return HookResult(
                success=True,
                duration=duration,
                extracted_vars=extracted_vars,
                hook_name=hook_config.name
            )

        except Exception as e:
            duration = time.time() - start_time
            return HookResult(
                success=False,
                error_message=f"HTTP 钩子执行异常: {str(e)}",
                duration=duration,
                hook_name=hook_config.name
            )

    def _replace_vars(self, value: Any, context: Dict[str, Any]) -> Any:
        """替换变量占位符"""
        if isinstance(value, str):
            result = value
            for var_name, var_value in context.items():
                result = result.replace(f"${{{var_name}}}", str(var_value))
            return result
        return value

    def _replace_vars_dict(self, d: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """替换字典中的变量"""
        if not d:
            return {}
        return {k: self._replace_vars(v, context) for k, v in d.items()}


class CommandHookExecutor(BaseHookExecutor):
    """Command 类型钩子执行器"""

    def execute(self, hook_config: HookConfig, context: Dict[str, Any]) -> HookResult:
        start_time = time.time()
        timeout = hook_config.timeout or self.timeout

        try:
            command = hook_config.command or ""
            command = self._replace_vars(command, context)

            self.logger.info(f"执行 Command 钩子: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            duration = time.time() - start_time
            extracted_vars = {}

            if result.returncode != 0:
                error_msg = f"命令执行失败 (返回码 {result.returncode})"
                if result.stderr:
                    error_msg += f", stderr: {result.stderr.strip()}"
                if result.stdout:
                    error_msg += f", stdout: {result.stdout.strip()}"

                return HookResult(
                    success=False,
                    error_message=error_msg,
                    duration=duration,
                    hook_name=hook_config.name
                )

            if hook_config.extract:
                stdout = result.stdout.strip()
                for var_name, pattern in hook_config.extract.items():
                    match = re.search(pattern, stdout)
                    if match:
                        try:
                            extracted_vars[var_name] = match.group(1) if match.groups() else match.group(0)
                        except IndexError:
                            pass

            return HookResult(
                success=True,
                duration=duration,
                extracted_vars=extracted_vars,
                hook_name=hook_config.name
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return HookResult(
                success=False,
                error_message=f"命令执行超时 ({timeout}s)",
                duration=duration,
                hook_name=hook_config.name
            )
        except Exception as e:
            duration = time.time() - start_time
            return HookResult(
                success=False,
                error_message=f"Command 钩子执行异常: {str(e)}",
                duration=duration,
                hook_name=hook_config.name
            )

    def _replace_vars(self, value: str, context: Dict[str, Any]) -> str:
        """替换变量占位符"""
        result = value
        for var_name, var_value in context.items():
            result = result.replace(f"${{{var_name}}}", str(var_value))
        return result


class ScriptHookExecutor(BaseHookExecutor):
    """Script 类型钩子执行器"""

    def execute(self, hook_config: HookConfig, context: Dict[str, Any]) -> HookResult:
        start_time = time.time()

        try:
            script_path = hook_config.script or ""
            script_path = self._replace_vars(script_path, context)

            self.logger.info(f"执行 Script 钩子: {script_path}")

            if not Path(script_path).exists():
                return HookResult(
                    success=False,
                    error_message=f"脚本文件不存在: {script_path}",
                    duration=time.time() - start_time,
                    hook_name=hook_config.name
                )

            spec = importlib.util.spec_from_file_location("hook_script", script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["hook_script"] = module
            spec.loader.exec_module(module)

            if not hasattr(module, 'execute'):
                return HookResult(
                    success=False,
                    error_message="脚本缺少 execute 函数",
                    duration=time.time() - start_time,
                    hook_name=hook_config.name
                )

            script_result = module.execute(context)

            duration = time.time() - start_time
            extracted_vars = {}

            if isinstance(script_result, dict):
                extracted_vars = script_result
            elif script_result is not None:
                extracted_vars["result"] = script_result

            if hook_config.extract:
                for var_name in hook_config.extract:
                    if var_name in extracted_vars:
                        extracted_vars[var_name] = extracted_vars[var_name]

            return HookResult(
                success=True,
                duration=duration,
                extracted_vars=extracted_vars,
                hook_name=hook_config.name
            )

        except Exception as e:
            duration = time.time() - start_time
            return HookResult(
                success=False,
                error_message=f"Script 钩子执行异常: {type(e).__name__}: {str(e)}",
                duration=duration,
                hook_name=hook_config.name
            )

    def _replace_vars(self, value: str, context: Dict[str, Any]) -> str:
        """替换变量占位符"""
        result = value
        for var_name, var_value in context.items():
            result = result.replace(f"${{{var_name}}}", str(var_value))
        return result


class HookEngine:
    """钩子引擎核心类"""

    def __init__(self, base_url: str = None, timeout: int = 30):
        self.api_client = APIClient(base_url=base_url)
        self.timeout = timeout
        self.logger = logging.getLogger("HookEngine")
        self.executors = {
            HookType.HTTP: HttpHookExecutor(self.api_client, timeout),
            HookType.COMMAND: CommandHookExecutor(self.api_client, timeout),
            HookType.SCRIPT: ScriptHookExecutor(self.api_client, timeout)
        }
        self.global_hooks = {
            'setup': [],
            'teardown': []
        }

    def set_global_hooks(self, setup_hooks: List[HookConfig] = None, teardown_hooks: List[HookConfig] = None):
        """设置全局钩子"""
        if setup_hooks:
            self.global_hooks['setup'] = setup_hooks
        if teardown_hooks:
            self.global_hooks['teardown'] = teardown_hooks

    def evaluate_condition(self, condition_str: str, context: Dict[str, Any]) -> bool:
        """
        评估条件表达式
        支持格式：
        - "${var} is not none"
        - "${var} == 'value'"
        - "${var} != 'value'"
        - "${var} is none"
        """
        if not condition_str:
            return True

        condition = condition_str.strip()

        var_match = re.match(r'\$\{(\w+)\}\s*(.+)', condition)
        if not var_match:
            return True

        var_name = var_match.group(1)
        expression = var_match.group(2).strip()
        var_value = context.get(var_name)

        if expression == "is not none":
            return var_value is not None
        elif expression == "is none":
            return var_value is None
        elif expression.startswith("=="):
            expected = expression[2:].strip().strip("'\"")
            return str(var_value) == expected
        elif expression.startswith("!="):
            expected = expression[2:].strip().strip("'\"")
            return str(var_value) != expected
        elif expression.startswith(">="):
            try:
                return float(var_value) >= float(expression[2:].strip())
            except (TypeError, ValueError):
                return False
        elif expression.startswith("<="):
            try:
                return float(var_value) <= float(expression[2:].strip())
            except (TypeError, ValueError):
                return False
        elif expression.startswith(">"):
            try:
                return float(var_value) > float(expression[1:].strip())
            except (TypeError, ValueError):
                return False
        elif expression.startswith("<"):
            try:
                return float(var_value) < float(expression[1:].strip())
            except (TypeError, ValueError):
                return False

        return True

    def execute_hooks(self, hooks: List[HookConfig], context: Dict[str, Any]) -> List[HookResult]:
        """
        执行钩子列表
        顺序执行，遇到失败且 ignore_failure=False 时停止
        """
        results = []

        for hook in hooks:
            if hook.condition and not self.evaluate_condition(hook.condition, context):
                self.logger.info(f"跳过钩子 '{hook.name}'（条件不满足）")
                continue

            executor = self.executors.get(hook.hook_type)
            if not executor:
                result = HookResult(
                    success=False,
                    error_message=f"未知的钩子类型: {hook.hook_type}",
                    hook_name=hook.name
                )
                results.append(result)
                if not hook.ignore_failure:
                    break
                continue

            result = executor.execute(hook, context)
            results.append(result)

            context.update(result.extracted_vars)

            if not result.success and not hook.ignore_failure:
                break

        return results

    def execute_test_case_with_hooks(self, test_case: Dict) -> Dict:
        """
        带钩子的测试用例执行
        生命周期：global_setup → setup → steps → teardown → global_teardown
        """
        from .runner import TestRunner, TestCaseResult

        context = {}
        all_results = {
            'global_setup_results': [],
            'setup_results': [],
            'step_results': [],
            'teardown_results': [],
            'global_teardown_results': [],
            'status': 'PASS',
            'error_message': None
        }

        test_runner = TestRunner(base_url=self.api_client.base_url)

        try:
            all_results['global_setup_results'] = self.execute_hooks(
                self.global_hooks['setup'], context
            )

            setup_failed = any(
                not r.success and not getattr(
                    next((h for h in self.global_hooks['setup'] if h.name == r.hook_name), None),
                    'ignore_failure', False
                )
                for r in all_results['global_setup_results']
            ) if all_results['global_setup_results'] else False

            case_setup_hooks = [
                HookConfig(
                    name=h.get('name', ''),
                    hook_type=HookType(h.get('type', 'http')),
                    method=h.get('method'),
                    endpoint=h.get('endpoint'),
                    command=h.get('command'),
                    script=h.get('script'),
                    condition=h.get('condition'),
                    extract=h.get('extract', {}),
                    ignore_failure=h.get('ignore_failure', False),
                    headers=h.get('headers', {}),
                    params=h.get('params', {}),
                    json_data=h.get('json')
                )
                for h in test_case.get('setup', [])
            ]

            all_results['setup_results'] = self.execute_hooks(case_setup_hooks, context)

            setup_error = None
            for r in all_results['setup_results']:
                if not r.success:
                    hook_config = next(
                        (h for h in case_setup_hooks if h.name == r.hook_name), None
                    )
                    if hook_config and not hook_config.ignore_failure:
                        setup_error = r.error_message
                        break

            if setup_failed or setup_error:
                all_results['status'] = 'ERROR'
                all_results['error_message'] = setup_error or "Global setup failed"
                self.logger.error(f"Setup 失败，跳过步骤执行: {all_results['error_message']}")
            else:
                try:
                    case_result: TestCaseResult = test_runner.execute_test_case(test_case)
                    all_results['step_results'] = case_result.step_results

                    if not case_result.passed:
                        all_results['status'] = 'FAIL'
                        all_results['error_message'] = case_result.error_message
                except Exception as e:
                    all_results['status'] = 'ERROR'
                    all_results['error_message'] = f"步骤执行异常: {str(e)}"

        except Exception as e:
            all_results['status'] = 'ERROR'
            all_results['error_message'] = f"执行异常: {str(e)}"

        finally:
            case_teardown_hooks = [
                HookConfig(
                    name=h.get('name', ''),
                    hook_type=HookType(h.get('type', 'http')),
                    method=h.get('method'),
                    endpoint=h.get('endpoint'),
                    command=h.get('command'),
                    script=h.get('script'),
                    condition=h.get('condition'),
                    extract=h.get('extract', {}),
                    ignore_failure=h.get('ignore_failure', False),
                    headers=h.get('headers', {}),
                    params=h.get('params', {}),
                    json_data=h.get('json')
                )
                for h in test_case.get('teardown', [])
            ]

            all_results['teardown_results'] = self.execute_hooks(case_teardown_hooks, context)

            all_results['global_teardown_results'] = self.execute_hooks(
                self.global_hooks['teardown'], context
            )

            test_runner.close()

        return all_results

    def close(self):
        """关闭 API 客户端"""
        self.api_client.close()
