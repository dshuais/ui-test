"""账户管理页面对象

基于 src/pages/system/basic/account-management/ 分析生成。
完整覆盖: 页面加载、Tab切换、搜索、新增、禁用、启用、删除
"""
import logging

import allure
from playwright.sync_api import Page

from common.base_page import BasePage

logger = logging.getLogger("ui_auto")


class AccountPage(BasePage):
    """账户管理页 PO 对象"""

    # ─── 菜单导航 ───────────────────────────────────

    SIDER = "aside.ant-layout-sider"
    MENU_BASIC = f"{SIDER} li:has-text('基础配置')"
    MENU_ACCOUNT = f"{SIDER} li.ant-menu-item:has-text('账户管理')"

    # ─── 页面元素 ───────────────────────────────────

    TAB_CUSTOMER = ".ant-tabs-tab:has-text('往来账户')"
    TAB_SELF = ".ant-tabs-tab:has-text('本方账户')"

    SEARCH_CUST_NAME = "input[placeholder='请输入往来客户']"
    BTN_SEARCH = "button:has-text('查 询')"
    BTN_NEW = "button:has-text('新 建')"

    TABLE = ".ant-table, .fe-table-wrapper"
    TABLE_ROWS = ".ant-table-tbody tr.ant-table-row"

    # 行操作按钮（fe-components 渲染为 span.fe-link，不是 button）
    BTN_DISABLE = "span.fe-link:has-text('禁用')"
    BTN_ENABLE = "span.fe-link:has-text('启用')"
    BTN_DELETE = "span.fe-link:has-text('删除')"

    # 确认弹窗（Ant Design Modal.confirm）
    CONFIRM_MODAL = ".ant-modal-confirm"
    CONFIRM_OK = f"{CONFIRM_MODAL} button.ant-btn-primary, {CONFIRM_MODAL} .ant-btn-primary"

    # ─── 新增弹窗 ───────────────────────────────────

    MODAL = ".ant-modal"
    MODAL_VISIBLE = ".ant-modal:visible, .ant-modal-wrap:not([style*='display: none']) .ant-modal"
    MODAL_OK_BTN = f"{MODAL} .ant-modal-footer button.ant-btn-primary"
    MODAL_TEXTAREA_REMARK = f"{MODAL} textarea"

    # ─── 导航 ───────────────────────────────────────

    @allure.step("导航到账户管理")
    def navigate(self) -> None:
        basic = self.page.locator(self.MENU_BASIC).first
        basic.click()
        self.page.wait_for_timeout(800)
        self.click(self.MENU_ACCOUNT)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    def is_page_loaded(self) -> bool:
        return self.is_visible(self.TABLE, timeout=15000)

    def get_table_row_count(self) -> int:
        try:
            return self.page.locator(self.TABLE_ROWS).count()
        except Exception:
            return 0

    # ─── Tab 切换 ───────────────────────────────────

    @allure.step("切换到「往来账户」Tab")
    def switch_to_customer_tab(self) -> None:
        self.click(self.TAB_CUSTOMER)
        self.page.wait_for_timeout(500)

    @allure.step("切换到「本方账户」Tab")
    def switch_to_self_tab(self) -> None:
        self.click(self.TAB_SELF)
        self.page.wait_for_timeout(500)

    # ─── 搜索 ───────────────────────────────────────

    @allure.step("搜索: {name}")
    def search_by_cust_name(self, name: str) -> None:
        self.fill(self.SEARCH_CUST_NAME, name)
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    # ─── 新增账户 ───────────────────────────────────

    def click_new(self) -> None:
        self.click(self.BTN_NEW)
        self.wait_for_visible(self.MODAL_VISIBLE, timeout=5000)

    def fill_account_form(self, acct_no: str, acct_name: str, remark: str = "") -> None:
        # 账号
        acct_inputs = self.page.locator(f"{self.MODAL} .ant-modal-body input:visible:not([disabled])")
        if acct_inputs.count() >= 1:
            for i in range(min(acct_inputs.count(), 3)):
                inp = acct_inputs.nth(i)
                pid = inp.get_attribute('id') or ''
                if 'acctNo' in pid or 'acct' in pid.lower():
                    inp.fill(acct_no)
                    break
            else:
                if acct_inputs.count() >= 2:
                    acct_inputs.nth(1).fill(acct_no)

        # 户名
        name_inputs = self.page.locator(f"{self.MODAL} .ant-modal-body input:visible:not([disabled])")
        for i in range(min(name_inputs.count(), 5)):
            inp = name_inputs.nth(i)
            pid = inp.get_attribute('id') or ''
            ph = inp.get_attribute('placeholder') or ''
            if 'acctName' in pid or '户名' in ph:
                inp.fill(acct_name)
                break
        else:
            if name_inputs.count() >= 3:
                name_inputs.nth(2).fill(acct_name)

        # 备注
        if remark:
            try:
                ta = self.page.locator(self.MODAL_TEXTAREA_REMARK).first
                if ta.is_visible():
                    ta.fill(remark)
            except Exception:
                pass

    def select_bank(self, bank_name: str = "中国银行") -> None:
        bank_select = self.page.locator(f"{self.MODAL} .ant-select:has(.ant-select-selection-search)").last
        bank_select.click()
        self.page.wait_for_timeout(500)
        search_input = self.page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) input").first
        if search_input.is_visible():
            search_input.fill(bank_name)
            self.page.wait_for_timeout(1000)
        option = self.page.locator(".ant-select-item-option:visible").first
        if option.is_visible():
            option.click()
        self.page.wait_for_timeout(500)

    def select_customer(self, customer_name: str = "腾讯") -> None:
        cust_select = self.page.locator(f"{self.MODAL} .ant-select:has(.ant-select-selection-search)").first
        cust_select.click()
        self.page.wait_for_timeout(500)
        search_input = self.page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) input").first
        if search_input.is_visible():
            search_input.fill(customer_name)
            self.page.wait_for_timeout(1500)
        option = self.page.locator(".ant-select-item-option:visible").first
        if option.is_visible():
            option.click()
        self.page.wait_for_timeout(500)

    def submit_form(self) -> None:
        self.click(self.MODAL_OK_BTN)
        self.wait_for_hidden(self.MODAL, timeout=10000)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    @allure.step("新增账户: {acct_name}")
    def add_account(self, acct_no, acct_name, bank_name="中国银行", remark="自动化测试", customer_name="腾讯", is_self=False):
        self.click_new()
        if not is_self:
            self.select_customer(customer_name)
        self.fill_account_form(acct_no=acct_no, acct_name=acct_name, remark=remark)
        self.select_bank(bank_name)
        self.submit_form()

    # ─── 行操作 ─────────────────────────────────────

    def _click_row_action(self, row_text: str, button_selector: str) -> None:
        """点击指定行上的操作按钮"""
        # 先等待表格行出现
        self.wait_for_visible(f"{self.TABLE_ROWS}:has-text('{row_text}')", timeout=10000)
        self.page.wait_for_timeout(500)
        row = self.page.locator(f"{self.TABLE_ROWS}:has-text('{row_text}')").first
        btn = row.locator(button_selector).first
        btn.scroll_into_view_if_needed()
        btn.click()

    def _confirm(self) -> None:
        """点击确认弹窗的确定按钮"""
        self.page.wait_for_timeout(500)
        ok_btn = self.page.locator(self.CONFIRM_OK).first
        if ok_btn.is_visible(timeout=3000):
            ok_btn.click()
            self.wait_for_network_idle()
            self.page.wait_for_timeout(1500)

    @allure.step("禁用账户: {account_name}")
    def disable_account(self, account_name: str) -> None:
        self._click_row_action(account_name, self.BTN_DISABLE)
        self._confirm()

    @allure.step("启用账户: {account_name}")
    def enable_account(self, account_name: str) -> None:
        self._click_row_action(account_name, self.BTN_ENABLE)
        self._confirm()

    @allure.step("删除账户: {account_name}")
    def delete_account(self, account_name: str) -> None:
        self._click_row_action(account_name, self.BTN_DELETE)
        self._confirm()

    def is_row_visible(self, text: str) -> bool:
        """表格中是否有包含指定文本的行"""
        return self.is_visible(f"{self.TABLE_ROWS}:has-text('{text}')", timeout=5000)

    def get_first_row_text(self) -> str:
        """获取第一行数据的文本（用于操作定位）"""
        try:
            return self.page.locator(self.TABLE_ROWS).first.inner_text()
        except Exception:
            return ""

    # ─── 截图辅助 ───────────────────────────────────

    def attach_screenshot(self, name: str) -> None:
        """截图并附加到 allure 报告"""
        try:
            allure.attach(
                self.page.screenshot(full_page=True),
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
