"""
API Test Agent GUI - 服务层

提供业务逻辑服务
"""
from .project_service import (
    list_projects, create_project, get_project,
    update_project, delete_project, get_project_stats
)
from .test_service import (
    list_tests, create_test, get_test, update_test,
    delete_test, get_test_yaml, create_test_from_yaml, validate_test
)
from .environment_service import (
    list_environments, create_environment, get_environment,
    update_environment, delete_environment, get_active_environment,
    resolve_variables
)
from .execution_service import execution_service, ExecutionService, ExecutionState
from .report_service import (
    list_reports, get_report, delete_report, get_report_stats,
    export_report
)
