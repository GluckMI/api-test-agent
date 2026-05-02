"""
API Test Agent GUI - Input validation utilities

Provides security validation functions for:
- Path traversal prevention
- Test ID format validation
- YAML file size limits
- Project ID format validation
"""
import re
from pathlib import Path

YAML_MAX_SIZE = 10 * 1024 * 1024  # 10MB

TEST_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
MAX_ID_LENGTH = 128


def validate_path_traversal(path: str) -> None:
    """
    Check for path traversal attempts.
    Raises ValueError if path contains '..' or other suspicious patterns.
    """
    if '..' in path:
        raise ValueError(f"Invalid path: path traversal detected")
    if path.startswith('/') or path.startswith('\\'):
        raise ValueError(f"Invalid path: absolute paths not allowed")


def validate_path_is_safe(base_dir: str, target_path: str) -> Path:
    """
    Ensure the resolved path is within the base directory.
    Returns the resolved Path if safe, raises ValueError otherwise.
    """
    base = Path(base_dir).resolve()
    target = Path(target_path).resolve()
    if not str(target).startswith(str(base)):
        raise ValueError(f"Invalid path: outside allowed directory")
    return target


def validate_test_id(test_id: str) -> None:
    """
    Validate test_id format:
    - Only alphanumeric, underscore, and hyphen allowed
    - Maximum length: 128 characters
    - Cannot be empty
    """
    if not test_id:
        raise ValueError("Test ID cannot be empty")
    if len(test_id) > MAX_ID_LENGTH:
        raise ValueError(f"Test ID too long (max {MAX_ID_LENGTH} characters)")
    if not TEST_ID_PATTERN.match(test_id):
        raise ValueError("Test ID contains invalid characters (only alphanumeric, underscore, hyphen allowed)")


def validate_project_id(project_id: str) -> None:
    """
    Validate project_id format.
    Same rules as test_id.
    """
    if not project_id:
        raise ValueError("Project ID cannot be empty")
    if len(project_id) > MAX_ID_LENGTH:
        raise ValueError(f"Project ID too long (max {MAX_ID_LENGTH} characters)")
    if not TEST_ID_PATTERN.match(project_id):
        raise ValueError("Project ID contains invalid characters (only alphanumeric, underscore, hyphen allowed)")


def validate_yaml_size(content: str) -> None:
    """
    Validate YAML content size.
    Raises ValueError if content exceeds YAML_MAX_SIZE.
    """
    content_size = len(content.encode('utf-8'))
    if content_size > YAML_MAX_SIZE:
        raise ValueError(f"YAML content too large (max {YAML_MAX_SIZE / (1024*1024):.0f}MB)")


def validate_yaml_file_size(file_path: Path) -> None:
    """
    Validate YAML file size on disk.
    Raises ValueError if file exceeds YAML_MAX_SIZE.
    """
    file_size = file_path.stat().st_size
    if file_size > YAML_MAX_SIZE:
        raise ValueError(f"YAML file too large (max {YAML_MAX_SIZE / (1024*1024):.0f}MB)")
