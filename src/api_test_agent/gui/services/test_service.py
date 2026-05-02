"""
API Test Agent GUI - 测试用例管理服务

提供测试用例 CRUD 操作、YAML 文件读写和测试用例验证
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import json
import uuid
from datetime import datetime

from ..config import settings
from ..models.test import (
    TestCase, TestCaseCreate, TestCaseUpdate, 
    TestCaseYAML, TestStepConfig, AssertionConfig
)
from ..utils.validation import (
    validate_test_id,
    validate_yaml_size,
    validate_yaml_file_size,
    validate_path_is_safe,
    YAML_MAX_SIZE,
)


def _ensure_dirs():
    """确保测试用例目录存在"""
    Path(settings.tests_dir).mkdir(parents=True, exist_ok=True)


def _get_test_file(test_id: str) -> Path:
    """获取测试用例文件路径"""
    validate_test_id(test_id)
    file_path = Path(settings.tests_dir) / f"{test_id}.yaml"
    validate_path_is_safe(settings.tests_dir, str(file_path))
    return file_path


def _test_to_yaml(test_data: Dict[str, Any]) -> str:
    """将测试数据转换为 YAML 格式"""
    yaml_content = {
        "name": test_data.get("name"),
        "description": test_data.get("description"),
        "variables": test_data.get("variables", {}),
        "steps": []
    }
    
    for step in test_data.get("steps", []):
        step_dict = {
            "name": step.get("name"),
            "request": {
                "method": step.get("method", "GET"),
                "url": step.get("endpoint"),
            }
        }
        
        if step.get("params"):
            step_dict["request"]["params"] = step["params"]
        if step.get("headers"):
            step_dict["request"]["headers"] = step["headers"]
        if step.get("json"):
            step_dict["request"]["json"] = step["json"]
        if step.get("data"):
            step_dict["request"]["data"] = step["data"]
        
        if step.get("assertions"):
            step_dict["assertions"] = step["assertions"]
        
        if step.get("extract"):
            step_dict["extract"] = step["extract"]
        
        yaml_content["steps"].append(step_dict)
    
    return yaml.dump(yaml_content, allow_unicode=True, default_flow_style=False)


def _yaml_to_test(yaml_content: str) -> Dict[str, Any]:
    """将 YAML 格式转换为测试数据"""
    validate_yaml_size(yaml_content)
    data = yaml.safe_load(yaml_content)
    if not data:
        return {}
    
    steps = []
    for step in data.get("steps", []):
        request = step.get("request", {})
        step_dict = {
            "name": step.get("name", ""),
            "method": request.get("method", "GET"),
            "endpoint": request.get("url", ""),
            "params": request.get("params", {}),
            "headers": request.get("headers", {}),
            "json": request.get("json"),
            "data": request.get("data"),
            "assertions": step.get("assertions", []),
            "extract": step.get("extract", {}),
        }
        steps.append(step_dict)
    
    return {
        "name": data.get("name", ""),
        "description": data.get("description"),
        "variables": data.get("variables", {}),
        "steps": steps,
    }


def list_tests(project_id: Optional[str] = None) -> List[TestCase]:
    """获取测试用例列表"""
    _ensure_dirs()
    tests = []
    tests_dir = Path(settings.tests_dir)
    
    for file in tests_dir.glob("*.yaml"):
        try:
            validate_path_is_safe(settings.tests_dir, str(file))
            validate_yaml_file_size(file)
            with open(file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    test_id = file.stem
                    test_data = {
                        "id": test_id,
                        "name": data.get("name", file.stem),
                        "description": data.get("description"),
                        "variables": data.get("variables", {}),
                        "steps": [
                            TestStepConfig(
                                name=step.get("name", ""),
                                method=step.get("request", {}).get("method", "GET"),
                                endpoint=step.get("request", {}).get("url", ""),
                                params=step.get("request", {}).get("params", {}),
                                headers=step.get("request", {}).get("headers", {}),
                                json_data=step.get("request", {}).get("json"),
                                data=step.get("request", {}).get("data"),
                                assertions=[AssertionConfig(**a) for a in step.get("assertions", [])] if step.get("assertions") else [],
                                extract=step.get("extract", {}),
                            )
                            for step in data.get("steps", [])
                        ],
                        "project_id": data.get("project_id"),
                        "file_path": str(file),
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "last_result": data.get("last_result"),
                    }
                    
                    if project_id is None or test_data["project_id"] == project_id:
                        tests.append(TestCase(**test_data))
        except Exception:
            continue
    
    tests.sort(key=lambda t: t.name)
    return tests


def create_test(test_data: TestCaseCreate) -> TestCase:
    """创建测试用例"""
    _ensure_dirs()
    test_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    test_dict = {
        "id": test_id,
        "name": test_data.name,
        "description": test_data.description,
        "variables": test_data.variables,
        "steps": [step.model_dump(by_alias=True) for step in test_data.steps],
        "project_id": test_data.project_id,
        "created_at": now,
        "updated_at": now,
        "last_result": None,
    }
    
    _save_test(test_id, test_dict)
    return TestCase(**test_dict)


def get_test(test_id: str) -> Optional[TestCase]:
    """获取单个测试用例"""
    file_path = _get_test_file(test_id)
    if not file_path.exists():
        return None
    
    validate_yaml_file_size(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        if not data:
            return None
        
        test_data = {
            "id": test_id,
            "name": data.get("name", test_id),
            "description": data.get("description"),
            "variables": data.get("variables", {}),
            "steps": [
                TestStepConfig(
                    name=step.get("name", ""),
                    method=step.get("request", {}).get("method", "GET"),
                    endpoint=step.get("request", {}).get("url", ""),
                    params=step.get("request", {}).get("params", {}),
                    headers=step.get("request", {}).get("headers", {}),
                    json_data=step.get("request", {}).get("json"),
                    data=step.get("request", {}).get("data"),
                    assertions=[AssertionConfig(**a) for a in step.get("assertions", [])] if step.get("assertions") else [],
                    extract=step.get("extract", {}),
                )
                for step in data.get("steps", [])
            ],
            "project_id": data.get("project_id"),
            "file_path": str(file_path),
            "created_at": data.get("created_at", datetime.now().isoformat()),
            "updated_at": data.get("updated_at", datetime.now().isoformat()),
            "last_result": data.get("last_result"),
        }
        
        return TestCase(**test_data)


def update_test(test_id: str, test_data: TestCaseUpdate) -> Optional[TestCase]:
    """更新测试用例"""
    file_path = _get_test_file(test_id)
    if not file_path.exists():
        return None
    
    validate_yaml_file_size(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        if not data:
            return None
    
    update_dict = test_data.model_dump(exclude_unset=True)
    
    if "name" in update_dict:
        data["name"] = update_dict["name"]
    if "description" in update_dict:
        data["description"] = update_dict["description"]
    if "variables" in update_dict:
        data["variables"] = update_dict["variables"]
    if "steps" in update_dict:
        data["steps"] = [step.model_dump(by_alias=True) for step in update_dict["steps"]]
    
    data["updated_at"] = datetime.now().isoformat()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    return get_test(test_id)


def delete_test(test_id: str) -> bool:
    """删除测试用例"""
    file_path = _get_test_file(test_id)
    if not file_path.exists():
        return False
    
    file_path.unlink()
    return True


def get_test_yaml(test_id: str) -> Optional[TestCaseYAML]:
    """获取测试用例的 YAML 格式"""
    file_path = _get_test_file(test_id)
    if not file_path.exists():
        return None
    
    validate_yaml_file_size(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()
    
    return TestCaseYAML(yaml_content=yaml_content)


def create_test_from_yaml(yaml_content: str, project_id: Optional[str] = None) -> TestCase:
    """从 YAML 内容创建测试用例"""
    test_data = _yaml_to_test(yaml_content)
    
    steps = []
    for step in test_data.get("steps", []):
        steps.append(TestStepConfig(
            name=step.get("name", ""),
            method=step.get("method", "GET"),
            endpoint=step.get("endpoint", ""),
            params=step.get("params", {}),
            headers=step.get("headers", {}),
            json_data=step.get("json"),
            data=step.get("data"),
            assertions=[AssertionConfig(**a) for a in step.get("assertions", [])] if step.get("assertions") else [],
            extract=step.get("extract", {}),
        ))
    
    test_create = TestCaseCreate(
        name=test_data.get("name", "Untitled"),
        description=test_data.get("description"),
        variables=test_data.get("variables", {}),
        steps=steps,
        project_id=project_id,
    )
    
    return create_test(test_create)


def _save_test(test_id: str, test_data: Dict[str, Any]):
    """保存测试用例到 YAML 文件"""
    file_path = _get_test_file(test_id)
    yaml_content = _test_to_yaml(test_data)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)


def validate_test(test_data: TestCaseCreate) -> List[str]:
    """验证测试用例配置"""
    errors = []
    
    if not test_data.name:
        errors.append("测试用例名称不能为空")
    
    if not test_data.steps:
        errors.append("测试用例至少需要一个步骤")
    
    for i, step in enumerate(test_data.steps):
        if not step.name:
            errors.append(f"步骤 {i+1} 缺少名称")
        if not step.endpoint:
            errors.append(f"步骤 {i+1} 缺少端点 URL")
        if step.method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            errors.append(f"步骤 {i+1} 的 HTTP 方法无效")
    
    return errors
