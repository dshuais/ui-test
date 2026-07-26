"""登录页面对象：封装登录页元素定位与操作"""
import logging

from playwright.sync_api import Page

from common.base_page import BasePage
from common.utils import get_account, get_config

logger = logging.getLogger("ui_auto")


class LoginPage(BasePage):
    """登录页面 PO 对象"""

    # ─── 元素定位器（登录表单）─────────────────────────
    # 用户名输入框 placeholder="请输入手机号"
    USERNAME_INPUT = "input[placeholder*='手机']"
    # 密码输入框
    PASSWORD_INPUT = "input[type='password']"
    # 登录按钮 text="登 录"（注意空格）
    LOGIN_BUTTON = "button:has-text('登 录')"

    # 登录页面唯一标识（用于判断是否在登录页）
    LOGIN_PAGE_INDICATOR = "input[type='password']"

    # ─── 元素定位器（选择企业弹窗）─────────────────────
    # 企业选择 Modal body
    ENTERPRISE_MODAL = ".ant-modal-body"
    # 企业卡片（inline style cursor:pointer）
    ENTERPRISE_CARD = "[style*='cursor: pointer']"
    # 确认按钮（如果有的话）
    ENTERPRISE_CONFIRM_BTN = ".ant-modal-footer button"

    # ─── 页面操作方法 ─────────────────────────────────

    def goto(self) -> None:
        """访问登录页面"""
        base_url = get_config("base_url")
        logger.info(f"访问登录页面: {base_url}")
        self.page.goto(base_url)
        self.wait_for_network_idle()

    def is_on_login_page(self) -> bool:
        """判断当前是否在登录页面"""
        return self.is_visible(self.LOGIN_PAGE_INDICATOR, timeout=5000)

    def fill_username(self, username: str) -> None:
        """输入用户名"""
        logger.info(f"输入用户名: {username}")
        self.fill(self.USERNAME_INPUT, username)

    def fill_password(self, password: str) -> None:
        """输入密码"""
        logger.info("输入密码: ******")
        self.fill(self.PASSWORD_INPUT, password)

    def click_login_button(self) -> None:
        """点击登录按钮"""
        logger.info("点击登录按钮")
        self.click(self.LOGIN_BUTTON)
        self.wait_for_network_idle()

    def wait_for_enterprise_modal(self) -> bool:
        """等待企业选择弹窗出现，返回是否出现"""
        return self.is_visible(self.ENTERPRISE_MODAL, timeout=10000)

    def select_first_enterprise(self) -> None:
        """选择第一个企业（默认选中列表中的第一项）"""
        logger.info("等待企业选择弹窗...")
        self.wait_for_visible(self.ENTERPRISE_MODAL, timeout=10000)
        logger.info("选择第一个企业")
        self.click(f"{self.ENTERPRISE_MODAL} {self.ENTERPRISE_CARD}")
        self.wait_for_network_idle()
        # 等待弹窗关闭
        self.wait_for_hidden(self.ENTERPRISE_MODAL, timeout=10000)
        logger.info("企业选择完成，弹窗已关闭")

    def login(
        self,
        username: str = None,
        password: str = None,
        select_enterprise: bool = True,
    ) -> None:
        """完整登录流程：输入账号密码 → 点击登录 → 选择企业

        参数默认从 data/account.json 读取 valid 账号
        """
        if username is None:
            username = get_account("valid", "username")
        if password is None:
            password = get_account("valid", "password")

        logger.info("===== 开始登录流程 =====")
        self.goto()
        self.fill_username(username)
        self.fill_password(password)
        self.click_login_button()

        # 登录成功后选择企业
        if select_enterprise:
            self.select_first_enterprise()

        logger.info("===== 登录流程完成 =====")
