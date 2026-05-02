"""
API Test Agent GUI - 测试用例数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AssertionConfig(BaseModel):
    """断言配置"""
    type: str = Field(..., description="断言类型")
    name: Optional[str] = Field(None, description="断言名称")
    expected: Any = Field(None, description="期望值")
    path: Optional[str] = Field(None, description="JSON Path")
    key: Optional[str] = Field(None, description="键名")
    script: Optional[str] = Field(None, description="自定义脚本")
    assertion_schema: Optional[Dict] = Field(None, description="JSON Schema", alias="schema")
    
    model_config = {"protected_namespaces": ()}


class TestStepConfig(BaseModel):
    """测试步骤配置"""
    name: str = Field(..., description="步骤名称")
    method: str = Field(default="GET", description="HTTP 方法")
    endpoint: str = Field(..., description="API 端点")
    params: Optional[Dict] = Field(default_factory=dict, description="查询参数")
    headers: Optional[Dict] = Field(default_factory=dict, description="请求头")
    json_data: Optional[Dict] = Field(None, description="JSON 请求体", alias="json")
    data: Optional[Any] = Field(None, description="表单数据")
    assertions: Optional[List[AssertionConfig]] = Field(default_factory=list, description="断言列表")
    extract: Optional[Dict] = Field(default_factory=dict, description="变量提取")


class TestCaseBase(BaseModel):
    """测试用例基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="用例名称")
    description: Optional[str] = Field(None, description="用例描述")
    variables: Optional[Dict] = Field(default_factory=dict, description="变量")
    steps: List[TestStepConfig] = Field(default_factory=list, description="测试步骤")


class TestCaseCreate(TestCaseBase):
    """创建测试用例模型"""
    project_id: Optional[str] = Field(None, description="所属项目 ID")


class TestCaseUpdate(BaseModel):
    """更新测试用例模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    variables: Optional[Dict] = None
    steps: Optional[List[TestStepConfig]] = None


class TestCaseYAML(BaseModel):
    """YAML 格式测试用例"""
    yaml_content: str = Field(..., description="YAML 内容")


class TestCase(TestCaseBase):
    """测试用例完整模型"""
    id: str
    project_id: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_result: Optional[Dict] = None

    class Config:
        from_attributes = True
