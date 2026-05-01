"""
API 接口自动化测试 Agent - 命令行接口
"""
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .config import Config, config
from .runner import TestRunner, TestSuiteResult
from .reports import ReportGenerator
from .utils import (
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

    # 新增参数：环境配置
    run_parser.add_argument('-e', '--env', type=str, default=None,
                           help='指定环境名称 (如 dev, staging, prod)')
    run_parser.add_argument('--var', action='append', default=[],
                           metavar='KEY=VALUE',
                           help='变量覆盖，支持多次使用 (如 --var timeout=60)')
    run_parser.add_argument('-w', '--workers', type=int, default=1,
                           help='并发工作线程数 (默认：1，即串行执行)')
    run_parser.add_argument('--show-config', action='store_true',
                           help='显示当前生效的配置信息')

    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化项目')
    init_parser.add_argument('-d', '--directory', default='.',
                            help='初始化目录 (默认：当前目录)')

    # env 子命令
    env_parser = subparsers.add_parser('env', help='环境管理')
    env_subparsers = env_parser.add_subparsers(dest='env_command', help='环境操作')

    # env list 命令
    env_list_parser = env_subparsers.add_parser('list', help='列出所有可用环境')

    # env validate 命令
    env_validate_parser = env_subparsers.add_parser('validate', help='验证环境配置')
    env_validate_parser.add_argument('environment', help='要验证的环境名称')

    # env show 命令
    env_show_parser = env_subparsers.add_parser('show', help='显示环境配置详情')
    env_show_parser.add_argument('environment', help='要查看的环境名称')
    env_show_parser.add_argument('--no-sanitize', action='store_true',
                                help='显示完整配置（不脱敏敏感信息）')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_tests(args)
    elif args.command == 'init':
        init_project(args)
    elif args.command == 'env':
        handle_env_command(args)
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

    # 解析 --var 参数为字典
    var_overrides = {}
    for var_item in args.var:
        if '=' in var_item:
            key, value = var_item.split('=', 1)
            var_overrides[key.strip()] = value.strip()
        else:
            print_warning(f"忽略无效的变量参数: {var_item} (格式应为 KEY=VALUE)")

    # 初始化配置（支持环境模式）
    test_config = Config(environment=args.env)

    # 应用变量覆盖
    if var_overrides and test_config.environment_manager:
        test_config.environment_manager.apply_overrides(var_overrides)
        print(f"✓ 已应用 {len(var_overrides)} 个变量覆盖")

    # 显示配置信息（如果请求）
    if args.show_config:
        _show_current_config(test_config, args.env)

    # 初始化测试runner
    base_url = args.base_url or test_config.get("base_url")
    runner = TestRunner(base_url=base_url)
    
    try:
        # 执行测试
        if path.is_file():
            print_info(f"执行测试文件：{path.absolute()}")
            result = runner.execute_test_file(str(path))
        else:
            print_info(f"执行测试目录：{path.absolute()}")

            if args.workers > 1:
                # 并发模式
                result = _run_concurrent_tests(runner, str(path), args.workers)
            else:
                # 串行模式（默认）
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
    
    from .utils import create_environment_template, create_test_case_template
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


def _show_current_config(config: Config, env_name: str = None):
    """显示当前配置信息

    Args:
        config: Config 实例
        env_name: 环境名称（如果有）
    """
    print("\n" + "=" * 60)
    print("当前配置信息")
    print("=" * 60)

    if env_name:
        print(f"\n  环境: {colored(env_name, 'cyan')}")

    # 显示基础配置
    print(f"\n  {'配置项':<25} {'值':<30}")
    print(f"  {'-' * 55}")
    print(f"  {'base_url':<25} {config.get('base_url', '(未设置)'):<30}")
    print(f"  {'timeout':<25} {str(config.get('timeout', 30)) + 's':<30}")
    print(f"  {'log_level':<25} {config.get('log_level', 'INFO'):<30}")

    # 显示环境变量（如果有）
    env_vars = config.get_environment_variables()
    if env_vars:
        print(f"\n  环境变量:")
        for key, value in env_vars.items():
            print(f"    {key}: {value}")

    # 显示环境完整配置（如果可用）
    if config.environment_manager:
        full_env_config = config.get_environment_config()
        if full_env_config and isinstance(full_env_config, dict):
            print(f"\n  完整环境配置 (已脱敏):")
            import json
            print(f"  {json.dumps(full_env_config, indent=4, ensure_ascii=False)}")

    print("=" * 60 + "\n")


def _run_concurrent_tests(runner: TestRunner, directory: str, workers: int) -> TestSuiteResult:
    """并发执行目录下的所有测试

    Args:
        runner: TestRunner 实例
        directory: 测试目录路径
        workers: 并发工作线程数

    Returns:
        TestSuiteResult 测试结果
    """
    try:
        from .concurrent import ConcurrentTestRunner
        from .runner import TestSuiteResult
    except ImportError as e:
        print_warning(f"并发模块不可用，回退到串行模式: {e}")
        return runner.execute_test_directory(directory)

    print_info(f"启用并发模式 (workers={workers})")

    # 加载所有测试用例
    test_cases = runner.load_test_suite(directory)

    if not test_cases:
        print_warning("没有找到测试用例")
        return TestSuiteResult(
            suite_name=f"All Tests in {directory}",
            start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            total_time=0.0,
            test_results=[]
        )

    # 使用并发执行器
    concurrent_runner = ConcurrentTestRunner(runner, max_workers=workers)
    concurrency_result = concurrent_runner.run_concurrent(test_cases)

    # 转换为 TestSuiteResult 格式（保持兼容性）
    result = TestSuiteResult(
        suite_name=f"All Tests in {directory}",
        start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_tests=concurrency_result.total_tests,
        passed_tests=concurrency_result.passed,
        failed_tests=concurrency_result.failed,
        total_time=concurrency_result.parallel_time,
        test_results=concurrency_result.results
    )

    # 显示并发统计
    print(f"\n  并发执行统计:")
    print(f"    总用例数: {concurrency_result.total_tests}")
    print(f"    通过: {concurrency_result.passed}, 失败: {concurrency_result.failed}")
    print(f"    并行耗时: {concurrency_result.parallel_time:.3f}s")
    print(f"    加速比: {concurrency_result.speedup}x")
    print(f"    工作线程: {concurrency_result.worker_count}")

    return result


def handle_env_command(args):
    """处理 env 子命令

    Args:
        args: 命令行参数
    """
    try:
        from .environment import EnvironmentManager
    except ImportError:
        print_error("environment 模块不可用")
        sys.exit(1)

    try:
        manager = EnvironmentManager()

        if args.env_command == 'list':
            env_list = manager.list_environments()
            print("\n可用的环境列表:")
            if env_list:
                for env_name in env_list:
                    print(f"  - {env_name}")
            else:
                print("  (无)")
            print()

        elif args.env_command == 'validate':
            errors = manager.validate_environment(args.environment)
            if errors:
                print_error(f"环境 '{args.environment}' 验证失败:")
                for error in errors:
                    print(f"  ✗ {error}")
                sys.exit(1)
            else:
                print_success(f"环境 '{args.environment}' 配置验证通过 ✓")

        elif args.env_command == 'show':
            try:
                config = manager.load_environment(args.environment)
                config_dict = manager.show_config(sanitize=not getattr(args, 'no_sanitize', False))

                import json
                print(f"\n环境 '{args.environment}' 配置详情:")
                print(json.dumps(config_dict, indent=2, ensure_ascii=False))
                print()
            except ValueError as e:
                print_error(str(e))
                sys.exit(1)

        else:
            print("请指定 env 子命令: list, validate, show")
            sys.exit(1)

    except FileNotFoundError as e:
        print_error(str(e))
        sys.exit(1)
