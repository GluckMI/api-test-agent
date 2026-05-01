@echo off
chcp 65001 >nul
echo ============================================
echo   API Test Agent - GitHub 上传助手
echo ============================================
echo.

REM 检查 Git 是否安装
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git，请先安装 Git: https://git-scm.com/
    pause
    exit /b 1
)

REM 检查是否在正确目录
if not exist "api_test_agent.py" (
    echo [错误] 请在项目根目录下运行此脚本
    echo 当前路径：%CD%
    pause
    exit /b 1
)

echo [步骤 1/7] 初始化 Git 仓库...
git init

echo [步骤 2/7] 添加所有文件到暂存区...
git add .

echo [步骤 3/7] 创建首次提交...
git commit -m "feat: Initial commit - API 接口自动化测试框架 v1.0"

echo.
echo ============================================
echo   下一步操作：
echo ============================================
echo.
echo 1. 在 GitHub 创建新仓库（不要勾选 Add README）
echo 2. 获取仓库 URL（例如：https://github.com/yourusername/api-test-agent.git）
echo 3. 执行以下命令：
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/api-test-agent.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 如果已存在远程仓库，使用命令：
echo    git remote add origin YOUR_REPO_URL
echo    git push -u origin main
echo.
echo 或使用 HTTPS 身份验证（推荐）：
echo    git push -u origin main --set-upstream
echo.
echo ============================================

pause
