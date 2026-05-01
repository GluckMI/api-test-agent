"""
API 接口自动化测试 Agent - 报告生成器
"""
import json
from pathlib import Path
from typing import List
from datetime import datetime
from dataclasses import asdict

from .runner import TestSuiteResult, TestCaseResult


class ReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_json_report(self, result: TestSuiteResult, 
                            filename: str = None) -> str:
        """生成 JSON 格式报告"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_test_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # 转换数据为可序列化格式
        report_data = {
            "suite_name": result.suite_name,
            "start_time": result.start_time,
            "end_time": result.end_time,
            "total_tests": result.total_tests,
            "passed_tests": result.passed_tests,
            "failed_tests": result.failed_tests,
            "total_time_seconds": result.total_time,
            "pass_rate": round(result.passed_tests / result.total_tests * 100, 2) if result.total_tests > 0 else 0,
            "tests": [
                {
                    "name": tc.name,
                    "description": tc.description,
                    "passed": tc.passed,
                    "total_steps": tc.total_steps,
                    "passed_steps": tc.passed_steps,
                    "failed_steps": tc.failed_steps,
                    "total_time": tc.total_time,
                    "error_message": tc.error_message,
                    "steps": tc.step_results
                }
                for tc in result.test_results
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def generate_markdown_report(self, result: TestSuiteResult,
                                filename: str = None) -> str:
        """生成 Markdown 格式报告"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_test_report_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        lines = []
        
        # 标题
        lines.append("# API 接口自动化测试报告\n")
        
        # 概览
        lines.append("## 测试概览\n")
        pass_rate = result.passed_tests / result.total_tests * 100 if result.total_tests > 0 else 0
        lines.append(f"| 项目 | 值 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 测试套件 | {result.suite_name} |")
        lines.append(f"| 开始时间 | {result.start_time} |")
        lines.append(f"| 结束时间 | {result.end_time} |")
        lines.append(f"| 总耗时 | {result.total_time:.3f} 秒 |")
        lines.append(f"| 总用例数 | {result.total_tests} |")
        lines.append(f"| **通过率** | **{pass_rate:.1f}%** |")
        lines.append("")
        
        # 结果摘要
        status_icon = "✅" if result.failed_tests == 0 else "❌"
        lines.append(f"{status_icon} 测试{'通过' if result.failed_tests == 0 else '失败'}\n")
        lines.append(f"- ✅ 通过: {result.passed_tests}")
        lines.append(f"- ❌ 失败: {result.failed_tests}")
        lines.append(f"- 📊 总数: {result.total_tests}\n")
        
        # 详细信息
        lines.append("## 测试详情\n")
        
        for i, test in enumerate(result.test_results, 1):
            icon = "✅" if test.passed else "❌"
            lines.append(f"### {i}. {icon} {test.name}\n")
            
            if test.description:
                lines.append(f"> {test.description}\n")
            
            lines.append(f"- **状态**: {'通过' if test.passed else '失败'}")
            lines.append(f"- **步骤**: {test.passed_steps}/{test.total_steps}")
            lines.append(f"- **耗时**: {test.total_time:.3f}s")
            
            if test.error_message:
                lines.append(f"- **错误**: {test.error_message}")
            
            lines.append("")
            
            # 步骤详情
            if test.step_results:
                lines.append("**步骤详情**:\n")
                lines.append("| # | 步骤名称 | 方法 | 端点 | 状态码 | 耗时 | 结果 |")
                lines.append("|---|---------|------|------|--------|------|------|")
                
                for j, step in enumerate(test.step_results, 1):
                    status_icon = "✅" if step.get("passed", False) else "❌"
                    method = step.get("method", "N/A")
                    endpoint = step.get("endpoint", "")
                    if len(endpoint) > 40:
                        endpoint = endpoint[:37] + "..."
                    
                    lines.append(f"| {j} | {step.get('name', '')} | {method} | {endpoint} | "
                               f"{step.get('status_code', 'N/A')} | "
                               f"{step.get('response_time', 'N/A')}s | {status_icon} |")
                
                lines.append("")
                
                # 断言详情（失败的）
                failed_assertions = []
                for step in test.step_results:
                    for assertion in step.get("assertions", []):
                        if not assertion.get("passed", True):
                            failed_assertions.append({
                                "step": step.get("name"),
                                "assertion": assertion
                            })
                
                if failed_assertions:
                    lines.append("**失败的断言**:\n")
                    for fa in failed_assertions:
                        lines.append(f"• **{fa['step']} - {fa['assertion']['name']}**")
                        lines.append(f"  - 期望: {fa['assertion']['expected']}")
                        lines.append(f"  - 实际: {fa['assertion']['actual']}")
                        lines.append(f"  - 信息: {fa['assertion']['message']}\n")
            
            lines.append("---\n")
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return str(filepath)
    
    def generate_html_report(self, result: TestSuiteResult,
                            filename: str = None) -> str:
        """生成 HTML 格式报告"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_test_report_{timestamp}.html"
        
        filepath = self.output_dir / filename
        
        pass_rate = result.passed_tests / result.total_tests * 100 if result.total_tests > 0 else 0
        overall_status = "success" if result.failed_tests == 0 else "danger"
        
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API 测试报告 - {result.suite_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                background: #f5f5f5; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                  padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                 gap: 15px; margin-top: 20px; }}
        .stat-card {{ background: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px; 
                     text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
        .summary {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
                   box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .summary-bar {{ height: 30px; background: #e0e0e0; border-radius: 15px; overflow: hidden; 
                       margin: 15px 0; display: flex; }}
        .bar-passed {{ background: #4caf50; transition: width 0.3s; }}
        .bar-failed {{ background: #f44336; transition: width 0.3s; }}
        .test-case {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px;
                     box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .test-caseHeader {{ display: flex; justify-content: space-between; align-items: center; 
                          margin-bottom: 15px; cursor: pointer; }}
        .test-case-title {{ font-size: 1.2em; font-weight: bold; }}
        .test-case.status-success {{ border-left: 4px solid #4caf50; }}
        .test-case.status-failure {{ border-left: 4px solid #f44336; }}
        .step-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .step-table th, .step-table td {{ padding: 10px; text-align: left; 
                                         border-bottom: 1px solid #e0e0e0; }}
        .step-table th {{ background: #f5f5f5; font-weight: 600; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; 
                font-size: 0.85em; font-weight: 500; }}
        .badge-success {{ background: #e8f5e9; color: #4caf50; }}
        .badge-error {{ background: #ffebee; color: #f44336; }}
        .badge-info {{ background: #e3f2fd; color: #2196f3; }}
        .details {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; }}
        .details.open {{ max-height: 2000px; }}
        .error-msg {{ background: #ffebee; padding: 10px; border-radius: 5px; 
                     color: #c62828; margin: 10px 0; }}
        .assertion {{ background: #fff3e0; padding: 10px; margin: 5px 0; border-radius: 5px;
                     border-left: 3px solid #ff9800; }}
        .method {{ display: inline-block; padding: 2px 8px; border-radius: 4px; 
                  font-size: 0.8em; font-weight: bold; }}
        .method-GET {{ background: #e3f2fd; color: #1976d2; }}
        .method-POST {{ background: #e8f5e9; color: #388e3c; }}
        .method-PUT {{ background: #fff3e0; color: #f57c00; }}
        .method-DELETE {{ background: #ffebee; color: #d32f2f; }}
        .method-PATCH {{ background: #f3e5f5; color: #7b1fa2; }}
        @media (max-width: 768px) {{ .stats {{ grid-template-columns: 1fr 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 API 接口自动化测试报告</h1>
            <p>{result.suite_name}</p>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{result.total_tests}</div>
                    <div class="stat-label">总用例数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #4caf50;">{result.passed_tests}</div>
                    <div class="stat-label">通过</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #f44336;">{result.failed_tests}</div>
                    <div class="stat-label">失败</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{pass_rate:.1f}%</div>
                    <div class="stat-label">通过率</div>
                </div>
            </div>
        </div>

        <div class="summary">
            <h3>📊 执行摘要</h3>
            <p><strong>开始时间:</strong> {result.start_time}</p>
            <p><strong>结束时间:</strong> {result.end_time}</p>
            <p><strong>总耗时:</strong> {result.total_time:.3f} 秒</p>
            <div class="summary-bar">
                <div class="bar-passed" style="width: {pass_rate}%"></div>
                <div class="bar-failed" style="width: {100 - pass_rate}%"></div>
            </div>
        </div>

        <h2 style="margin-bottom: 15px;">🧪 测试详情</h2>
'''
        
        for i, test in enumerate(result.test_results, 1):
            status_class = "status-success" if test.passed else "status-failure"
            status_badge = '<span class="badge badge-success">✅ 通过</span>' if test.passed else '<span class="badge badge-error">❌ 失败</span>'
            
            html_content += f'''
        <div class="test-case {status_class}">
            <div class="test-caseHeader" onclick="toggleDetails(this)">
                <div>
                    <span class="test-case-title">{i}. {test.name}</span>
                    <br><small style="color: #666;">{test.description or ''}</small>
                </div>
                <div>
                    <span class="badge badge-info">{test.passed_steps}/{test.total_steps} 步骤</span>
                    {status_badge}
                </div>
            </div>
            <div class="details">
'''
            if test.error_message:
                html_content += f'<div class="error-msg">⚠️ {test.error_message}</div>\n'
            
            if test.step_results:
                html_content += '''
                <table class="step-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>步骤名称</th>
                            <th>方法</th>
                            <th>端点</th>
                            <th>状态码</th>
                            <th>耗时 (s)</th>
                            <th>结果</th>
                        </tr>
                    </thead>
                    <tbody>
'''
                for j, step in enumerate(test.step_results, 1):
                    method = step.get("method", "GET")
                    endpoint = step.get("endpoint", "")
                    if len(endpoint) > 50:
                        endpoint = endpoint[:47] + "..."
                    passed = step.get("passed", False)
                    status_icon = "✅" if passed else "❌"
                    badge_class = "badge-success" if passed else "badge-error"
                    
                    html_content += f'''
                        <tr>
                            <td>{j}</td>
                            <td>{step.get('name', '')}</td>
                            <td><span class="method method-{method}">{method}</span></td>
                            <td><code>{endpoint}</code></td>
                            <td>{step.get('status_code', 'N/A')}</td>
                            <td>{step.get('response_time', 'N/A')}</td>
                            <td><span class="badge {badge_class}">{status_icon}</span></td>
                        </tr>
'''
                
                html_content += '''
                    </tbody>
                </table>
'''
                
                # 失败的断言
                failed_assertions = []
                for step in test.step_results:
                    for assertion in step.get("assertions", []):
                        if not assertion.get("passed", True):
                            failed_assertions.append({
                                "step": step.get("name"),
                                "assertion": assertion
                            })
                
                if failed_assertions:
                    html_content += '<div style="margin-top: 15px;"><strong>❌ 失败的断言:</strong><br>\n'
                    for fa in failed_assertions:
                        html_content += f'''
                        <div class="assertion">
                            <strong>{fa['step']} - {fa['assertion']['name']}</strong><br>
                            期望: <code>{fa['assertion']['expected']}</code><br>
                            实际: <code>{fa['assertion']['actual']}</code><br>
                            信息: {fa['assertion']['message']}
                        </div>
'''
                    html_content += '</div>\n'
            
            html_content += '''
            </div>
        </div>
'''
        
        html_content += '''
    </div>

    <script>
        function toggleDetails(header) {
            const details = header.nextElementSibling;
            details.classList.toggle('open');
        }
        
        // 默认展开失败的测试用例
        document.querySelectorAll('.test-case.status-failure .details').forEach(el => {
            el.classList.add('open');
        });
    </script>
</body>
</html>
'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_all_reports(self, result: TestSuiteResult) -> dict:
        """生成所有格式的报告会话"""
        reports = {}
        
        reports['json'] = self.generate_json_report(result)
        reports['markdown'] = self.generate_markdown_report(result)
        reports['html'] = self.generate_html_report(result)
        
        return reports
