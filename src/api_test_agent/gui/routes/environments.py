"""
API Test Agent GUI - 环境管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from ..services import environment_service

router = APIRouter()


@router.get("/")
async def list_environments(project_id: Optional[str] = None):
    """获取环境配置列表"""
    return environment_service.list_environments(project_id)


@router.post("/", status_code=201)
async def create_environment(env_data: dict):
    """创建环境配置"""
    return environment_service.create_environment(env_data)


@router.get("/{env_id}")
async def get_environment(env_id: str):
    """获取环境配置详情"""
    env = environment_service.get_environment(env_id)
    if not env:
        raise HTTPException(status_code=404, detail="环境配置不存在")
    return env


@router.put("/{env_id}")
async def update_environment(env_id: str, env_data: dict):
    """更新环境配置"""
    updated = environment_service.update_environment(env_id, env_data)
    if not updated:
        raise HTTPException(status_code=404, detail="环境配置不存在")
    return updated


@router.delete("/{env_id}", status_code=204)
async def delete_environment(env_id: str):
    """删除环境配置"""
    success = environment_service.delete_environment(env_id)
    if not success:
        raise HTTPException(status_code=404, detail="环境配置不存在")


@router.get("/active")
async def get_active_environment(project_id: Optional[str] = None):
    """获取当前活动环境"""
    env = environment_service.get_active_environment(project_id)
    if not env:
        raise HTTPException(status_code=404, detail="没有可用的环境配置")
    return env
