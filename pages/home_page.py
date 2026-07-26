"""首页（主页面）对象：封装登录后的主页面元素与操作

基于实际 ERP 页面结构调整：
- 左侧: <aside class="ant-layout-sider ant-layout-sider-dark sider-layouts">
- 顶部: <div class="comp-top-menu">
- 主布局: <div class="orchid-main-base-layout">
"""
import logging

from playwright.sync_api import Page

from common.base_page import BasePage

logger = logging.getLogger("ui_auto")


class HomePage(BasePage):
    """首页 PO 对象"""

    # ─── 元素定位器（基于实际页面）─────────────────────

    # 左侧边栏菜单
    SIDE_MENU = "aside.ant-layout-sider, .ant-layout-sider, aside"

    # 顶部导航/菜单栏
    HEADER = ".comp-top-menu, .ant-layout-header, header"

    # 页面主体布局容器
    MAIN_LAYOUT = ".orchid-main-base-layout, .ant-layout"

    # 页面内容区域
    CONTENT_AREA = ".ant-layout-content, main, [role='main']"

    # ─── 页面操作方法 ─────────────────────────────────

    def is_page_loaded(self, timeout: int = 15000) -> bool:
        """判断首页是否加载完成"""
        logger.info("等待首页加载...")
        indicators = [
            self.MAIN_LAYOUT,
            self.SIDE_MENU,
            self.HEADER,
        ]
        for selector in indicators:
            if self.is_visible(selector, timeout=5000):
                logger.info(f"首页已加载，检测到元素: {selector}")
                return True
        logger.warning("首页加载标识均未检测到，正在截图...")
        self.take_screenshot("home_page_loaded_check")
        return False

    def is_side_menu_visible(self) -> bool:
        """左侧菜单是否可见"""
        logger.info("检查左侧菜单是否可见")
        return self.is_visible(self.SIDE_MENU, timeout=10000)

    def is_header_visible(self) -> bool:
        """顶部导航栏是否可见"""
        return self.is_visible(self.HEADER, timeout=10000)

    def get_current_page_title(self) -> str:
        """获取当前页面标题"""
        title = self.page.title()
        logger.info(f"当前页面标题: {title}")
        return title
