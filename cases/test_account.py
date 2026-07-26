"""账户管理模块 — 同一账户的完整生命周期测试

流程：新增 → 禁用 → 启用 → 删除
同一个账户从头到尾，截图只在操作完成后验证时刻。
"""
import time

import allure
import pytest

from pages.account_page import AccountPage
from pages.login_page import LoginPage
from common.browser_engine import BrowserEngine
from common.utils import get_config


@allure.feature("系统管理")
@allure.story("账户管理")
class TestAccount:

    acct_name = ""
    acct_no = ""

    @pytest.fixture(scope="class")
    def shared_page(self, browser_engine: BrowserEngine):
        """共享一个 page，所有用例串行执行"""
        browser, context, page = browser_engine.new_context()

        try:
            page.goto(get_config("base_url"), wait_until="domcontentloaded")
            page.evaluate("() => { localStorage.setItem('debug_micro_apps', 'web-erp'); }")
        except Exception:
            pass

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()
        account_page.switch_to_customer_tab()

        ts = str(int(time.time()))[-6:]
        TestAccount.acct_no = "62" + ts
        TestAccount.acct_name = f"自动化测试{ts}"

        yield page
        context.close()

    @allure.title("1. 新增往来账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_01_add(self, shared_page):
        account_page = AccountPage(shared_page)

        account_page.add_account(
            acct_no=TestAccount.acct_no,
            acct_name=TestAccount.acct_name,
            bank_name="中国银行",
            remark="自动化测试",
            is_self=False,
        )
        with allure.step("验证：新增后列表"):
            account_page.attach_screenshot("新增后列表")
            assert account_page.is_row_visible(TestAccount.acct_name), \
                f"新增后表格中应包含 {TestAccount.acct_name}"

    @allure.title("2. 禁用账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_02_disable(self, shared_page):
        account_page = AccountPage(shared_page)
        account_page.disable_account(TestAccount.acct_name)
        with allure.step("验证：禁用后列表"):
            account_page.attach_screenshot("禁用后列表")
            assert account_page.is_page_loaded()

    @allure.title("3. 启用账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_03_enable(self, shared_page):
        account_page = AccountPage(shared_page)
        account_page.enable_account(TestAccount.acct_name)
        with allure.step("验证：启用后列表"):
            account_page.attach_screenshot("启用后列表")
            assert account_page.is_page_loaded()

    @allure.title("4. 删除账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_04_delete(self, shared_page):
        account_page = AccountPage(shared_page)

        account_page.disable_account(TestAccount.acct_name)
        account_page.delete_account(TestAccount.acct_name)
        with allure.step("验证：删除后列表"):
            account_page.attach_screenshot("删除后列表")
            assert not account_page.is_row_visible(TestAccount.acct_name), \
                f"删除后表格中不应再包含 {TestAccount.acct_name}"
