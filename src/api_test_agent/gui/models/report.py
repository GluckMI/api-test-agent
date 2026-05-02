"""
API Test Agent GUI - 报告数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReportSummary(BaseModel):
    """报告摘要"""
    id: str
    test_name: str
    status: str = Field(..., description="执行状态: PASS/FAIL")
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float = Field(..., description="通过率")
    total_time: float = Field(..., description="总耗时（秒）")
    executed_at: datetime
    report_format: str = Field(default="json", description="报告格式")


class TestReport(ReportSummary):
    """完整测试报告"""
    test_results: List[Dict[str, Any]] = Field(default_factory=list, description="详细测试结果")
    error_messages: Optional[Dict] = Field(None, description="错误信息")
    environment: Optional[str] = Field(None, description="执行环境")
    
    class Config:
        from_attributes = True
