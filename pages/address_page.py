"""地址管理页面对象

基于 src/pages/system/basic/address-management/ 分析生成。
- 两个 Tab: 客户地址/企业地址
- 行操作: 编辑、禁用(确认弹窗)、启用(确认弹窗)、删除(确认弹窗，仅禁用态)
- 新增页: 独立路由，含 Map 地图选点
"""
import logging

import allure
from playwright.sync_api import Page

from common.base_page import BasePage
from common.utils import get_config

logger = logging.getLogger("ui_auto")


class AddressPage(BasePage):
    """地址管理 PO 对象"""

    SIDER = "aside.ant-layout-sider"
    MENU_BASIC = f"{SIDER} li:has-text('基础配置')"
    MENU_ADDRESS = f"{SIDER} li.ant-menu-item:has-text('地址管理')"

    # 列表页
    TAB_CUSTOMER = ".ant-tabs-tab:has-text('客户地址')"
    BTN_SEARCH = "button:has-text('查 询')"
    BTN_NEW = "button:has-text('新 建')"
    TABLE = ".ant-table, .fe-table-wrapper"
    TABLE_ROWS = ".ant-table-tbody tr.ant-table-row"

    # 行操作
    BTN_DISABLE = "span.fe-link:has-text('禁用')"
    BTN_ENABLE = "span.fe-link:has-text('启用')"
    BTN_DELETE = "span.fe-link:has-text('删除')"

    # 确认弹窗
    CONFIRM_MODAL = ".ant-modal-confirm"
    CONFIRM_OK = f"{CONFIRM_MODAL} button.ant-btn-primary, {CONFIRM_MODAL} .ant-btn-primary"

    # ─── 导航 ───────────────────────────────────────

    @allure.step("导航到地址管理")
    def navigate(self) -> None:
        basic = self.page.locator(self.MENU_BASIC).first
        basic.click()
        self.page.wait_for_timeout(800)
        self.click(self.MENU_ADDRESS)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    @allure.step("切换到「客户地址」Tab")
    def switch_to_customer_tab(self) -> None:
        self.click(self.TAB_CUSTOMER)
        self.page.wait_for_timeout(500)

    def is_page_loaded(self) -> bool:
        return self.is_visible(self.TABLE, timeout=15000)

    def is_row_visible(self, text: str) -> bool:
        return self.is_visible(f"{self.TABLE_ROWS}:has-text('{text}')", timeout=5000)

    # ─── 新增地址 ───────────────────────────────────

    @allure.step("打开新增页面")
    def go_to_add_page(self) -> None:
        self.click(self.BTN_NEW)
        self.page.wait_for_timeout(3000)
        self.wait_for_network_idle()

    @allure.step("填写地址表单: {address_name}")
    def fill_address_form(self, address_name: str, contact_name: str = "测试联系人", phone: str = "13800138000") -> None:
        # 所属客户 select
        self._pick_labeled_select("所属客户")

        # 地址名称
        self.page.locator("input[placeholder='请输入地址名称']").first.fill(address_name)
        # 联系电话
        self.page.locator("input[placeholder='请输入联系电话']").first.fill(phone)
        # 联系人
        self.page.locator("input[placeholder='请输入联系人']").first.fill(contact_name)
        # 详细地址：点击地图自动选址
        map_canvas = self.page.locator('.amap-layer').first
        if map_canvas.is_visible():
            box = map_canvas.bounding_box()
            if box:
                self.page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                self.page.wait_for_timeout(2000)

    def _pick_labeled_select(self, label_text: str) -> None:
        row = self.page.locator(f".ant-form-item:has(.ant-form-item-label:has-text('{label_text}'))").first
        row.locator('.ant-select-selector').first.click()
        self.page.wait_for_timeout(800)
        option = self.page.locator('.ant-select-item-option:visible').first
        if option.is_visible():
            option.click()
            self.page.wait_for_timeout(500)

    @allure.step("提交地址")
    def submit_address(self) -> None:
        # FeButton 渲染为 button.fe-btn-primary
        self.click("button.fe-btn-primary:has-text('确 认'), button:has-text('确 认')")
        self.page.wait_for_timeout(5000)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    @allure.step("新增地址: {address_name}")
    def add_address(self, address_name: str) -> None:
        self.go_to_add_page()
        self.fill_address_form(address_name=address_name)
        self.submit_address()

    # ─── 行操作 ─────────────────────────────────────

    def _click_row_action(self, row_text: str, button_selector: str) -> None:
        self.wait_for_visible(f"{self.TABLE_ROWS}:has-text('{row_text}')", timeout=10000)
        self.page.wait_for_timeout(500)
        row = self.page.locator(f"{self.TABLE_ROWS}:has-text('{row_text}')").first
        btn = row.locator(button_selector).first
        btn.scroll_into_view_if_needed()
        btn.click()

    def _confirm(self) -> None:
        self.page.wait_for_timeout(500)
        ok_btn = self.page.locator(self.CONFIRM_OK).first
        if ok_btn.is_visible(timeout=3000):
            ok_btn.click()
            self.wait_for_network_idle()
            self.page.wait_for_timeout(1500)

    @allure.step("禁用地址: {address_name}")
    def disable_address(self, address_name: str) -> None:
        self._click_row_action(address_name, self.BTN_DISABLE)
        self._confirm()

    @allure.step("启用地址: {address_name}")
    def enable_address(self, address_name: str) -> None:
        self._click_row_action(address_name, self.BTN_ENABLE)
        self._confirm()

    @allure.step("删除地址: {address_name}")
    def delete_address(self, address_name: str) -> None:
        self._click_row_action(address_name, self.BTN_DELETE)
        self._confirm()

    def attach_screenshot(self, name: str) -> None:
        try:
            allure.attach(
                self.page.screenshot(full_page=True),
                name=name, attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
