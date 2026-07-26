"""往来客户页面对象

基于 src/pages/system/basic/customers-management/customers-management-list.tsx 分析生成。
qiankun 微前端应用，必须通过侧边栏菜单导航。

页面元素（实测）：
- 搜索: input[placeholder='请输入客户名称'], 查 询, 重 置
- 工具栏: 新 建, 导 出, 批量下载
- 表格: .ant-table / .fe-table-wrapper
"""
import logging

from playwright.sync_api import Page

from common.base_page import BasePage

logger = logging.getLogger("ui_auto")


class CustomersPage(BasePage):
    """往来客户列表页 PO 对象"""

    # ─── 菜单导航选择器 ────────────────────────────

    SIDER = "aside.ant-layout-sider"
    # 基础配置（一级菜单）
    MENU_BASIC_CONFIG = f"{SIDER} li:has-text('基础配置')"
    # 往来客户（二级菜单子项）
    MENU_CUSTOMERS = f"{SIDER} li.ant-menu-item:has-text('往来客户')"

    # ─── 页面元素选择器 ────────────────────────────

    # 搜索输入框
    SEARCH_CUST_NAME = "input[placeholder='请输入客户名称']"
    # 查询按钮
    SEARCH_BUTTON = "button:has-text('查 询')"
    # 重置按钮
    RESET_BUTTON = "button:has-text('重 置')"

    # 工具栏按钮
    BTN_NEW = "button:has-text('新 建')"
    BTN_EXPORT = "button:has-text('导 出')"

    # 表格
    TABLE = ".ant-table, .fe-table-wrapper"
    TABLE_ROWS = ".ant-table-tbody tr.ant-table-row"

    # ─── 页面导航 ───────────────────────────────────

    def navigate(self) -> None:
        """通过侧边栏菜单导航到往来客户列表页"""
        logger.info("通过菜单导航 → 基础配置 → 往来客户")

        # 展开"基础配置"
        basic_config = self.page.locator(self.MENU_BASIC_CONFIG).first
        basic_config.click()
        self.page.wait_for_timeout(800)

        # 点击"往来客户"子菜单
        self.click(self.MENU_CUSTOMERS)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

        logger.info(f"当前 URL: {self.page.url}")

    # ─── 搜索操作 ───────────────────────────────────

    def search_by_name(self, name: str) -> None:
        """按客户名称搜索"""
        logger.info(f"搜索客户: {name}")
        self.fill(self.SEARCH_CUST_NAME, name)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_network_idle()

    def click_new_button(self) -> None:
        """点击新建按钮"""
        logger.info("点击新建按钮")
        self.click(self.BTN_NEW)
        self.wait_for_network_idle()

    # ─── 表格校验 ───────────────────────────────────

    def is_table_loaded(self) -> bool:
        """判断表格是否加载完成"""
        return self.is_visible(self.TABLE, timeout=15000)

    def get_table_row_count(self) -> int:
        """获取表格数据行数"""
        try:
            return self.page.locator(self.TABLE_ROWS).count()
        except Exception:
            return 0

    def is_page_loaded(self) -> bool:
        """判断页面是否加载完成"""
        return self.is_table_loaded()
