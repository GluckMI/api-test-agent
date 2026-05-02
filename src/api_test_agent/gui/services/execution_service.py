"""
API Test Agent GUI - 测试执行服务

集成现有 test_runner，提供执行状态管理、结果收集和格式化
"""
from typing import Dict, Any, Optional, List, Callable
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
import yaml
import json

from ...runner import TestRunner, TestCaseResult, TestSuiteResult
from ..config import settings
from .test_service import get_test, _get_test_file


class ExecutionState:
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    STOPPED = "stopped"
    ERROR = "error"


class ExecutionRecord:
    """执行记录"""
    def __init__(self, execution_id: str, test_id: str):
        self.execution_id = execution_id
        self.test_id = test_id
        self.status = ExecutionState.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.logs: List[str] = []
        self.progress: float = 0.0
        self.total_steps: int = 0
        self.current_step: int = 0
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "test_id": self.test_id,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result": self.result,
            "logs": self.logs,
            "progress": self.progress,
            "total_steps": self.total_steps,
            "current_step": self.current_step,
            "error": self.error,
        }


class ExecutionService:
    """测试执行服务"""
    
    def __init__(self):
        self._executions: Dict[str, ExecutionRecord] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """获取执行记录"""
        return self._executions.get(execution_id)
    
    def list_executions(self) -> List[Dict[str, Any]]:
        """获取所有执行记录"""
        return [exec.to_dict() for exec in self._executions.values()]
    
    async def run_test(self, test_id: str, env_id: Optional[str] = None, 
                       on_progress: Optional[Callable] = None) -> Dict[str, Any]:
        """
        异步执行测试用例
        
        Args:
            test_id: 测试用例 ID
            env_id: 环境 ID（可选）
            on_progress: 进度回调函数
            
        Returns:
            执行结果字典
        """
        execution_id = str(uuid.uuid4())
        record = ExecutionRecord(execution_id, test_id)
        self._executions[execution_id] = record
        
        test = get_test(test_id)
        if not test:
            record.status = ExecutionState.ERROR
            record.error = f"测试用例 {test_id} 不存在"
            return record.to_dict()
        
        # 构建测试用例配置
        test_config = {
            "name": test.name,
            "description": test.description or "",
            "variables": test.variables or {},
            "steps": [
                {
                    "name": step.name,
                    "method": step.method,
                    "endpoint": step.endpoint,
                    "params": step.params or {},
                    "headers": step.headers or {},
                    "json": step.json_data,
                    "data": step.data,
                    "assertions": [a.model_dump() for a in (step.assertions or [])],
                    "extract": step.extract or {},
                }
                for step in test.steps
            ],
        }
        
        record.total_steps = len(test_config["steps"])
        record.status = ExecutionState.RUNNING
        record.start_time = datetime.now()
        
        # 执行测试
        try:
            runner = TestRunner()
            
            # 执行测试用例
            result = runner.execute_test_case(test_config)
            
            record.current_step = record.total_steps
            record.progress = 100.0
            record.end_time = datetime.now()
            
            # 转换结果为字典
            record.result = {
                "name": result.name,
                "description": result.description,
                "passed": result.passed,
                "total_steps": result.total_steps,
                "passed_steps": result.passed_steps,
                "failed_steps": result.failed_steps,
                "step_results": result.step_results,
                "total_time": result.total_time,
                "error_message": result.error_message,
            }
            
            record.status = ExecutionState.PASSED if result.passed else ExecutionState.FAILED
            
            # 保存报告
            await self._save_report(execution_id, test_id, record.result)
            
            # 调用进度回调
            if on_progress:
                on_progress(record.to_dict())
            
            runner.close()
            
        except Exception as e:
            record.status = ExecutionState.ERROR
            record.error = str(e)
            record.end_time = datetime.now()
            record.logs.append(f"执行错误: {str(e)}")
        
        return record.to_dict()
    
    async def run_tests_batch(self, test_ids: List[str], env_id: Optional[str] = None) -> Dict[str, Any]:
        """
        批量执行测试用例
        
        Args:
            test_ids: 测试用例 ID 列表
            env_id: 环境 ID（可选）
            
        Returns:
            批量执行结果
        """
        results = []
        for test_id in test_ids:
            result = await self.run_test(test_id, env_id)
            results.append(result)
        
        passed = sum(1 for r in results if r["status"] == ExecutionState.PASSED)
        failed = sum(1 for r in results if r["status"] in [ExecutionState.FAILED, ExecutionState.ERROR])
        
        return {
            "total": len(test_ids),
            "passed": passed,
            "failed": failed,
            "results": results,
        }
    
    async def _save_report(self, execution_id: str, test_id: str, result: Dict[str, Any]):
        """保存执行报告"""
        reports_dir = Path(settings.reports_dir)
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            "id": execution_id,
            "test_id": test_id,
            "test_name": result.get("name", ""),
            "status": "PASS" if result.get("passed") else "FAIL",
            "total_tests": 1,
            "passed_tests": 1 if result.get("passed") else 0,
            "failed_tests": 0 if result.get("passed") else 1,
            "pass_rate": 100.0 if result.get("passed") else 0.0,
            "total_time": result.get("total_time", 0),
            "executed_at": datetime.now().isoformat(),
            "report_format": "json",
            "test_results": result.get("step_results", []),
            "error_messages": {"error": result.get("error_message")} if result.get("error_message") else None,
            "environment": None,
        }
        
        report_file = reports_dir / f"{execution_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    def stop_execution(self, execution_id: str) -> bool:
        """停止执行（占位实现）"""
        record = self._executions.get(execution_id)
        if record and record.status == ExecutionState.RUNNING:
            record.status = ExecutionState.STOPPED
            record.end_time = datetime.now()
            return True
        return False
    
    def register_callback(self, execution_id: str, callback: Callable):
        """注册执行进度回调"""
        if execution_id not in self._callbacks:
            self._callbacks[execution_id] = []
        self._callbacks[execution_id].append(callback)
    
    def _notify_callbacks(self, execution_id: str, data: Dict[str, Any]):
        """通知所有回调"""
        callbacks = self._callbacks.get(execution_id, [])
        for callback in callbacks:
            try:
                callback(data)
            except Exception:
                pass


# 全局执行服务实例
execution_service = ExecutionService()
