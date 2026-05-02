"""
API Test Agent GUI - 项目数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    """项目基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    base_url: Optional[str] = Field(None, description="API 基础 URL")


class ProjectCreate(ProjectBase):
    """创建项目模型"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    base_url: Optional[str] = None


class Project(ProjectBase):
    """项目完整模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    test_count: int = Field(default=0, description="测试用例数量")
    last_run_at: Optional[datetime] = None

    class Config:
        from_attributes = True
