"""
Hook Engine Unit Tests
Covers HTTP/Command/Script executors, normal and error flows, teardown guarantee, variable scope, condition evaluation
"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from api_test_agent.hooks import (
    HookEngine,
    HookConfig,
    HookResult,
    HookType,
    HttpHookExecutor,
    CommandHookExecutor,
    ScriptHookExecutor,
    BaseHookExecutor
)
from api_test_agent.client import APIResponse


class TestHookDataStructures:
    """Task 2.1: Test data structures and interface definitions"""

    def test_hook_config_creation(self):
        """Test HookConfig dataclass creation"""
        config = HookConfig(
            name="test_hook",
            hook_type=HookType.HTTP,
            method="POST",
            endpoint="/api/test",
            extract={"id": "data.id"},
            ignore_failure=True
        )
        assert config.name == "test_hook"
        assert config.hook_type == HookType.HTTP
        assert config.method == "POST"
        assert config.endpoint == "/api/test"
        assert config.extract == {"id": "data.id"}
        assert config.ignore_failure is True

    def test_hook_result_creation(self):
        """Test HookResult dataclass creation"""
        result = HookResult(
            success=True,
            duration=0.5,
            extracted_vars={"user_id": 123},
            hook_name="test"
        )
        assert result.success is True
        assert result.duration == 0.5
        assert result.extracted_vars == {"user_id": 123}
        assert result.hook_name == "test"

    def test_hook_type_enum(self):
        """Test HookType enum values"""
        assert HookType.HTTP.value == "http"
        assert HookType.COMMAND.value == "command"
        assert HookType.SCRIPT.value == "script"

    def test_base_hook_executor_is_abstract(self):
        """Test BaseHookExecutor is abstract class"""
        with pytest.raises(TypeError):
            BaseHookExecutor()

    def test_hook_config_defaults(self):
        """Test HookConfig default values"""
        config = HookConfig(name="test", hook_type=HookType.COMMAND)
        assert config.method is None
        assert config.endpoint is None
        assert config.command is None
        assert config.script is None
        assert config.condition is None
        assert config.extract == {}
        assert config.ignore_failure is False
        assert config.headers == {}
        assert config.params == {}
        assert config.json_data is None
        assert config.timeout is None


class TestHttpHookExecutor:
    """Task 2.2: Test HTTP type hook executor"""

    @pytest.fixture
    def executor(self):
        mock_client = Mock()
        return HttpHookExecutor(api_client=mock_client, timeout=10)

    def test_http_get_success(self, executor):
        """Test HTTP GET success scenario"""
        executor.api_client.request.return_value = APIResponse(
            status_code=200,
            headers={},
            body={"data": {"id": 123, "name": "test"}},
            response_time=0.1,
            success=True
        )

        config = HookConfig(
            name="get_user",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="/api/users/1",
            extract={"user_id": "data.id", "user_name": "data.name"}
        )

        result = executor.execute(config, {})
        assert result.success is True
        assert result.extracted_vars == {"user_id": 123, "user_name": "test"}
        assert result.hook_name == "get_user"
        assert result.duration > 0

    def test_http_post_with_json(self, executor):
        """Test HTTP POST with JSON data"""
        executor.api_client.request.return_value = APIResponse(
            status_code=201,
            headers={},
            body={"id": 456, "created": True},
            response_time=0.2,
            success=True
        )

        config = HookConfig(
            name="create_user",
            hook_type=HookType.HTTP,
            method="POST",
            endpoint="/api/users",
            json_data={"name": "new user"},
            headers={"Content-Type": "application/json"}
        )

        result = executor.execute(config, {})
        assert result.success is True
        executor.api_client.request.assert_called_once()

    def test_http_request_failure(self, executor):
        """Test HTTP request failure scenario"""
        executor.api_client.request.return_value = APIResponse(
            status_code=500,
            headers={},
            body={"error": "Internal Server Error"},
            response_time=0.1,
            success=False,
            error_message="Server Error"
        )

        config = HookConfig(
            name="failing_request",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="/api/error"
        )

        result = executor.execute(config, {})
        assert result.success is False
        assert "500" in result.error_message
        assert "Server Error" in result.error_message

    def test_http_variable_replacement(self, executor):
        """Test HTTP hook variable replacement"""
        executor.api_client.request.return_value = APIResponse(
            status_code=200,
            headers={},
            body={},
            response_time=0.1,
            success=True
        )

        config = HookConfig(
            name="var_test",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="/api/users/${user_id}",
            params={"token": "${auth_token}"},
            headers={"X-Token": "${auth_token}"}
        )

        context = {"user_id": "42", "auth_token": "abc123"}
        result = executor.execute(config, context)

        call_args = executor.api_client.request.call_args
        assert "42" in str(call_args)
        assert "abc123" in str(call_args)

    def test_http_exception_handling(self, executor):
        """Test HTTP exception handling"""
        executor.api_client.request.side_effect = Exception("Connection refused")

        config = HookConfig(
            name="exception_test",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="/api/test"
        )

        result = executor.execute(config, {})
        assert result.success is False
        assert "Connection refused" in result.error_message

    def test_http_default_method(self, executor):
        """Test default method is GET"""
        executor.api_client.request.return_value = APIResponse(
            status_code=200,
            headers={},
            body={},
            response_time=0.1,
            success=True
        )

        config = HookConfig(
            name="default_method",
            hook_type=HookType.HTTP,
            endpoint="/api/test"
        )

        result = executor.execute(config, {})
        assert result.success is True
        call_kwargs = executor.api_client.request.call_args[1]
        assert call_kwargs['method'] == 'GET'


class TestCommandHookExecutor:
    """Task 2.3: Test Command type hook executor"""

    @pytest.fixture
    def executor(self):
        return CommandHookExecutor(timeout=5)

    def test_command_success(self, executor):
        """Test command successful execution"""
        config = HookConfig(
            name="echo_test",
            hook_type=HookType.COMMAND,
            command='echo "hello world"'
        )

        result = executor.execute(config, {})
        assert result.success is True
        assert result.error_message is None

    def test_command_with_variable_replacement(self, executor):
        """Test variable replacement in command"""
        config = HookConfig(
            name="var_echo",
            hook_type=HookType.COMMAND,
            command='echo "User ${user_id}"'
        )

        context = {"user_id": "42"}
        result = executor.execute(config, context)
        assert result.success is True

    def test_command_failure_nonzero_exit(self, executor):
        """Test command returns non-zero exit code"""
        config = HookConfig(
            name="fail_cmd",
            hook_type=HookType.COMMAND,
            command='exit 1'
        )

        result = executor.execute(config, {})
        assert result.success is False
        assert "return code 1" in result.error_message or "1" in result.error_message

    def test_command_timeout(self, executor):
        """Test command timeout"""
        config = HookConfig(
            name="timeout_cmd",
            hook_type=HookType.COMMAND,
            command='ping -n 10 127.0.0.1',
            timeout=1
        )

        result = executor.execute(config, {})
        assert result.success is False
        assert "timeout" in result.error_message.lower() or "超时" in result.error_message

    def test_command_extract_variables(self, executor):
        """Test extracting variables from command output"""
        config = HookConfig(
            name="extract_test",
            hook_type=HookType.COMMAND,
            command='echo "ID: 12345 Name: test"',
            extract={
                "id": r"ID: (\d+)",
                "name": r"Name: (\w+)"
            }
        )

        result = executor.execute(config, {})
        assert result.success is True
        assert result.extracted_vars.get("id") == "12345"
        assert result.extracted_vars.get("name") == "test"


class TestScriptHookExecutor:
    """Task 2.4: Test Script type hook executor"""

    @pytest.fixture
    def executor(self):
        return ScriptHookExecutor()

    @pytest.fixture
    def temp_script_file(self, tmp_path):
        """Create temporary Python script file"""
        script_content = '''
def execute(context):
    return {
        "user_id": 123,
        "username": context.get("name", "default")
    }
'''
        script_file = tmp_path / "test_script.py"
        script_file.write_text(script_content)
        return str(script_file)

    def test_script_success(self, executor, temp_script_file):
        """Test script successful execution"""
        config = HookConfig(
            name="script_test",
            hook_type=HookType.SCRIPT,
            script=temp_script_file
        )

        result = executor.execute(config, {"name": "test_user"})
        assert result.success is True
        assert result.extracted_vars["user_id"] == 123
        assert result.extracted_vars["username"] == "test_user"

    def test_script_not_found(self, executor):
        """Test script file not found"""
        config = HookConfig(
            name="missing_script",
            hook_type=HookType.SCRIPT,
            script="/nonexistent/path/script.py"
        )

        result = executor.execute(config, {})
        assert result.success is False
        assert "not found" in result.error_message.lower() or "does not exist" in result.error_message.lower() or "不存在" in result.error_message

    def test_script_missing_execute_function(self, executor, tmp_path):
        """Test script missing execute function"""
        script_content = '''
def run(context):
    return {}
'''
        script_file = tmp_path / "no_execute.py"
        script_file.write_text(script_content)

        config = HookConfig(
            name="no_execute",
            hook_type=HookType.SCRIPT,
            script=str(script_file)
        )

        result = executor.execute(config, {})
        assert result.success is False
        assert "execute" in result.error_message.lower()

    def test_script_exception(self, executor, tmp_path):
        """Test exception inside script"""
        script_content = '''
def execute(context):
    raise ValueError("Script error occurred")
'''
        script_file = tmp_path / "error_script.py"
        script_file.write_text(script_content)

        config = HookConfig(
            name="error_script",
            hook_type=HookType.SCRIPT,
            script=str(script_file)
        )

        result = executor.execute(config, {})
        assert result.success is False
        assert "ValueError" in result.error_message
        assert "Script error occurred" in result.error_message

    def test_script_returns_none(self, executor, tmp_path):
        """Test script returns None"""
        script_content = '''
def execute(context):
    pass
'''
        script_file = tmp_path / "none_return.py"
        script_file.write_text(script_content)

        config = HookConfig(
            name="none_return",
            hook_type=HookType.SCRIPT,
            script=str(script_file)
        )

        result = executor.execute(config, {})
        assert result.success is True
        assert result.extracted_vars == {}

    def test_script_variable_replacement(self, executor, tmp_path):
        """Test variable replacement in script path"""
        script_content = '''
def execute(context):
    return {"path": context.get("script_path")}
'''
        script_file = tmp_path / "var_script.py"
        script_file.write_text(script_content)

        config = HookConfig(
            name="var_path",
            hook_type=HookType.SCRIPT,
            script="${script_path}"
        )

        result = executor.execute(config, {"script_path": str(script_file)})
        assert result.success is True


class TestHookEngineCore:
    """Task 2.5: Test hook engine core scheduling logic"""

    @pytest.fixture
    def engine(self):
        return HookEngine(base_url="http://test.com", timeout=10)

    def test_execute_hooks_empty_list(self, engine):
        """Test empty hooks list"""
        results = engine.execute_hooks([], {})
        assert results == []

    def test_execute_hooks_single_success(self, engine):
        """Test single hook successful execution"""
        with patch.object(engine.executors[HookType.COMMAND], 'execute') as mock_exec:
            mock_exec.return_value = HookResult(success=True, hook_name="test")

            config = HookConfig(name="test", hook_type=HookType.COMMAND, command='echo test')
            results = engine.execute_hooks([config], {})

            assert len(results) == 1
            assert results[0].success is True
            mock_exec.assert_called_once()

    def test_execute_hooks_multiple_sequential(self, engine):
        """Test multiple hooks sequential execution"""
        with patch.object(engine.executors[HookType.COMMAND], 'execute') as mock_exec:
            mock_exec.side_effect = [
                HookResult(success=True, extracted_vars={"a": 1}, hook_name="h1"),
                HookResult(success=True, extracted_vars={"b": 2}, hook_name="h2"),
                HookResult(success=True, extracted_vars={"c": 3}, hook_name="h3")
            ]

            hooks = [
                HookConfig(name=f"h{i}", hook_type=HookType.COMMAND, command='echo test')
                for i in range(1, 4)
            ]
            context = {}
            results = engine.execute_hooks(hooks, context)

            assert len(results) == 3
            assert all(r.success for r in results)
            assert context == {"a": 1, "b": 2, "c": 3}

    def test_execute_hooks_stop_on_failure(self, engine):
        """Test stop on failure"""
        with patch.object(engine.executors[HookType.COMMAND], 'execute') as mock_exec:
            mock_exec.side_effect = [
                HookResult(success=True, hook_name="h1"),
                HookResult(success=False, error_message="Failed", hook_name="h2"),
                HookResult(success=True, hook_name="h3")
            ]

            hooks = [
                HookConfig(name=f"h{i}", hook_type=HookType.COMMAND, command='echo test')
                for i in range(1, 4)
            ]
            results = engine.execute_hooks(hooks, {})

            assert len(results) == 2
            assert results[0].success is True
            assert results[1].success is False
            assert mock_exec.call_count == 2

    def test_execute_hooks_ignore_failure(self, engine):
        """Test ignore_failure continues execution"""
        with patch.object(engine.executors[HookType.COMMAND], 'execute') as mock_exec:
            mock_exec.side_effect = [
                HookResult(success=False, error_message="Ignored", hook_name="h1"),
                HookResult(success=True, hook_name="h2")
            ]

            hooks = [
                HookConfig(name="h1", hook_type=HookType.COMMAND, command='echo fail', ignore_failure=True),
                HookConfig(name="h2", hook_type=HookType.COMMAND, command='echo ok')
            ]
            results = engine.execute_hooks(hooks, {})

            assert len(results) == 2
            assert results[0].success is False
            assert results[1].success is True

    def test_evaluate_condition_is_not_none(self, engine):
        """Test condition expression: is not none"""
        assert engine.evaluate_condition("${var} is not none", {"var": "value"}) is True
        assert engine.evaluate_condition("${var} is not none", {"var": None}) is False
        assert engine.evaluate_condition("${var} is not none", {}) is False

    def test_evaluate_condition_is_none(self, engine):
        """Test condition expression: is none"""
        assert engine.evaluate_condition("${var} is none", {"var": None}) is True
        assert engine.evaluate_condition("${var} is none", {"var": "value"}) is False

    def test_evaluate_condition_equals(self, engine):
        """Test condition expression: equals"""
        assert engine.evaluate_condition("${var} == 'value'", {"var": "value"}) is True
        assert engine.evaluate_condition("${var} == 'other'", {"var": "value"}) is False

    def test_evaluate_condition_not_equals(self, engine):
        """Test condition expression: !="""
        assert engine.evaluate_condition("${var} != 'other'", {"var": "value"}) is True
        assert engine.evaluate_condition("${var} != 'value'", {"var": "value"}) is False

    def test_evaluate_condition_numeric_comparison(self, engine):
        """Test numeric comparison"""
        assert engine.evaluate_condition("${var} >= 100", {"var": 150}) is True
        assert engine.evaluate_condition("${var} >= 100", {"var": 50}) is False
        assert engine.evaluate_condition("${var} > 50", {"var": 100}) is True
        assert engine.evaluate_condition("${var} < 50", {"var": 30}) is True

    def test_evaluate_condition_empty_string(self, engine):
        """Test empty condition string (always passes)"""
        assert engine.evaluate_condition("", {"var": "value"}) is True
        assert engine.evaluate_condition(None, {"var": None}) is True

    def test_skip_hook_when_condition_false(self, engine):
        """Test skip hook when condition is false"""
        with patch.object(engine.executors[HookType.COMMAND], 'execute') as mock_exec:
            config = HookConfig(
                name="conditional",
                hook_type=HookType.COMMAND,
                command='echo test',
                condition="${order_id} is not none"
            )
            results = engine.execute_hooks([config], {"order_id": None})

            assert len(results) == 0
            mock_exec.assert_not_called()

    def test_execute_hook_when_condition_true(self, engine):
        """Test execute hook when condition is true"""
        with patch.object(engine.executors[HookType.COMMAND], 'execute') as mock_exec:
            mock_exec.return_value = HookResult(success=True, hook_name="cond")

            config = HookConfig(
                name="conditional",
                hook_type=HookType.COMMAND,
                command='echo test',
                condition="${order_id} is not none"
            )
            results = engine.execute_hooks([config], {"order_id": "12345"})

            assert len(results) == 1
            mock_exec.assert_called_once()


class TestLifecycleIntegration:
    """Task 2.6: Test lifecycle integration"""

    @pytest.fixture
    def engine(self):
        return HookEngine(base_url="http://test.com", timeout=10)

    def test_normal_lifecycle_execution(self, engine):
        """Test normal lifecycle execution flow"""
        test_case = {
            "name": "normal_test",
            "description": "Test normal flow",
            "steps": []
        }

        with patch('test_runner.TestRunner') as MockRunner:
            mock_runner_instance = Mock()
            MockRunner.return_value = mock_runner_instance
            mock_runner_instance.execute_test_case.return_value = Mock(
                passed=True,
                step_results=[],
                error_message=None
            )

            with patch.object(engine, 'execute_hooks', return_value=[]):
                result = engine.execute_test_case_with_hooks(test_case)

                assert result['status'] == 'PASS'
                mock_runner_instance.execute_test_case.assert_called_once()
                mock_runner_instance.close.assert_called_once()

    def test_setup_failure_marks_error(self, engine):
        """Test setup failure marks ERROR status"""
        test_case = {
            "name": "setup_fail_test",
            "setup": [
                {
                    "name": "fail_setup",
                    "type": "command",
                    "command": "exit 1"
                }
            ],
            "steps": []
        }

        original_execute = engine.execute_hooks
        def mock_execute(hooks, context):
            if any(h.name == "fail_setup" for h in hooks):
                return [HookResult(success=False, error_message="Setup failed", hook_name="fail_setup")]
            return []

        with patch.object(engine, 'execute_hooks', side_effect=mock_execute):
            result = engine.execute_test_case_with_hooks(test_case)

            assert result['status'] == 'ERROR'
            assert "Setup failed" in result['error_message']

    def test_teardown_always_executes_on_error(self, engine):
        """Test teardown always executes even on setup failure"""
        test_case = {
            "name": "teardown_guarantee",
            "setup": [{"name": "fail_setup", "type": "command", "command": "exit 1"}],
            "teardown": [{"name": "cleanup", "type": "command", "command": "echo cleanup"}],
            "steps": []
        }

        call_log = []
        def mock_execute(hooks, context):
            hook_names = [h.name for h in hooks]
            call_log.append(hook_names)
            if "fail_setup" in hook_names:
                return [HookResult(success=False, error_message="Fail", hook_name="fail_setup")]
            return [HookResult(success=True, hook_name=h) for h in hooks]

        with patch.object(engine, 'execute_hooks', side_effect=mock_execute):
            result = engine.execute_test_case_with_hooks(test_case)

            assert result['status'] == 'ERROR'
            teardown_calls = [names for names in call_log if "cleanup" in names]
            assert len(teardown_calls) > 0, "Teardown should be executed even on setup failure"

    def test_global_and_case_hooks_execution_order(self, engine):
        """Test global and case-level hooks execution order"""
        engine.set_global_hooks(
            setup_hooks=[HookConfig(name="global_setup", hook_type=HookType.COMMAND, command='echo gs')],
            teardown_hooks=[HookConfig(name="global_teardown", hook_type=HookType.COMMAND, command='echo gt')]
        )

        test_case = {
            "name": "hooks_order_test",
            "setup": [{"name": "case_setup", "type": "command", "command": "echo cs"}],
            "teardown": [{"name": "case_teardown", "type": "command", "command": "echo ct"}],
            "steps": []
        }

        execution_order = []
        def mock_execute(hooks, context):
            for h in hooks:
                execution_order.append(h.name)
            return [HookResult(success=True, hook_name=h.name) for h in hooks]

        with patch.object(engine, 'execute_hooks', side_effect=mock_execute):
            with patch('test_runner.TestRunner') as MockRunner:
                mock_runner = Mock()
                MockRunner.return_value = mock_runner
                mock_runner.execute_test_case.return_value = Mock(passed=True, step_results=[], error_message=None)

                engine.execute_test_case_with_hooks(test_case)

                assert execution_order[0] == "global_setup"
                assert execution_order[1] == "case_setup"
                assert "case_teardown" in execution_order
                assert execution_order[-1] == "global_teardown"

    def test_steps_skipped_on_setup_failure(self, engine):
        """Test steps are skipped when setup fails"""
        test_case = {
            "name": "skip_steps",
            "setup": [{"name": "bad_setup", "type": "command", "command": "exit 1"}],
            "steps": [{"name": "step1", "method": "GET", "endpoint": "/test"}]
        }

        def mock_execute(hooks, context):
            if any(h.name == "bad_setup" for h in hooks):
                return [HookResult(success=False, error_message="Setup error", hook_name="bad_setup")]
            return []

        with patch.object(engine, 'execute_hooks', side_effect=mock_execute):
            with patch('test_runner.TestRunner') as MockRunner:
                mock_runner = Mock()
                MockRunner.return_value = mock_runner

                result = engine.execute_test_case_with_hooks(test_case)

                mock_runner.execute_test_case.assert_not_called()
                assert result['status'] == 'ERROR'


class TestVariableScope:
    """Test variable scope management"""

    @pytest.fixture
    def engine(self):
        return HookEngine(timeout=10)

    def test_extracted_variables_available_in_context(self, engine):
        """Test extracted variables available in subsequent hooks"""
        with patch.object(engine.executors[HookType.COMMAND], 'execute') as mock_exec:
            mock_exec.side_effect = [
                HookResult(success=True, extracted_vars={"token": "abc123"}, hook_name="get_token"),
                HookResult(success=True, hook_name="use_token")
            ]

            hooks = [
                HookConfig(name="get_token", hook_type=HookType.COMMAND, command='echo token'),
                HookConfig(name="use_token", hook_type=HookType.COMMAND, command='echo ${token}')
            ]
            context = {}
            engine.execute_hooks(hooks, context)

            assert context["token"] == "abc123"
            second_call_args = mock_exec.call_args
            assert second_call_args[0][1]["token"] == "abc123"

    def test_variables_isolated_between_executions(self, engine):
        """Test variables isolated between different executions"""
        context1 = {}
        context2 = {}

        with patch.object(engine.executors[HookType.COMMAND], 'execute') as mock_exec:
            mock_exec.side_effect = [
                HookResult(success=True, extracted_vars={"id": 999}, hook_name="test"),
                HookResult(success=True, extracted_vars={"id": 888}, hook_name="test")
            ]

            engine.execute_hooks([
                HookConfig(name="test", hook_type=HookType.COMMAND, command='echo test')
            ], context1)

            engine.execute_hooks([
                HookConfig(name="test", hook_type=HookType.COMMAND, command='echo test')
            ], context2)

            assert "id" in context1
            assert context2.get("id") == 888


class TestEdgeCases:
    """Edge cases and exception handling tests"""

    @pytest.fixture
    def engine(self):
        return HookEngine(timeout=10)

    def test_unknown_hook_type_handling(self, engine):
        """Test unknown hook type handling"""
        config = HookConfig(name="test", hook_type=HookType.HTTP)
        results = engine.execute_hooks([config], {})
        assert len(results) == 1

    def test_empty_command_executor(self):
        """Test empty command execution"""
        executor = CommandHookExecutor()
        config = HookConfig(name="empty", hook_type=HookType.COMMAND, command="")
        result = executor.execute(config, {})
        assert result.success is True

    def test_http_extractor_nested_path(self):
        """Test nested path extraction"""
        client = Mock()
        client.request.return_value = APIResponse(
            status_code=200,
            headers={},
            body={"level1": {"level2": {"level3": "deep_value"}}},
            response_time=0.1,
            success=True
        )
        executor = HttpHookExecutor(api_client=client)

        config = HookConfig(
            name="nested",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="/test",
            extract={"value": "level1.level2.level3"}
        )

        result = executor.execute(config, {})
        assert result.extracted_vars["value"] == "deep_value"

    def test_condition_with_missing_variable(self, engine):
        """Test condition expression referencing non-existent variable"""
        assert engine.evaluate_condition("${nonexist} is not none", {}) is False
        assert engine.evaluate_condition("${nonexist} is none", {}) is True

    def test_close_engine(self, engine):
        """Test closing engine properly"""
        engine.api_client = Mock()
        engine.close()
        engine.api_client.close.assert_called_once()

    def test_http_extract_variable_failure(self):
        """Test HTTP variable extraction failure"""
        client = Mock()
        client.request.return_value = APIResponse(
            status_code=200,
            headers={},
            body={"data": {"id": 123}},
            response_time=0.1,
            success=True
        )
        executor = HttpHookExecutor(api_client=client)

        config = HookConfig(
            name="extract_fail",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="/test",
            extract={"valid": "data.id", "invalid": "nonexistent.path"}
        )

        result = executor.execute(config, {})
        assert result.success is True
        assert "valid" in result.extracted_vars

    def test_http_list_index_extraction(self):
        """Test extracting from list by index"""
        client = Mock()
        client.request.return_value = APIResponse(
            status_code=200,
            headers={},
            body={"items": [{"name": "first"}, {"name": "second"}]},
            response_time=0.1,
            success=True
        )
        executor = HttpHookExecutor(api_client=client)

        config = HookConfig(
            name="list_extract",
            hook_type=HookType.HTTP,
            method="GET",
            endpoint="/test",
            extract={"first_name": "items.0.name"}
        )

        result = executor.execute(config, {})
        assert result.success is True
        assert result.extracted_vars["first_name"] == "first"

    def test_command_failure_with_stderr_and_stdout(self):
        """Test command failure with both stderr and stdout"""
        executor = CommandHookExecutor()
        config = HookConfig(
            name="fail_with_output",
            hook_type=HookType.COMMAND,
            command='echo "stdout message" >&2 && echo "error" && exit 1'
        )

        result = executor.execute(config, {})
        assert result.success is False
        assert "return code" in result.error_message or "1" in result.error_message

    def test_command_generic_exception(self):
        """Test command generic exception handling"""
        executor = CommandHookExecutor()
        config = HookConfig(
            name="exception_cmd",
            hook_type=HookType.COMMAND,
            command='nonexistent_command_xyz'
        )

        result = executor.execute(config, {})
        assert result.success is False

    def test_script_returns_non_dict(self, tmp_path):
        """Test script returns non-dict value"""
        script_content = '''
def execute(context):
    return "simple_string_result"
'''
        script_file = tmp_path / "string_return.py"
        script_file.write_text(script_content)

        executor = ScriptHookExecutor()
        config = HookConfig(
            name="string_return",
            hook_type=HookType.SCRIPT,
            script=str(script_file)
        )

        result = executor.execute(config, {})
        assert result.success is True
        assert "result" in result.extracted_vars

    def test_evaluate_condition_invalid_pattern(self, engine):
        """Test condition with invalid pattern returns True"""
        assert engine.evaluate_condition("invalid condition without variable", {}) is True

    def test_evaluate_condition_numeric_comparison_with_non_numeric(self, engine):
        """Test numeric comparison with non-numeric value returns False"""
        assert engine.evaluate_condition("${var} >= 100", {"var": "not_a_number"}) is False
        assert engine.evaluate_condition("${var} <= 50", {"var": "abc"}) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
