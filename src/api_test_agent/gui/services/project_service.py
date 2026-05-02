"""
API Test Agent GUI - 项目管理服务

提供项目 CRUD 操作、文件管理和统计数据计算
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime
import shutil

from ..config import settings
from ..models.project import Project, ProjectCreate, ProjectUpdate


def _ensure_dirs():
    """确保必要的目录存在"""
    Path(settings.projects_dir).mkdir(parents=True, exist_ok=True)


def _get_project_file(project_id: str) -> Path:
    """获取项目文件路径"""
    return Path(settings.projects_dir) / f"{project_id}.json"


def _read_project(project_id: str) -> Optional[Dict[str, Any]]:
    """读取项目数据"""
    file_path = _get_project_file(project_id)
    if not file_path.exists():
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_project(project_id: str, data: Dict[str, Any]):
    """保存项目数据"""
    file_path = _get_project_file(project_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_projects() -> List[Project]:
    """获取所有项目列表"""
    _ensure_dirs()
    projects = []
    projects_dir = Path(settings.projects_dir)
    
    for file in projects_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                projects.append(Project(**data))
        except Exception:
            continue
    
    # 按创建时间倒序排序
    projects.sort(key=lambda p: p.created_at, reverse=True)
    return projects


def create_project(project_data: ProjectCreate) -> Project:
    """创建新项目"""
    _ensure_dirs()
    project_id = str(uuid.uuid4())
    now = datetime.now()
    
    project_dict = {
        "id": project_id,
        "name": project_data.name,
        "description": project_data.description,
        "base_url": project_data.base_url,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "test_count": 0,
        "last_run_at": None,
    }
    
    _save_project(project_id, project_dict)
    
    # 创建项目目录结构
    project_dir = Path(settings.projects_dir) / project_id
    project_dir.mkdir(exist_ok=True)
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "reports").mkdir(exist_ok=True)
    (project_dir / "configs").mkdir(exist_ok=True)
    (project_dir / "environments").mkdir(exist_ok=True)
    
    return Project(**project_dict)


def get_project(project_id: str) -> Optional[Project]:
    """获取单个项目详情"""
    data = _read_project(project_id)
    if data is None:
        return None
    return Project(**data)


def update_project(project_id: str, project_data: ProjectUpdate) -> Optional[Project]:
    """更新项目信息"""
    data = _read_project(project_id)
    if data is None:
        return None
    
    # 更新字段
    update_dict = project_data.model_dump(exclude_unset=True)
    data.update(update_dict)
    data["updated_at"] = datetime.now().isoformat()
    
    _save_project(project_id, data)
    return Project(**data)


def delete_project(project_id: str) -> bool:
    """删除项目及其所有关联数据"""
    project_file = _get_project_file(project_id)
    if not project_file.exists():
        return False
    
    # 删除项目元数据文件
    project_file.unlink()
    
    # 删除项目目录
    project_dir = Path(settings.projects_dir) / project_id
    if project_dir.exists():
        shutil.rmtree(project_dir)
    
    return True


def get_project_stats(project_id: str) -> Dict[str, Any]:
    """获取项目统计数据"""
    project = get_project(project_id)
    if project is None:
        return {}
    
    # 统计测试用例数量
    tests_dir = Path(settings.tests_dir)
    test_count = 0
    if tests_dir.exists():
        test_count = len(list(tests_dir.glob("*.yaml")))
    
    # 统计报告数量
    reports_dir = Path(settings.reports_dir)
    report_count = 0
    if reports_dir.exists():
        report_count = len(list(reports_dir.glob("*.json")))
    
    return {
        "test_count": test_count,
        "report_count": report_count,
        "last_run_at": project.last_run_at,
    }
