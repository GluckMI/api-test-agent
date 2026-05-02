"""
API Test Agent GUI - 测试用例管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from ..models.test import TestCase, TestCaseCreate, TestCaseUpdate, TestCaseYAML
from ..services import test_service
from ..utils.validation import validate_test_id, validate_yaml_size

router = APIRouter()


@router.get("/", response_model=List[TestCase])
async def list_tests(project_id: Optional[str] = None):
    """获取测试用例列表"""
    return test_service.list_tests(project_id)


@router.post("/", response_model=TestCase, status_code=201)
async def create_test(test: TestCaseCreate):
    """创建测试用例"""
    errors = test_service.validate_test(test)
    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))
    return test_service.create_test(test)


@router.get("/{test_id}", response_model=TestCase)
async def get_test(test_id: str):
    """获取测试用例详情"""
    try:
        validate_test_id(test_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    test = test_service.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return test


@router.put("/{test_id}", response_model=TestCase)
async def update_test(test_id: str, test: TestCaseUpdate):
    """更新测试用例"""
    try:
        validate_test_id(test_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    updated = test_service.update_test(test_id, test)
    if not updated:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return updated


@router.delete("/{test_id}", status_code=204)
async def delete_test(test_id: str):
    """删除测试用例"""
    try:
        validate_test_id(test_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    success = test_service.delete_test(test_id)
    if not success:
        raise HTTPException(status_code=404, detail="测试用例不存在")


@router.get("/{test_id}/yaml", response_model=TestCaseYAML)
async def get_test_yaml(test_id: str):
    """获取测试用例 YAML 格式"""
    try:
        validate_test_id(test_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    yaml_content = test_service.get_test_yaml(test_id)
    if not yaml_content:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return yaml_content


@router.post("/from-yaml", response_model=TestCase, status_code=201)
async def create_test_from_yaml(yaml_data: dict):
    """从 YAML 内容创建测试用例"""
    yaml_content = yaml_data.get("yaml_content", "")
    project_id = yaml_data.get("project_id")
    
    try:
        validate_yaml_size(yaml_content)
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))
    
    try:
        test = test_service.create_test_from_yaml(yaml_content, project_id)
        return test
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"YAML 解析失败: {str(e)}")
