"""账户管理页面对象

基于 src/pages/system/basic/account-management/ 分析生成。
- 两个 Tab: 往来账户(EAccountType=1) / 本方账户(EAccountType=2)
- 工具栏: 新建
- 新建弹窗: AccountOperateModal > AccountForm (往来客户/账号/户名/开户行/行号/备注)

往来账户表单: 往来客户(select)、往来账号(input)、往来户名(input)、开户行名(select)、开户行号(input disabled)、账户备注(textarea)
本方账户表单: 本方账号(input)、本方户名(input)、开户行名(select)、开户行号(input disabled)、账户备注(textarea)
"""
import logging

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

    # Tab
    TAB_CUSTOMER = ".ant-tabs-tab:has-text('往来账户')"
    TAB_SELF = ".ant-tabs-tab:has-text('本方账户')"

    # 搜索表单（往来账户 tab）
    SEARCH_CUST_NAME = "input[placeholder='请输入往来客户']"
    SEARCH_BANK_NAME = "input[placeholder*='开户行名']"

    # 按钮
    BTN_SEARCH = "button:has-text('查 询')"
    BTN_NEW = "button:has-text('新 建')"

    # 表格
    TABLE = ".ant-table, .fe-table-wrapper"
    TABLE_ROWS = ".ant-table-tbody tr.ant-table-row"

    # 页面标题
    PAGE_TITLE = "text=账户管理"

    # ─── 新增弹窗选择器 ─────────────────────────────

    MODAL = ".ant-modal"
    MODAL_VISIBLE = ".ant-modal:visible, .ant-modal-wrap:not([style*='display: none']) .ant-modal"
    MODAL_TITLE = ".ant-modal-title"
    # 弹窗内表单字段（通过 label 定位）
    MODAL_INPUT_ACCT_NO = f"{MODAL} input[id*='acctNo' i], {MODAL} .ant-form-item:has(.ant-form-item-label:has-text('账号')) input"
    MODAL_INPUT_ACCT_NAME = f"{MODAL} input[id*='acctName' i], {MODAL} .ant-form-item:has(.ant-form-item-label:has-text('户名')) input"
    MODAL_TEXTAREA_REMARK = f"{MODAL} textarea"
    # 弹窗确认按钮
    MODAL_OK_BTN = f"{MODAL} .ant-modal-footer button.ant-btn-primary"

    def navigate(self) -> None:
        """通过侧边栏菜单导航到账户管理"""
        logger.info("通过菜单导航 → 基础配置 → 账户管理")

        basic = self.page.locator(self.MENU_BASIC).first
        basic.click()
        self.page.wait_for_timeout(800)

        self.click(self.MENU_ACCOUNT)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

        logger.info(f"当前 URL: {self.page.url}")

    def is_page_loaded(self) -> bool:
        return self.is_visible(self.TABLE, timeout=15000)

    def get_table_row_count(self) -> int:
        try:
            return self.page.locator(self.TABLE_ROWS).count()
        except Exception:
            return 0

    # ─── Tab 切换 ───────────────────────────────────

    def switch_to_customer_tab(self) -> None:
        """切换到往来账户 tab"""
        self.click(self.TAB_CUSTOMER)
        self.page.wait_for_timeout(500)

    def switch_to_self_tab(self) -> None:
        """切换到本方账户 tab"""
        self.click(self.TAB_SELF)
        self.page.wait_for_timeout(500)

    # ─── 搜索 ───────────────────────────────────────

    def search_by_cust_name(self, name: str) -> None:
        """按往来客户名称搜索"""
        logger.info(f"搜索往来客户: {name}")
        self.fill(self.SEARCH_CUST_NAME, name)
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()

    # ─── 新增账户 ───────────────────────────────────

    def click_new(self) -> None:
        """点击新建按钮，打开新增弹窗"""
        logger.info("点击新建按钮")
        self.click(self.BTN_NEW)
        # 等待弹窗出现
        self.wait_for_visible(self.MODAL_VISIBLE, timeout=5000)
        logger.info("新增弹窗已打开")

    def fill_account_form(
        self,
        acct_no: str,
        acct_name: str,
        remark: str = "",
    ) -> None:
        """填写账户表单（通用：往来/本方）- 开户行需要手动在下拉框中选择

        Args:
            acct_no: 账号
            acct_name: 户名
            remark: 备注（可选）
        """
        logger.info(f"填写账户表单: 账号={acct_no}, 户名={acct_name}")

        # 账号 - 弹窗内第一个可见的 input（排除 disabled 的）
        acct_inputs = self.page.locator(f"{self.MODAL} .ant-modal-body input:visible:not([disabled])")
        if acct_inputs.count() >= 1:
            # 第一个非 disabled input 通常是往来客户选择框或账号
            # 需要跳过 select 的搜索框
            for i in range(min(acct_inputs.count(), 3)):
                inp = acct_inputs.nth(i)
                pid = inp.get_attribute('id') or ''
                if 'acctNo' in pid or 'acct' in pid.lower():
                    inp.fill(acct_no)
                    logger.info(f"账号已填入 input#{i}")
                    break
            else:
                # 没找到 id 匹配的，填第二个可见 input（第一个通常是客户选择框的搜索）
                if acct_inputs.count() >= 2:
                    acct_inputs.nth(1).fill(acct_no)
                    logger.info("账号已填入 input#1（fallback）")

        # 户名
        name_inputs = self.page.locator(f"{self.MODAL} .ant-modal-body input:visible:not([disabled])")
        for i in range(min(name_inputs.count(), 5)):
            inp = name_inputs.nth(i)
            pid = inp.get_attribute('id') or ''
            ph = inp.get_attribute('placeholder') or ''
            if 'acctName' in pid or '户名' in ph:
                inp.fill(acct_name)
                logger.info(f"户名已填入")
                break
        else:
            # fallback
            if name_inputs.count() >= 3:
                name_inputs.nth(2).fill(acct_name)

        # 备注
        if remark:
            try:
                ta = self.page.locator(self.MODAL_TEXTAREA_REMARK).first
                if ta.is_visible():
                    ta.fill(remark)
                    logger.info(f"备注已填入: {remark}")
            except Exception:
                pass

    def select_bank(self, bank_name: str = "中国银行") -> None:
        """在弹窗中选择开户行名"""
        logger.info(f"选择开户行: {bank_name}")

        # 找到开户行 select 并展开
        bank_select = self.page.locator(f"{self.MODAL} .ant-select:has(.ant-select-selection-search)").last
        bank_select.click()
        self.page.wait_for_timeout(500)

        # 在 dropdown 中搜索并选中
        search_input = self.page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) input").first
        if search_input.is_visible():
            search_input.fill(bank_name)
            self.page.wait_for_timeout(1000)

        # 点击第一个匹配项
        option = self.page.locator(".ant-select-item-option:visible").first
        if option.is_visible():
            option.click()
            logger.info(f"已选择开户行: {bank_name}")
        self.page.wait_for_timeout(500)

    def select_customer(self, customer_name: str = "腾讯") -> None:
        """在弹窗中选择往来客户（仅往来账户）"""
        logger.info(f"选择往来客户: {customer_name}")

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
            logger.info(f"已选择客户")
        self.page.wait_for_timeout(500)

    def submit_form(self) -> None:
        """点击弹窗确定按钮提交表单"""
        logger.info("提交账户表单")
        self.click(self.MODAL_OK_BTN)
        # 等待弹窗关闭
        self.wait_for_hidden(self.MODAL, timeout=10000)
        self.wait_for_network_idle()
        logger.info("账户表单已提交，弹窗已关闭")

    def add_account(
        self,
        acct_no: str,
        acct_name: str,
        bank_name: str = "中国银行",
        remark: str = "自动化测试",
        customer_name: str = "腾讯",
        is_self: bool = False,
    ) -> None:
        """完整新增账户流程

        Args:
            acct_no: 账号
            acct_name: 户名
            bank_name: 开户行名
            remark: 备注
            customer_name: 往来客户（仅往来账户）
            is_self: 是否本方账户
        """
        self.click_new()

        if not is_self:
            self.select_customer(customer_name)

        self.fill_account_form(acct_no=acct_no, acct_name=acct_name, remark=remark)
        self.select_bank(bank_name)
        self.submit_form()

    def is_row_with_text(self, text: str) -> bool:
        """表格中是否包含指定文本的行"""
        return self.is_visible(f"{self.TABLE_ROWS}:has-text('{text}')", timeout=5000)
