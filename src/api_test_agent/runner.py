"""
API 接口自动化测试 Agent - 测试执行器
支持钩子引擎和数据驱动的集成
"""
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

from .client import APIClient, APIResponse
from .assertions import AssertEngine, AssertionResult
from .config import config

# 尝试导入新模块（可选依赖）
try:
    from .hooks import HookEngine
    HOOK_ENGINE_AVAILABLE = True
except ImportError:
    HOOK_ENGINE_AVAILABLE = False

try:
    from .data_driver import DataDriver, DataSourceConfig
    DATA_DRIVER_AVAILABLE = True
except ImportError:
    DATA_DRIVER_AVAILABLE = False


@dataclass
class TestStep:
    """测试步骤"""
    name: str
    method: str
    endpoint: str
    params: Dict = field(default_factory=dict)
    headers: Dict = field(default_factory=dict)
    json_data: Any = None
    data: Any = None
    auth: tuple = None
    assertions: List[Dict] = field(default_factory=list)
    setup_steps: List['TestStep'] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCaseResult:
    """测试用例执行结果"""
    name: str
    description: str
    passed: bool
    total_steps: int
    passed_steps: int
    failed_steps: int
    step_results: List[Dict]
    total_time: float
    error_message: Optional[str] = None


@dataclass
class TestSuiteResult:
    """测试套件执行结果"""
    suite_name: str
    start_time: str
    end_time: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_time: float
    test_results: List[TestCaseResult] = field(default_factory=list)


class TestRunner:
    """测试执行器"""
    
    def __init__(self, base_url: str = None):
        self.client = APIClient(base_url=base_url)
        self.logger = self._setup_logger()
        self.variables = {}  # 全局变量存储
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("APITestRunner")
        logger.setLevel(getattr(logging, config.get("log_level", "INFO")))
        
        if not logger.handlers:
            # 控制台处理器
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(ch)
            
            # 文件处理器
            log_file = config.get("log_file", "api_test.log")
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(fh)
        
        return logger
    
    def load_test_case(self, file_path: str) -> Dict:
        """加载测试用例文件（支持 YAML 和 JSON）"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"测试用例文件不存在：{file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif path.suffix == '.json':
                return json.load(f)
            else:
                # 尝试 YAML
                return yaml.safe_load(f)
    
    def load_test_suite(self, directory: str) -> List[Dict]:
        """加载测试目录下的所有测试用例"""
        test_dir = Path(directory)
        test_cases = []
        
        for ext in ['*.yaml', '*.yml', '*.json']:
            for file in test_dir.glob(ext):
                try:
                    case = self.load_test_case(str(file))
                    test_cases.append(case)
                except Exception as e:
                    self.logger.error(f"加载测试用例失败 {file}: {e}")
        
        return test_cases
    
    def execute_step(self, step: TestStep, context: Dict = None) -> tuple:
        """
        执行单个测试步骤
        
        Returns:
            (response, step_result_dict)
        """
        context = context or {}
        
        # 解析变量（简单的 ${var} 替换）
        def replace_vars(value: Any) -> Any:
            if isinstance(value, str):
                for var_name, var_value in self.variables.items():
                    value = value.replace(f"${{{var_name}}}", str(var_value))
                for var_name, var_value in context.items():
                    value = value.replace(f"${{{var_name}}}", str(var_value))
                return value
            elif isinstance(value, dict):
                return {k: replace_vars(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_vars(item) for item in value]
            return value
        
        endpoint = replace_vars(step.endpoint)
        params = replace_vars(step.params)
        headers = replace_vars(step.headers)
        json_data = replace_vars(step.json_data)
        data = replace_vars(step.data)
        
        self.logger.info(f"执行步骤: {step.name}")
        self.logger.info(f"请求: {step.method} {endpoint}")
        
        # 发送请求
        response_method = getattr(self.client, step.method.lower())
        response = response_method(
            endpoint=endpoint,
            params=params,
            headers=headers,
            json_data=json_data,
            data=data,
            auth=step.auth
        )
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.info(f"响应时间: {response.response_time:.3f}s")
        
        # 执行断言
        assertion_results = AssertEngine.validate_response(response, step.assertions)
        
        step_passed = all(ar.passed for ar in assertion_results)
        
        # 记录步骤结果
        step_result = {
            "name": step.name,
            "method": step.method,
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time": round(response.response_time, 3),
            "passed": step_passed,
            "assertions": [
                {
                    "name": ar.name,
                    "passed": ar.passed,
                    "message": ar.message,
                    "expected": str(ar.expected),
                    "actual": str(ar.actual)
                }
                for ar in assertion_results
            ],
            "error": response.error_message if not response.success else None
        }
        
        if response.success:
            self.logger.info(f"✓ 步骤 {step.name} 完成")
        else:
            self.logger.error(f"✗ 步骤 {step.name} 失败：{response.error_message}")
        
        # 保存响应中的变量供后续步骤使用
        for var_name, var_config in step.variables.items():
            if isinstance(var_config, dict) and "path" in var_config:
                value = AssertEngine._get_value_by_path(response.body, var_config["path"])
                self.variables[var_name] = value
                context[var_name] = value
        
        return response, step_result
    
    def execute_test_case(self, test_case: Dict) -> TestCaseResult:
        """执行单个测试用例

        支持钩子引擎集成：如果测试用例定义了 hooks（setup/teardown/global_setup/global_teardown），
        将委托给 HookEngine 执行完整的生命周期。

        Args:
            test_case: 测试用例配置字典

        Returns:
            TestCaseResult 测试结果
        """
        # 检测是否定义了 hooks
        has_hooks = any([
            test_case.get('setup'),
            test_case.get('teardown'),
            test_case.get('global_setup'),
            test_case.get('global_teardown')
        ])

        # 如果有 hooks 且 HookEngine 可用，使用钩子引擎执行
        if has_hooks and HOOK_ENGINE_AVAILABLE:
            return self._execute_with_hooks(test_case)

        # 否则使用原有的执行逻辑（向后兼容）
        return self._execute_test_case_original(test_case)

    def _execute_with_hooks(self, test_case: Dict) -> TestCaseResult:
        """使用 HookEngine 执行带钩子的测试用例

        Args:
            test_case: 包含 hooks 配置的测试用例

        Returns:
            TestCaseResult 测试结果
        """
        self.logger.info("检测到钩子配置，使用 HookEngine 执行")

        try:
            hook_engine = HookEngine(base_url=self.client.base_url)

            # 设置全局钩子
            global_setup = test_case.get('global_setup', [])
            global_teardown = test_case.get('global_teardown', [])
            if global_setup or global_teardown:
                hook_engine.set_global_hooks(
                    setup_hooks=global_setup,
                    teardown_hooks=global_teardown
                )

            # 使用 HookEngine 执行完整生命周期
            hook_result = hook_engine.execute_test_case_with_hooks(test_case)

            # 转换 HookEngine 结果为 TestCaseResult 格式
            step_results = hook_result.get('step_results', [])
            passed_steps = sum(1 for step in step_results if step.get("passed", False))
            failed_steps = len(step_results) - passed_steps

            total_time = 0.0
            for result_list in [
                hook_result.get('global_setup_results', []),
                hook_result.get('setup_results', []),
                hook_result.get('teardown_results', []),
                hook_result.get('global_teardown_results', [])
            ]:
                for r in result_list:
                    if hasattr(r, 'duration'):
                        total_time += r.duration

            # 从步骤结果中计算总时间
            for step in step_results:
                if isinstance(step, dict) and 'response_time' in step:
                    total_time += step['response_time']

            passed = hook_result.get('status') == 'PASS'
            error_message = hook_result.get('error_message')

            result = TestCaseResult(
                name=test_case.get("name", "Unnamed Test"),
                description=test_case.get("description", ""),
                passed=passed,
                total_steps=len(step_results),
                passed_steps=passed_steps,
                failed_steps=failed_steps,
                step_results=step_results,
                total_time=round(total_time, 3),
                error_message=error_message
            )

            self.logger.info(f"HookEngine 执行完成: {'通过' if passed else '失败'}")
            return result

        except Exception as e:
            self.logger.error(f"HookEngine 执行失败: {e}")
            self.logger.info("回退到原始执行模式")
            return self._execute_test_case_original(test_case)

        finally:
            if 'hook_engine' in locals():
                hook_engine.close()

    def _execute_test_case_original(self, test_case: Dict) -> TestCaseResult:
        """原始的测试用例执行逻辑（向后兼容）

        Args:
            test_case: 测试用例配置字典

        Returns:
            TestCaseResult 测试结果
        """
        start_time = datetime.now()
        
        name = test_case.get("name", "Unnamed Test")
        description = test_case.get("description", "")
        steps_config = test_case.get("steps", [])
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"开始执行测试用例：{name}")
        self.logger.info(f"描述：{description}")
        self.logger.info(f"{'='*60}\n")
        
        step_results = []
        passed_steps = 0
        failed_steps = 0
        error_message = None
        
        for i, step_config in enumerate(steps_config):
            step = TestStep(
                name=step_config.get("name", f"步骤 {i+1}"),
                method=step_config.get("method", "GET"),
                endpoint=step_config.get("endpoint", ""),
                params=step_config.get("params", {}),
                headers=step_config.get("headers", {}),
                json_data=step_config.get("json"),
                data=step_config.get("data"),
                auth=tuple(step_config.get("auth", [])) if step_config.get("auth") else None,
                assertions=step_config.get("assertions", []),
                variables=step_config.get("extract", {})
            )
            
            try:
                response, step_result = self.execute_step(step)
                step_results.append(step_result)
                
                if step_result["passed"]:
                    passed_steps += 1
                else:
                    failed_steps += 1
                    if not error_message:
                        error_message = f"步骤 '{step.name}' 断言失败"
                        
            except Exception as e:
                failed_steps += 1
                step_results.append({
                    "name": step.name,
                    "passed": False,
                    "error": str(e)
                })
                if not error_message:
                    error_message = str(e)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        passed = failed_steps == 0
        
        result = TestCaseResult(
            name=name,
            description=description,
            passed=passed,
            total_steps=len(steps_config),
            passed_steps=passed_steps,
            failed_steps=failed_steps,
            step_results=step_results,
            total_time=round(total_time, 3),
            error_message=error_message
        )
        
        self.logger.info(f"\n测试用例 {name} {'通过' if passed else '失败'}")
        self.logger.info(f"总步骤：{len(steps_config)}, 通过：{passed_steps}, 失败：{failed_steps}")
        self.logger.info(f"耗时：{total_time:.3f}s\n")
        
        return result
    
    def execute_test_file(self, file_path: str) -> TestSuiteResult:
        """执行测试文件

        支持数据驱动：如果文件中定义了 data_source 配置，
        将使用 DataDriver 批量生成多个测试用例。

        Args:
            file_path: 测试文件路径

        Returns:
            TestSuiteResult 测试套件结果
        """
        start_time = datetime.now()
        test_case = self.load_test_case(file_path)

        # 检测是否配置了数据源
        data_source_config = test_case.get('data_source') if isinstance(test_case, dict) else None

        if data_source_config and DATA_DRIVER_AVAILABLE:
            # 数据驱动模式
            return self._execute_with_data_driver(file_path, test_case, data_source_config)

        # 处理可能是列表的情况（原有逻辑）
        if isinstance(test_case, list):
            results = [self.execute_test_case(tc) for tc in test_case]
            suite_name = Path(file_path).stem
            test_results = results
        else:
            result = self.execute_test_case(test_case)
            suite_name = test_case.get("name", Path(file_path).stem)
            test_results = [result]

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        passed_tests = sum(1 for r in test_results if r.passed)
        failed_tests = len(test_results) - passed_tests

        return TestSuiteResult(
            suite_name=suite_name,
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=len(test_results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=round(total_time, 3),
            test_results=test_results
        )

    def _execute_with_data_driver(self, file_path: str, test_case: Dict, data_source_config: Dict) -> TestSuiteResult:
        """使用 DataDriver 执行数据驱动的测试

        Args:
            file_path: 原始测试文件路径
            test_case: 包含 data_source 的测试用例
            data_source_config: 数据源配置字典

        Returns:
            TestSuiteResult 测试套件结果
        """
        start_time = datetime.now()
        self.logger.info(f"检测到数据源配置，使用 DataDriver 生成测试用例")

        try:
            # 构建 DataSourceConfig 对象
            ds_config = DataSourceConfig(
                type=data_source_config.get('type', 'csv'),
                file=data_source_config.get('file', ''),
                mapping=data_source_config.get('mapping', {}),
                filter=data_source_config.get('filter'),
                case_name_template=data_source_config.get('case_name_template', '{name}_{row_index}')
            )

            # 创建模板（移除 data_source 字段）
            template = {k: v for k, v in test_case.items() if k != 'data_source'}

            # 使用 DataDriver 生成测试用例
            driver = DataDriver()
            generated_cases = driver.generate_test_cases(ds_config, template)

            self.logger.info(f"DataDriver 生成了 {len(generated_cases)} 个测试用例")

            # 执行所有生成的测试用例
            test_results = []
            for gen_case in generated_cases:
                self.logger.debug(f"生成的用例: {gen_case.name}")
                self.logger.debug(f"用例配置 keys: {list(gen_case.config.keys())}")
                self.logger.debug(f"steps 存在: {'steps' in gen_case.config}")
                if 'steps' in gen_case.config:
                    self.logger.debug(f"steps 数量: {len(gen_case.config['steps'])}")
                result = self.execute_test_case(gen_case.config)
                test_results.append(result)

            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()

            passed_tests = sum(1 for r in test_results if r.passed)
            failed_tests = len(test_results) - passed_tests

            return TestSuiteResult(
                suite_name=f"{Path(file_path).stem} (DataDriven: {len(generated_cases)} cases)",
                start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
                total_tests=len(test_results),
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=round(total_time, 3),
                test_results=test_results
            )

        except Exception as e:
            self.logger.error(f"DataDriver 执行失败: {e}")
            self.logger.info("回退到原始执行模式")
            # 回退：移除 data_source 后执行原始用例
            fallback_case = {k: v for k, v in test_case.items() if k != 'data_source'}
            result = self.execute_test_case(fallback_case)

            return TestSuiteResult(
                suite_name=Path(file_path).stem,
                start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total_tests=1,
                passed_tests=1 if result.passed else 0,
                failed_tests=0 if result.passed else 1,
                total_time=result.total_time,
                test_results=[result]
            )
    
    def execute_test_directory(self, directory: str) -> TestSuiteResult:
        """执行目录下所有测试文件"""
        start_time = datetime.now()
        test_cases = self.load_test_suite(directory)
        
        results = [self.execute_test_case(tc) for tc in test_cases]
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = len(results) - passed_tests
        
        return TestSuiteResult(
            suite_name=f"All Tests in {directory}",
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=len(results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=round(total_time, 3),
            test_results=results
        )
    
    def close(self):
        """关闭客户端连接"""
        self.client.close()
