"""浏览器引擎模块：封装 Playwright 浏览器启动、上下文管理"""
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from common.utils import get_config

ROOT_DIR = Path(__file__).resolve().parent.parent


class BrowserEngine:
    """Playwright 浏览器引擎，管理浏览器生命周期"""

    def __init__(self):
        self._playwright: Playwright | None = None
        self._config = get_config("browser")

    def start_playwright(self) -> None:
        """
        session 级别：启动 Playwright 实例（全局唯一）
        只调用一次，后续所有测试复用此实例
        """
        self._playwright = sync_playwright().start()

    def new_context(self) -> tuple[Browser, BrowserContext, Page]:
        """
        function 级别：创建独立的 browser + context + page
        每条用例调用一次，保证用例间隔离
        """
        if self._playwright is None:
            raise RuntimeError("Playwright 未初始化，请先调用 start_playwright()")

        headless = self._config.get("headless", False)
        viewport = self._config.get("viewport", {"width": 1920, "height": 1080})
        timeout = self._config.get("timeout", 15000)

        browser = self._playwright.chromium.launch(headless=headless)
        context = browser.new_context(viewport=viewport, locale="zh-CN")
        context.set_default_timeout(timeout)
        page = context.new_page()
        return browser, context, page

    def stop(self) -> None:
        """关闭 Playwright 实例（session 结束时调用）"""
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
