#!/bin/bash
# ===================================================
# UI 自动化测试一键执行脚本 (macOS / Linux)
# 功能：执行用例 → 生成 Allure 原始数据 → 构建 HTML 报告
# ===================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  UI 自动化测试开始执行"
echo "========================================"

# 1. 执行 pytest 用例，生成 allure 原始数据
echo "[1/3] 执行测试用例..."
pytest cases/ --alluredir=reports/allure_raw || echo "部分用例失败（非致命），继续生成报告..."

# 2. 根据原始数据生成静态 HTML 报告
echo "[2/3] 生成 Allure HTML 报告..."
allure generate reports/allure_raw -o reports/allure_html --clean

# 3. 打开 Allure 报告
echo "[3/3] 打开 Allure 报告..."
allure open reports/allure_html

echo "========================================"
echo "  执行完毕"
echo "========================================"
