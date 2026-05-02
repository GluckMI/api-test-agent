"""
API Test Agent GUI - 报告管理路由
"""
from fastapi import APIRouter, HTTPException, Response
from typing import List, Optional

from ..models.report import ReportSummary, TestReport
from ..services import report_service

router = APIRouter()


@router.get("/stats")
async def get_report_stats():
    """获取报告统计信息"""
    return report_service.get_report_stats()


@router.get("/", response_model=List[ReportSummary])
async def list_reports(test_id: Optional[str] = None, limit: int = 50):
    """获取报告列表"""
    return report_service.list_reports(test_id, limit)


@router.get("/{report_id}", response_model=TestReport)
async def get_report(report_id: str):
    """获取报告详情"""
    report = report_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report


@router.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """删除报告"""
    success = report_service.delete_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="报告不存在")


@router.get("/{report_id}/export")
async def export_report(report_id: str, format: str = "json"):
    """导出报告"""
    report_content = report_service.export_report(report_id, format)
    if not report_content:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if format == "markdown":
        return Response(content=report_content, media_type="text/markdown")
    else:
        return Response(content=report_content, media_type="application/json")
