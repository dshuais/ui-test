"""账户管理页面对象

基于 src/pages/system/basic/account-management/ 源码分析生成。
完整覆盖: 两大Tab（往来账户 + 本方账户）、搜索、新增、禁用、启用、删除
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

    # ─── Tab ────────────────────────────────────────

    TAB_CUSTOMER = ".ant-tabs-tab:has-text('往来账户')"
    TAB_SELF = ".ant-tabs-tab:has-text('本方账户')"
    TAB_ACTIVE = ".ant-tabs-tab-active"

    # ─── 搜索区域（往来账户）─────────────────────────

    SEARCH_CUST_NAME = "input[placeholder='请输入往来客户']"
    SEARCH_BANK_NAME = "input[placeholder='请输入开户行名']"
    SEARCH_ACCT_NAME = "input[placeholder='请输入本方户名']"
    SEARCH_STATUS = ".ant-select:has(.ant-select-selection-placeholder:has-text('状态'))"
    SEARCH_STATUS_CUSTOMER = ".ant-form-item:has(.ant-input:placeholder('请输入往来客户')) + .ant-form-item .ant-select"
    BTN_SEARCH = "button:has-text('查 询')"
    BTN_RESET = "button:has-text('重 置')"

    # ─── 表格 ───────────────────────────────────────

    TABLE = ".ant-table, .fe-table-wrapper"
    TABLE_LOADING = ".ant-spin-container.ant-spin-blur"
    TABLE_ROWS = ".ant-table-tbody tr.ant-table-row"
    TABLE_EMPTY = ".ant-empty"

    # ─── 工具栏 ─────────────────────────────────────

    BTN_NEW = "button:has-text('新 建')"

    # ─── 行操作按钮 ─────────────────────────────────

    BTN_DISABLE = "span.fe-link:has-text('禁用')"
    BTN_ENABLE = "span.fe-link:has-text('启用')"
    BTN_DELETE = "span.fe-link:has-text('删除')"

    # ─── 确认弹窗（Modal.confirm）────────────────────

    CONFIRM_MODAL = ".ant-modal-confirm"
    CONFIRM_OK = f"{CONFIRM_MODAL} button.ant-btn-primary, {CONFIRM_MODAL} .ant-btn-primary"

    # ─── 新增/编辑弹窗 ──────────────────────────────

    MODAL = ".ant-modal"
    MODAL_VISIBLE = ".ant-modal:visible, .ant-modal-wrap:not([style*='display: none']) .ant-modal"
    MODAL_CONTENT = ".ant-modal-content"
    MODAL_TITLE = f"{MODAL} .ant-modal-title"
    MODAL_OK_BTN = f"{MODAL} .ant-modal-footer button.ant-btn-primary"
    MODAL_CANCEL_BTN = f"{MODAL} .ant-modal-footer button:not(.ant-btn-primary)"
    MODAL_TEXTAREA_REMARK = f"{MODAL} textarea"

    # ─── 下拉选项 ───────────────────────────────────

    DROPDOWN = ".ant-select-dropdown:not(.ant-select-dropdown-hidden)"
    DROPDOWN_SEARCH_INPUT = f"{DROPDOWN} input"
    DROPDOWN_OPTION = f"{DROPDOWN} .ant-select-item-option:visible"
    DROPDOWN_OPTION_FIRST = f"{DROPDOWN} .ant-select-item-option:visible"

    # ═══════════════════════════════════════════════════
    # 导航
    # ═══════════════════════════════════════════════════

    @allure.step("导航到账户管理")
    def navigate(self, wait_table: bool = True) -> None:
        basic = self.page.locator(self.MENU_BASIC).first
        basic.click()
        self.page.wait_for_timeout(800)
        self.click(self.MENU_ACCOUNT)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)
        if wait_table:
            self.wait_for_table_loaded()

    @allure.step("等待表格加载完成")
    def wait_for_table_loaded(self, timeout: int = 15000) -> None:
        self.wait_for_visible(self.TABLE, timeout=timeout)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1000)

    def is_page_loaded(self) -> bool:
        return self.is_visible(self.TABLE, timeout=10000)

    def is_table_loaded(self) -> bool:
        try:
            self.wait_for_network_idle()
            self.page.wait_for_timeout(1000)
            return self.is_visible(self.TABLE, timeout=8000)
        except Exception:
            return False

    def get_table_row_count(self) -> int:
        try:
            return self.page.locator(self.TABLE_ROWS).count()
        except Exception:
            return 0

    def is_row_visible(self, text: str) -> bool:
        """表格中是否有包含指定文本的行"""
        return self.is_visible(f"{self.TABLE_ROWS}:has-text('{text}')", timeout=5000)

    # ═══════════════════════════════════════════════════
    # Tab 切换
    # ═══════════════════════════════════════════════════

    def _switch_tab(self, tab_selector: str) -> None:
        """切换到指定 Tab"""
        self.click(tab_selector)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1000)
        self.wait_for_table_loaded()

    @allure.step("切换到「往来账户」Tab")
    def switch_to_customer_tab(self) -> None:
        self._switch_tab(self.TAB_CUSTOMER)

    @allure.step("切换到「本方账户」Tab")
    def switch_to_self_tab(self) -> None:
        self._switch_tab(self.TAB_SELF)

    def get_active_tab_text(self) -> str:
        """获取当前激活的 Tab 文本"""
        try:
            return self.page.locator(self.TAB_ACTIVE).inner_text().strip()
        except Exception:
            return ""

    # ═══════════════════════════════════════════════════
    # 搜索（往来账户）
    # ═══════════════════════════════════════════════════

    @allure.step("往来账户搜索 - 按往来客户: {cust_name}")
    def search_customer_by_name(self, cust_name: str) -> None:
        self.fill(self.SEARCH_CUST_NAME, cust_name)
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1500)

    @allure.step("往来账户搜索 - 按开户行名: {bank_name}")
    def search_customer_by_bank(self, bank_name: str) -> None:
        self.fill(self.SEARCH_BANK_NAME, bank_name)
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1500)

    @allure.step("往来账户搜索 - 按状态: {status}")
    def search_customer_by_status(self, status: str) -> None:
        self.click(f"{self.SEARCH_STATUS_CUSTOMER} .ant-select-selector")
        self.page.wait_for_timeout(500)
        option = self.page.locator(f"{self.DROPDOWN_OPTION}:has-text('{status}')").first
        if option.is_visible(timeout=3000):
            option.click()
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1500)

    @allure.step("往来账户搜索 - 清空搜索条件")
    def reset_search_customer(self) -> None:
        self.click(self.BTN_RESET)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1500)

    # ═══════════════════════════════════════════════════
    # 搜索（本方账户）
    # ═══════════════════════════════════════════════════

    @allure.step("本方账户搜索 - 按开户行名: {bank_name}")
    def search_self_by_bank(self, bank_name: str) -> None:
        self.fill(self.SEARCH_BANK_NAME, bank_name)
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1500)

    @allure.step("本方账户搜索 - 按本方户名: {acct_name}")
    def search_self_by_name(self, acct_name: str) -> None:
        self.fill(self.SEARCH_ACCT_NAME, acct_name)
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1500)

    @allure.step("本方账户搜索 - 按状态: {status}")
    def search_self_by_status(self, status: str) -> None:
        selectors = self.page.locator(f"{self.SEARCH_STATUS}")
        count = selectors.count()
        if count > 0:
            selectors.first.click()
            self.page.wait_for_timeout(500)
            option = self.page.locator(f"{self.DROPDOWN_OPTION}:has-text('{status}')").first
            if option.is_visible(timeout=3000):
                option.click()
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1500)

    @allure.step("本方账户搜索 - 清空搜索条件")
    def reset_search_self(self) -> None:
        self.click(self.BTN_RESET)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(1500)

    # ═══════════════════════════════════════════════════
    # 新增账户
    # ═══════════════════════════════════════════════════

    @allure.step("点击新建按钮")
    def click_new(self) -> None:
        self.click(self.BTN_NEW)
        self.wait_for_visible(self.MODAL_VISIBLE, timeout=5000)
        self.page.wait_for_timeout(500)

    def _get_modal_title(self) -> str:
        """获取弹窗标题"""
        try:
            return self.page.locator(self.MODAL_TITLE).inner_text().strip()
        except Exception:
            return ""

    @allure.step("选择客户: {customer_name}")
    def _select_customer(self, customer_name: str = "") -> None:
        """在弹出的新增弹窗中选择往来客户（弹窗内第一个 ant-select）"""
        selects = self.page.locator(f"{self.MODAL_CONTENT} .ant-form .ant-select")
        selects.first.click()
        self.page.wait_for_timeout(500)

        # 等待下拉出现并选择第一个选项
        option = self.page.locator(self.DROPDOWN_OPTION_FIRST).first
        if option.is_visible(timeout=5000):
            option.click()
            self.page.wait_for_timeout(500)
            return

        # 无可见选项 → 尝试搜索
        search_input = self.page.locator(f"{self.DROPDOWN_SEARCH_INPUT}").first
        if search_input.is_visible(timeout=3000):
            keyword = customer_name or "测试"
            search_input.fill(keyword)
            self.page.wait_for_timeout(2000)
            option = self.page.locator(self.DROPDOWN_OPTION_FIRST).first
            if option.is_visible(timeout=5000):
                option.click()
                self.page.wait_for_timeout(500)

    @allure.step("选择银行: {bank_name}")
    def _select_bank(self, bank_name: str = "中国银行") -> None:
        """选择开户行（弹窗中最后一个 ant-select）"""
        selects = self.page.locator(f"{self.MODAL_CONTENT} .ant-form .ant-select")
        count = selects.count()
        idx = count - 1  # 最后一个select就是银行
        selects.nth(idx).click()
        self.page.wait_for_timeout(500)

        # 等待下拉出现并选择第一个选项
        option = self.page.locator(self.DROPDOWN_OPTION_FIRST).first
        if option.is_visible(timeout=5000):
            option.click()
            self.page.wait_for_timeout(500)
            return

        # 搜索银行名
        search_input = self.page.locator(f"{self.DROPDOWN_SEARCH_INPUT}").first
        if search_input.is_visible(timeout=3000):
            search_input.fill(bank_name)
            self.page.wait_for_timeout(2000)
            option = self.page.locator(self.DROPDOWN_OPTION_FIRST).first
            if option.is_visible(timeout=5000):
                option.click()
                self.page.wait_for_timeout(500)

    @allure.step("填写账号: {acct_no}, 户名: {acct_name}, 备注: {remark}")
    def _fill_account_form(self, acct_no: str, acct_name: str, remark: str = "") -> None:
        """填写弹窗中的账号、户名、备注（使用已知字段 id）"""
        # 账号输入框 id=acctNo
        acct_no_input = self.page.locator(f"{self.MODAL_CONTENT} #acctNo")
        if acct_no_input.is_visible(timeout=3000):
            acct_no_input.fill(acct_no)

        # 户名输入框 id=acctName
        acct_name_input = self.page.locator(f"{self.MODAL_CONTENT} #acctName")
        if acct_name_input.is_visible(timeout=3000):
            acct_name_input.fill(acct_name)

        # 备注
        if remark:
            try:
                ta = self.page.locator(self.MODAL_TEXTAREA_REMARK).first
                if ta.is_visible(timeout=2000):
                    ta.fill(remark)
            except Exception:
                pass

    @allure.step("提交表单")
    def _submit_form(self) -> None:
        self.click(self.MODAL_OK_BTN)
        self.page.wait_for_timeout(1000)
        try:
            self.wait_for_hidden(self.MODAL, timeout=15000)
        except Exception:
            # 弹窗未关闭 — 可能是表单校验失败，截图记录后仍抛异常
            self.attach_screenshot("表单提交失败-弹窗未关闭")
            logger.error("表单提交失败：弹窗未关闭，请检查表单校验错误")
            raise
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    @allure.step("新增往来账户: {acct_no} - {acct_name}")
    def add_customer_account(self, acct_no: str, acct_name: str,
                             bank_name: str = "中国银行", remark: str = "自动化测试",
                             customer_name: str = "腾讯") -> None:
        self.click_new()
        self._select_customer(customer_name)
        self._fill_account_form(acct_no, acct_name, remark)
        self._select_bank(bank_name)
        self._submit_form()

    @allure.step("新增本方账户: {acct_no} - {acct_name}")
    def add_self_account(self, acct_no: str, acct_name: str,
                         bank_name: str = "中国银行", remark: str = "自动化测试") -> None:
        self.click_new()
        self._fill_account_form(acct_no, acct_name, remark)
        self._select_bank(bank_name)
        self._submit_form()

    # ═══════════════════════════════════════════════════
    # 行操作（禁用 / 启用 / 删除）
    # ═══════════════════════════════════════════════════

    def _find_row(self, text: str):
        """找到包含指定文本的行"""
        self.wait_for_visible(f"{self.TABLE_ROWS}:has-text('{text}')", timeout=10000)
        self.page.wait_for_timeout(500)
        return self.page.locator(f"{self.TABLE_ROWS}:has-text('{text}')").first

    def _click_row_action(self, row_text: str, button_selector: str) -> None:
        """点击指定行上的操作按钮"""
        row = self._find_row(row_text)
        btn = row.locator(button_selector).first
        btn.scroll_into_view_if_needed()
        btn.click()

    def _confirm_action(self) -> None:
        """点击确认弹窗的确定按钮"""
        self.page.wait_for_timeout(500)
        ok_btn = self.page.locator(self.CONFIRM_OK).first
        if ok_btn.is_visible(timeout=3000):
            ok_btn.click()
            self.wait_for_network_idle()
            self.page.wait_for_timeout(2000)

    @allure.step("禁用账户: {account_name}")
    def disable_account(self, account_name: str) -> None:
        self._click_row_action(account_name, self.BTN_DISABLE)
        self._confirm_action()

    @allure.step("启用账户: {account_name}")
    def enable_account(self, account_name: str) -> None:
        self._click_row_action(account_name, self.BTN_ENABLE)
        self._confirm_action()

    @allure.step("删除账户: {account_name}")
    def delete_account(self, account_name: str) -> None:
        self._click_row_action(account_name, self.BTN_DELETE)
        self._confirm_action()

    # ═══════════════════════════════════════════════════
    # 截图辅助
    # ═══════════════════════════════════════════════════

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
