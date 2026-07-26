@echo off
REM ===================================================
REM UI 自动化测试一键执行脚本 (Windows)
REM 功能：执行用例 → 生成 Allure 原始数据 → 构建 HTML 报告
REM ===================================================

cd /d "%~dp0"

echo ========================================
echo   UI 自动化测试开始执行
echo ========================================

REM 1. 执行 pytest 用例，生成 allure 原始数据
echo [1/3] 执行测试用例...
pytest cases/ --alluredir=reports/allure_raw
if %errorlevel% neq 0 (
    echo 部分用例失败（非致命），继续生成报告...
)

REM 2. 根据原始数据生成静态 HTML 报告
echo [2/3] 生成 Allure HTML 报告...
allure generate reports/allure_raw -o reports/allure_html --clean

REM 3. 打开 Allure 报告
echo [3/3] 打开 Allure 报告...
allure open reports/allure_html

echo ========================================
echo   执行完毕
echo ========================================
pause
