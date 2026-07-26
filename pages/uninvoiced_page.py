"""待开票列表页面对象

基于 src/pages/invoicing/uninvoiced/uninvoiced-list.tsx 分析生成。
qiankun 微前端，通过侧边栏「开票管理 → 待开票列表」导航。

搜索表单: 业务来源、收货时间、车牌号、销售方、待开票金额(min/max)、商品品类、商品名称、创建时间
工具栏: 全部选中、刷新、开票
表格: 业务来源、业务单号、收货时间、车牌号、销售方、采购方、商品品类、商品名称、计量单位、已开票金额、待开票金额、创建时间
"""
import logging

from playwright.sync_api import Page

from common.base_page import BasePage

logger = logging.getLogger("ui_auto")


class UninvoicedPage(BasePage):
    """待开票列表页 PO 对象"""

    # ─── 菜单导航 ───────────────────────────────────

    SIDER = "aside.ant-layout-sider"
    MENU_INVOICING = f"{SIDER} li:has-text('开票管理')"
    MENU_UNINVOICED = f"{SIDER} li.ant-menu-item:has-text('待开票列表')"

    # ─── 页面元素 ───────────────────────────────────

    # 搜索表单（基于 FeForm items 分析）
    SEARCH_BIZ_SOURCE = "[data-index='invoiceBizSourceType']"
    SEARCH_PLATE_NO = "input[placeholder*='车牌']"
    SEARCH_SKU_NAME = "input[placeholder*='商品名称']"

    # 按钮（注意 Ant Design 按钮文本中的空格）
    BTN_SEARCH = "button:has-text('查 询')"
    BTN_RESET = "button:has-text('重 置')"
    BTN_SELECT_ALL = "button:has-text('全部选中')"
    BTN_REFRESH = "button:has-text('刷 新'), button:has-text('刷新')"
    BTN_INVOICE = "button:has-text('开 票'), button:has-text('开票')"

    # 表格
    TABLE = ".ant-table, .fe-table-wrapper"
    TABLE_ROWS = ".ant-table-tbody tr.ant-table-row"

    # 分页
    PAGINATION = ".ant-pagination"

    # 页面标题标识
    PAGE_TITLE_SELECTOR = "text=待开票列表"

    def navigate(self) -> None:
        """通过侧边栏菜单导航到待开票列表"""
        logger.info("通过菜单导航 → 开票管理 → 待开票列表")

        # 展开"开票管理"
        invoicing_menu = self.page.locator(self.MENU_INVOICING).first
        invoicing_menu.click()
        self.page.wait_for_timeout(800)

        # 点击"待开票列表"
        self.click(self.MENU_UNINVOICED)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

        logger.info(f"当前 URL: {self.page.url}")

    def is_page_loaded(self) -> bool:
        """判断页面是否加载完成"""
        return self.is_visible(self.PAGE_TITLE_SELECTOR, timeout=5000) or self.is_visible(self.TABLE, timeout=15000)

    def is_table_loaded(self) -> bool:
        """判断表格是否加载"""
        return self.is_visible(self.TABLE, timeout=15000)

    def get_table_row_count(self) -> int:
        """获取表格数据行数"""
        try:
            return self.page.locator(self.TABLE_ROWS).count()
        except Exception:
            return 0

    def search_by_plate_no(self, plate_no: str) -> None:
        """按车牌号搜索"""
        logger.info(f"搜索车牌号: {plate_no}")
        self.fill(self.SEARCH_PLATE_NO, plate_no)
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()

    def click_select_all(self) -> None:
        """点击全部选中按钮"""
        logger.info("点击全部选中")
        self.click(self.BTN_SELECT_ALL)
        self.wait_for_network_idle()

    def click_refresh(self) -> None:
        """点击刷新按钮"""
        logger.info("点击刷新")
        self.click(self.BTN_REFRESH)
        self.wait_for_network_idle()
