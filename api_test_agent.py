"""
API 接口自动化测试 Agent - 主程序
支持命令行调用和 Python API 两种方式

使用示例:
    # 运行单个测试文件
    python api_test_agent.py run test.yaml
    
    # 运行目录下的所有测试
    python api_test_agent.py run tests/
    
    # 指定输出报告格式
    python api_test_agent.py run test.yaml --reports html,json
    
    # 指定环境配置
    python api_test_agent.py run test.yaml --env prod
"""
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import Config, config
from test_runner import TestRunner
from report_generator import ReportGenerator
from utils import (
    print_banner, print_success, print_error, 
    print_warning, print_info, colored, Color
)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="API 接口自动化测试 Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 运行单个测试文件
  python api_test_agent.py run test.yaml
  
  # 运行目录下的所有测试
  python api_test_agent.py run tests/ --reports html,markdown,json
  
  # 使用不同的报告格式
  python api_test_agent.py run test.yaml -r html
  
  # 生成配置文件模板
  python api_test_agent.py init
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # run 命令
    run_parser = subparsers.add_parser('run', help='运行测试')
    run_parser.add_argument('path', help='测试文件或目录路径')
    run_parser.add_argument('-o', '--output', default='reports', 
                           help='报告输出目录 (默认：reports)')
    run_parser.add_argument('-r', '--reports', default='html,markdown,json',
                           help='报告格式，逗号分隔 (默认：html,markdown,json)')
    run_parser.add_argument('-v', '--verbose', action='store_true',
                           help='显示详细信息')
    run_parser.add_argument('--base-url', help='API 基础 URL（覆盖配置）')
    run_parser.add_argument('-t', '--timeout', type=int, default=None,
                           help='请求超时时间（秒）')
    
    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化项目')
    init_parser.add_argument('-d', '--directory', default='.',
                            help='初始化目录 (默认：当前目录)')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_tests(args)
    elif args.command == 'init':
        init_project(args)
    else:
        parser.print_help()


def run_tests(args):
    """执行测试"""
    print_banner("🚀 API 接口自动化测试")
    
    path = Path(args.path)
    
    # 验证路径存在
    if not path.exists():
        print_error(f"路径不存在：{args.path}")
        sys.exit(1)
    
    # 解析报告格式
    report_formats = [fmt.strip().lower() for fmt in args.reports.split(',')]
    valid_formats = {'html', 'markdown', 'json'}
    report_formats = [f for f in report_formats if f in valid_formats]
    
    if not report_formats:
        print_warning(f"有效的报告格式：{valid_formats}")
        report_formats = ['html']
    
    # 设置输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化测试runner
    runner = TestRunner(base_url=args.base_url)
    
    try:
        # 执行测试
        if path.is_file():
            print_info(f"执行测试文件：{path.absolute()}")
            result = runner.execute_test_file(str(path))
        else:
            print_info(f"执行测试目录：{path.absolute()}")
            result = runner.execute_test_directory(str(path))
        
        # 生成报告
        generator = ReportGenerator(output_dir=str(output_dir))
        reports_generated = {}
        
        if 'json' in report_formats:
            reports_generated['JSON'] = generator.generate_json_report(result)
        
        if 'markdown' in report_formats:
            reports_generated['Markdown'] = generator.generate_markdown_report(result)
        
        if 'html' in report_formats:
            reports_generated['HTML'] = generator.generate_html_report(result)
        
        # 打印结果摘要
        print_summary(result)
        
        # 打印报告路径
        if reports_generated:
            print("\n生成的报告:")
            for format_name, report_path in reports_generated.items():
                try:
                    print(f"   {colored('✓', 'green')} {format_name}: {report_path}")
                except (UnicodeEncodeError, KeyError):
                    print(f"   [OK] {format_name}: {report_path}")
        
        # 退出码
        sys.exit(0 if result.failed_tests == 0 else 1)
        
    except Exception as e:
        print_error(f"执行测试时出错：{e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    finally:
        runner.close()


def print_summary(result):
    """打印测试结果摘要"""
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    pass_rate = result.passed_tests / result.total_tests * 100 if result.total_tests > 0 else 0
    
    # 概览表格
    print(f"\n  {'项目':<20} {'值':>10}")
    print(f"  {'-'*35}")
    print(f"  {'测试套件':<20} {result.suite_name:>10}")
    print(f"  {'总用例数':<20} {str(result.total_tests):>10}")
    
    try:
        passed_str = colored(str(result.passed_tests), 'green')
        failed_str = colored(str(result.failed_tests), 'red')
        rate_color = 'green' if pass_rate >= 80 else ('yellow' if pass_rate >= 50 else 'red')
        rate_str = colored(f'{pass_rate:.1f}%', rate_color)
        
        print(f"  {'通过':<20} {passed_str:>10}")
        print(f"  {'失败':<20} {failed_str:>10}")
        print(f"  {'通过率':<20} {rate_str:>10}")
    except (UnicodeEncodeError, KeyError):
        # 回退到简单文本
        print(f"  {'通过':<20} {str(result.passed_tests):>10}")
        print(f"  {'失败':<20} {str(result.failed_tests):>10}")
        print(f"  {'通过率':<20} {f'{pass_rate:.1f}%':>10}")
    
    print(f"  {'总耗时':<20} {result.total_time:.3f}s>")
    
    # 状态图标
    try:
        status_icon = "✅" if result.failed_tests == 0 else "❌"
        status_text = "测试全部通过！🎉" if result.failed_tests == 0 else f"有 {result.failed_tests} 个测试失败"
        print(f"\n  {status_icon} {status_text}")
    except UnicodeEncodeError:
        status_text = "所有测试通过！" if result.failed_tests == 0 else f"有 {result.failed_tests} 个测试失败"
        print(f"\n  [INFO] {status_text}")
    
    print("=" * 60 + "\n")


def init_project(args):
    """初始化项目"""
    directory = Path(args.directory)
    directory.mkdir(parents=True, exist_ok=True)
    
    from utils import create_environment_template, create_test_case_template
    import yaml
    
    print_banner("📦 初始化 API 测试项目")
    
    # 创建目录结构
    dirs = ['tests', 'configs', 'reports']
    for d in dirs:
        (directory / d).mkdir(exist_ok=True)
        print(f"  {colored('✓', 'green')} 创建目录: {d}/")
    
    # 创建配置文件
    config_file = directory / 'configs' / 'environments.yaml'
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(create_environment_template(), f, indent=2, allow_unicode=True)
    print(f"  {colored('✓', 'green')} 创建配置文件: configs/environments.yaml")
    
    # 创建示例测试用例
    test_file = directory / 'tests' / 'sample_test.yaml'
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(create_test_case_template(), f, indent=2, allow_unicode=True)
    print(f"  {colored('✓', 'green')} 创建示例测试: tests/sample_test.yaml")
    
    # 创建 requirements.txt
    requirements_file = directory / 'requirements.txt'
    with open(requirements_file, 'w', encoding='utf-8') as f:
        f.write("requests>=2.28.0\nPyYAML>=6.0\n")
    print(f"  {colored('✓', 'green')} 创建依赖文件: requirements.txt")
    
    # 创建 README.md
    readme_file = directory / 'README.md'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("""# API 接口自动化测试项目

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
python ../api_test_agent.py run tests/
```

## 目录结构
```
├── configs/          # 配置文件
│   └── environments.yaml  # 环境配置
├── tests/           # 测试用例
│   └── sample_test.yaml   # 示例测试
├── reports/         # 测试报告
└── requirements.txt # 依赖
```

## 更多帮助
```bash
python ../api_test_agent.py --help
```
""")
    print(f"  {colored('✓', 'green')} 创建说明文件: README.md")
    
    print(f"\n{colored('✅ 项目初始化完成!', 'green')}")
    print(f"开始编辑测试用例，然后运行:")
    print(f"  cd {directory}")
    print(f"  python ../api_test_agent.py run tests/")


if __name__ == "__main__":
    main()
