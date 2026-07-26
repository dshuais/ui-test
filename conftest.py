"""Pytest 全局夹具：浏览器生命周期管理、失败自动截图"""
import logging

import allure
import pytest

from common.browser_engine import BrowserEngine
from common.logger import setup_logger
from common.utils import get_config

# 初始化日志
setup_logger()
logger = logging.getLogger("ui_auto")


@pytest.fixture(scope="session")
def browser_engine():
    """
    session 级别：只启动一次 Playwright 实例
    所有用例共用同一个 BrowserEngine 实例
    """
    engine = BrowserEngine()
    engine.start_playwright()
    logger.info("===== Playwright 引擎已启动 =====")
    yield engine
    engine.stop()
    logger.info("===== Playwright 引擎已关闭 =====")


@pytest.fixture(scope="function")
def page(browser_engine: BrowserEngine):
    """
    function 级别：每条用例独立的 browser + context + page
    用例之间隔离，互不污染（cookie / localStorage / sessionStorage 独立）
    """
    browser, context, page = browser_engine.new_context()

    # 注入 localStorage 配置（微前端 debug 模式）
    # 使得本地 base 项目能正确映射
    try:
        page.goto(get_config("base_url"), wait_until="domcontentloaded")
        page.evaluate("() => { localStorage.setItem('debug_micro_apps', 'web-erp'); }")
        logger.info("已设置 localStorage: debug_micro_apps=web-erp")
    except Exception as e:
        logger.warning(f"设置 localStorage 失败（非关键）: {e}")

    yield page

    # 用例结束后清理
    context.close()
    logger.info("===== 用例上下文已关闭 =====")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    每个用例执行结束后自动截图并附加到 Allure 报告
    - 通过用例：截图作为 PASSED_xxx 保存
    - 失败用例：截图作为 FAILED_xxx 保存
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        page = item.funcargs.get("page", None)
        if page:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_func_name = item.name  # pytest 函数名：test_xxx
            prefix = "FAILED" if report.failed else "PASSED"
            screenshot_name = f"{prefix}_{test_func_name}_{timestamp}"

            # 记录函数名到 allure，便于报告匹配截图
            allure.dynamic.label("testMethod", test_func_name)
            screenshot_path = (
                __import__("pathlib").Path(__file__).resolve().parent
                / "reports"
                / "screenshots"
                / f"{screenshot_name}.png"
            )
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                if report.failed:
                    logger.error(f"用例失败，截图已保存: {screenshot_path}")
                else:
                    logger.info(f"用例通过，截图已保存: {screenshot_path}")

                # 附加到 allure
                allure.attach(
                    page.screenshot(full_page=True),
                    name=screenshot_name,
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                logger.warning(f"截图失败（非致命）: {e}")
