"""
API 接口自动化测试 Agent - 工具函数
"""
import os
import json
import yaml
import hashlib
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


def load_config_file(file_path: str) -> dict:
    """加载配置文件（支持 JSON 和 YAML）"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在：{file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif path.suffix == '.json':
            return json.load(f)
        else:
            # 尝试自动检测
            try:
                return json.load(f)
            except:
                f.seek(0)
                return yaml.safe_load(f)


def save_config_file(file_path: str, config: dict):
    """保存配置文件"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.suffix in ['.yaml', '.yml']:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, indent=2, allow_unicode=True)
    else:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


def generate_test_id(prefix: str = "test") -> str:
    """生成唯一的测试 ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(4)
    return f"{prefix}_{timestamp}_{random_part}"


def calculate_hash(data: Any) -> str:
    """计算数据的哈希值"""
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    else:
        data_str = str(data)
    
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:16]


def merge_dicts(base: dict, override: dict) -> dict:
    """深度合并两个字典"""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 1:
        return f"{seconds*1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.3f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def safe_get(data: Any, *keys, default=None):
    """安全地获取嵌套字典的值"""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        elif isinstance(current, (list, tuple)):
            try:
                index = int(key) if isinstance(key, str) else key
                current = current[index]
            except (IndexError, ValueError):
                return default
        else:
            return default
        
        if current is None:
            return default
    
    return current


def validate_url(url: str) -> bool:
    """验证 URL 格式"""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def create_environment_template() -> dict:
    """创建环境配置模板"""
    return {
        "dev": {
            "base_url": "http://localhost:8080",
            "timeout": 30,
            "headers": {}
        },
        "staging": {
            "base_url": "https://staging.example.com",
            "timeout": 30,
            "headers": {}
        },
        "prod": {
            "base_url": "https://api.example.com",
            "timeout": 60,
            "headers": {}
        }
    }


def create_test_case_template() -> dict:
    """创建测试用例模板"""
    return {
        "name": "示例测试用例",
        "description": "这是一个测试用例的描述",
        "variables": {},
        "steps": [
            {
                "name": "步骤名称",
                "method": "GET",
                "endpoint": "/api/v1/resource",
                "params": {},
                "headers": {},
                "assertions": [
                    {
                        "type": "status_code",
                        "expected": 200,
                        "name": "状态码检查"
                    }
                ]
            }
        ]
    }


def print_banner(title: str):
    """打印漂亮的标题栏"""
    border = "=" * 60
    try:
        print(f"\n{border}")
        print(f"  {title}")
        print(f"{border}\n")
    except UnicodeEncodeError:
        # Windows 控制台编码问题，使用纯文本
        print(f"\n{border}")
        print(f"  API 接口自动化测试")
        print(f"{border}\n")


def print_success(message: str):
    """打印成功消息"""
    try:
        print(f"✅ {message}")
    except UnicodeEncodeError:
        print(f"[PASS] {message}")


def print_error(message: str):
    """打印错误消息"""
    try:
        print(f"❌ {message}")
    except UnicodeEncodeError:
        print(f"[ERROR] {message}")


def print_warning(message: str):
    """打印警告消息"""
    try:
        print(f"⚠️ {message}")
    except UnicodeEncodeError:
        print(f"[WARN] {message}")


def print_info(message: str):
    """打印信息消息"""
    try:
        print(f"📝 {message}")
    except UnicodeEncodeError:
        print(f"[INFO] {message}")


class Color:
    """控制台颜色代码"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def colored(text: str, color: str) -> str:
    """给文本添加颜色"""
    colors_map = {
        'header': Color.HEADER,
        'blue': Color.OKBLUE,
        'cyan': Color.OKCYAN,
        'green': Color.OKGREEN,
        'yellow': Color.WARNING,
        'red': Color.FAIL,
        'bold': Color.BOLD,
        'underline': Color.UNDERLINE
    }
    
    color_code = colors_map.get(color.lower(), '')
    end_code = Color.ENDC
    
    return f"{color_code}{text}{end_code}"
