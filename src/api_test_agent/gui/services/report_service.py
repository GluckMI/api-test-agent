"""
API Test Agent GUI - 报告管理服务

提供报告生成、存储、查询和统计功能
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from ..config import settings
from ..models.report import ReportSummary, TestReport


def _ensure_dirs():
    """确保报告目录存在"""
    Path(settings.reports_dir).mkdir(parents=True, exist_ok=True)


def list_reports(test_id: Optional[str] = None, limit: int = 50) -> List[ReportSummary]:
    """获取报告列表"""
    _ensure_dirs()
    reports = []
    reports_dir = Path(settings.reports_dir)
    
    for file in reports_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                summary = ReportSummary(
                    id=data.get("id", file.stem),
                    test_name=data.get("test_name", file.stem),
                    status=data.get("status", "UNKNOWN"),
                    total_tests=data.get("total_tests", 0),
                    passed_tests=data.get("passed_tests", 0),
                    failed_tests=data.get("failed_tests", 0),
                    pass_rate=data.get("pass_rate", 0.0),
                    total_time=data.get("total_time", 0.0),
                    executed_at=datetime.fromisoformat(data["executed_at"]) if data.get("executed_at") else datetime.now(),
                    report_format=data.get("report_format", "json"),
                )
                
                # 过滤特定测试的报告
                if test_id is None or data.get("test_id") == test_id:
                    reports.append(summary)
        except Exception:
            continue
    
    # 按执行时间倒序排序
    reports.sort(key=lambda r: r.executed_at, reverse=True)
    return reports[:limit]


def get_report(report_id: str) -> Optional[TestReport]:
    """获取报告详情"""
    report_file = Path(settings.reports_dir) / f"{report_id}.json"
    if not report_file.exists():
        return None
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return TestReport(
                id=data.get("id", report_id),
                test_name=data.get("test_name", report_id),
                status=data.get("status", "UNKNOWN"),
                total_tests=data.get("total_tests", 0),
                passed_tests=data.get("passed_tests", 0),
                failed_tests=data.get("failed_tests", 0),
                pass_rate=data.get("pass_rate", 0.0),
                total_time=data.get("total_time", 0.0),
                executed_at=datetime.fromisoformat(data["executed_at"]) if data.get("executed_at") else datetime.now(),
                report_format=data.get("report_format", "json"),
                test_results=data.get("test_results", []),
                error_messages=data.get("error_messages"),
                environment=data.get("environment"),
            )
    except Exception:
        return None


def delete_report(report_id: str) -> bool:
    """删除报告"""
    report_file = Path(settings.reports_dir) / f"{report_id}.json"
    if not report_file.exists():
        return False
    
    report_file.unlink()
    return True


def get_report_stats() -> Dict[str, Any]:
    """获取报告统计信息"""
    _ensure_dirs()
    reports_dir = Path(settings.reports_dir)
    
    total_reports = 0
    passed_reports = 0
    failed_reports = 0
    total_time = 0.0
    pass_rates = []
    
    for file in reports_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_reports += 1
                
                if data.get("status") == "PASS":
                    passed_reports += 1
                else:
                    failed_reports += 1
                
                total_time += data.get("total_time", 0.0)
                pass_rates.append(data.get("pass_rate", 0.0))
        except Exception:
            continue
    
    avg_pass_rate = sum(pass_rates) / len(pass_rates) if pass_rates else 0.0
    
    return {
        "total_reports": total_reports,
        "passed_reports": passed_reports,
        "failed_reports": failed_reports,
        "total_time": round(total_time, 3),
        "avg_pass_rate": round(avg_pass_rate, 2),
        "pass_rate_trend": _calculate_pass_rate_trend(),
    }


def _calculate_pass_rate_trend() -> List[Dict[str, Any]]:
    """计算通过率趋势"""
    _ensure_dirs()
    reports_dir = Path(settings.reports_dir)
    trends = []
    
    for file in sorted(reports_dir.glob("*.json")):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                trends.append({
                    "executed_at": data.get("executed_at"),
                    "pass_rate": data.get("pass_rate", 0.0),
                    "total_time": data.get("total_time", 0.0),
                    "status": data.get("status"),
                })
        except Exception:
            continue
    
    return trends[-20:]  # 返回最近 20 条记录


def export_report(report_id: str, format: str = "json") -> Optional[str]:
    """导出报告"""
    report = get_report(report_id)
    if not report:
        return None
    
    if format == "json":
        return json.dumps(report.model_dump(), ensure_ascii=False, indent=2)
    elif format == "markdown":
        return _to_markdown(report)
    else:
        return json.dumps(report.model_dump(), ensure_ascii=False, indent=2)


def _to_markdown(report: TestReport) -> str:
    """将报告转换为 Markdown 格式"""
    md = f"# 测试报告：{report.test_name}\n\n"
    md += f"- **执行时间**: {report.executed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"- **状态**: {'✅ 通过' if report.status == 'PASS' else '❌ 失败'}\n"
    md += f"- **通过率**: {report.pass_rate:.1f}%\n"
    md += f"- **总耗时**: {report.total_time:.3f}s\n\n"
    
    md += "## 测试步骤结果\n\n"
    md += "| 步骤 | 状态 | 耗时(s) | 消息 |\n"
    md += "|------|------|---------|------|\n"
    
    for i, step in enumerate(report.test_results, 1):
        status = "✅" if step.get("passed") else "❌"
        md += f"| {i}. {step.get('name', 'N/A')} | {status} | {step.get('response_time', 0):.3f} | {step.get('error', '')} |\n"
    
    if report.error_messages:
        md += "\n## 错误信息\n\n"
        for key, value in report.error_messages.items():
            md += f"- **{key}**: {value}\n"
    
    return md
