"""
API Test Agent GUI - 项目管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import List

from ..models.project import Project, ProjectCreate, ProjectUpdate
from ..services import project_service

router = APIRouter()


@router.get("/", response_model=List[Project])
async def list_projects():
    """获取项目列表"""
    return project_service.list_projects()


@router.post("/", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate):
    """创建项目"""
    return project_service.create_project(project)


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """获取项目详情"""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project: ProjectUpdate):
    """更新项目"""
    updated = project_service.update_project(project_id, project)
    if not updated:
        raise HTTPException(status_code=404, detail="项目不存在")
    return updated


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str):
    """删除项目"""
    success = project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="项目不存在")


@router.get("/{project_id}/stats")
async def get_project_stats(project_id: str):
    """获取项目统计数据"""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project_service.get_project_stats(project_id)
