"""
API Test Agent GUI - 环境配置管理服务

提供环境配置的 CRUD 操作、环境切换和变量继承处理
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import json
import uuid
from datetime import datetime

from ..config import settings


def _ensure_dirs():
    """确保环境配置目录存在"""
    env_dir = Path(settings.data_dir) / "environments"
    env_dir.mkdir(parents=True, exist_ok=True)
    return env_dir


def _get_env_file(env_id: str) -> Path:
    """获取环境配置文件路径"""
    env_dir = _ensure_dirs()
    return env_dir / f"{env_id}.yaml"


def list_environments(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取环境配置列表"""
    env_dir = _ensure_dirs()
    environments = []
    
    for file in env_dir.glob("*.yaml"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    env_id = file.stem
                    env_data = {
                        "id": env_id,
                        "name": data.get("name", env_id),
                        "description": data.get("description"),
                        "base_url": data.get("base_url", ""),
                        "variables": data.get("variables", {}),
                        "headers": data.get("headers", {}),
                        "project_id": data.get("project_id"),
                        "is_default": data.get("is_default", False),
                        "created_at": data.get("created_at", datetime.now().isoformat()),
                        "updated_at": data.get("updated_at", datetime.now().isoformat()),
                    }
                    
                    if project_id is None or env_data["project_id"] == project_id:
                        environments.append(env_data)
        except Exception:
            continue
    
    environments.sort(key=lambda e: e.get("name", ""))
    return environments


def create_environment(env_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建环境配置"""
    _ensure_dirs()
    env_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    env_dict = {
        "id": env_id,
        "name": env_data.get("name", "New Environment"),
        "description": env_data.get("description"),
        "base_url": env_data.get("base_url", ""),
        "variables": env_data.get("variables", {}),
        "headers": env_data.get("headers", {}),
        "project_id": env_data.get("project_id"),
        "is_default": env_data.get("is_default", False),
        "created_at": now,
        "updated_at": now,
    }
    
    file_path = _get_env_file(env_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(env_dict, f, allow_unicode=True, default_flow_style=False)
    
    return env_dict


def get_environment(env_id: str) -> Optional[Dict[str, Any]]:
    """获取单个环境配置"""
    file_path = _get_env_file(env_id)
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def update_environment(env_id: str, env_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新环境配置"""
    file_path = _get_env_file(env_id)
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        if not data:
            return None
    
    for key, value in env_data.items():
        if key in ["name", "description", "base_url", "variables", "headers", "project_id", "is_default"]:
            data[key] = value
    
    data["updated_at"] = datetime.now().isoformat()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    return data


def delete_environment(env_id: str) -> bool:
    """删除环境配置"""
    file_path = _get_env_file(env_id)
    if not file_path.exists():
        return False
    
    file_path.unlink()
    return True


def get_active_environment(project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """获取当前活动的环境配置"""
    environments = list_environments(project_id)
    
    # 查找默认环境
    for env in environments:
        if env.get("is_default"):
            return env
    
    # 如果没有默认环境，返回第一个
    return environments[0] if environments else None


def resolve_variables(env_id: str, test_variables: Optional[Dict] = None) -> Dict[str, Any]:
    """解析环境变量和测试变量的合并"""
    env = get_environment(env_id)
    if not env:
        return test_variables or {}
    
    env_variables = env.get("variables", {})
    merged = {**env_variables}
    
    if test_variables:
        merged.update(test_variables)
    
    return merged
