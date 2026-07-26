"""PO 基类：封装所有页面公用的等待、操作、截图能力"""
import logging
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, expect

ROOT_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = ROOT_DIR / "reports" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("ui_auto")


class BasePage:
    """页面对象基类，所有 Page 类必须继承"""

    def __init__(self, page: Page):
        self.page = page

    # ─── 等待方法 ─────────────────────────────────────

    def wait_for_visible(self, selector: str, timeout: int = 10000) -> None:
        """等待元素可见"""
        logger.info(f"等待元素可见: {selector}")
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)

    def wait_for_clickable(self, selector: str, timeout: int = 10000) -> None:
        """等待元素可点击"""
        logger.info(f"等待元素可点击: {selector}")
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)

    def wait_for_hidden(self, selector: str, timeout: int = 10000) -> None:
        """等待元素隐藏（如 loading 遮罩消失）"""
        logger.info(f"等待元素隐藏: {selector}")
        self.page.wait_for_selector(selector, state="hidden", timeout=timeout)

    def wait_for_network_idle(self, timeout: int = 30000) -> None:
        """等待网络空闲（页面加载完成）"""
        logger.info("等待网络空闲...")
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    # ─── 操作方法 ─────────────────────────────────────

    def click(self, selector: str) -> None:
        """点击元素（含异常捕获 + 自动截图）"""
        try:
            self.wait_for_clickable(selector)
            self.page.click(selector)
            logger.info(f"点击元素成功: {selector}")
        except Exception as e:
            self._take_screenshot(f"click_failed_{self._safe_name(selector)}")
            logger.error(f"点击元素失败: {selector}, 错误: {e}")
            raise

    def fill(self, selector: str, text: str) -> None:
        """输入文本（含异常捕获 + 自动截图）"""
        try:
            self.wait_for_visible(selector)
            self.page.fill(selector, text)
            logger.info(f"输入文本成功: {selector}")
        except Exception as e:
            self._take_screenshot(f"fill_failed_{self._safe_name(selector)}")
            logger.error(f"输入文本失败: {selector}, 错误: {e}")
            raise

    def get_text(self, selector: str) -> str:
        """获取元素文本内容"""
        self.wait_for_visible(selector)
        text = self.page.text_content(selector) or ""
        logger.info(f"获取文本: {selector} = {text}")
        return text.strip()

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """判断元素是否可见"""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def navigate(self, url: str) -> None:
        """跳转到指定 URL 并等待网络空闲"""
        logger.info(f"导航到: {url}")
        self.page.goto(url)
        self.wait_for_network_idle()

    def get_current_url(self) -> str:
        """获取当前页面 URL"""
        return self.page.url

    # ─── 截图方法 ─────────────────────────────────────

    def take_screenshot(self, name: str = "") -> str:
        """手动截图，返回截图文件路径"""
        return self._take_screenshot(name)

    def _take_screenshot(self, name: str = "") -> str:
        """执行截图"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png" if name else f"screenshot_{timestamp}.png"
        filepath = SCREENSHOT_DIR / filename
        self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"截图已保存: {filepath}")
        return str(filepath)

    @staticmethod
    def _safe_name(selector: str) -> str:
        """将 CSS 选择器转换为安全的文件名片段"""
        return selector.replace(" ", "_").replace(">", "_").replace("[", "_").replace("]", "_").replace("=", "_").replace('"', "").replace("'", "")[:50]
