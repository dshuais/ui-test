"""账户管理模块测试用例

基于 src/pages/system/basic/account-management/ 分析自动生成
包含: 页面加载、Tab 切换、搜索、新增往来账户、新增本方账户
"""
import logging

import allure
import pytest

from pages.account_page import AccountPage
from pages.login_page import LoginPage

logger = logging.getLogger("ui_auto")


@allure.feature("系统管理")
@allure.story("账户管理")
class TestAccount:

    @allure.title("正向用例：账户管理页面加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_account_list_loads(self, page):
        logger.info("========== test_account_list_loads 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()

        assert account_page.is_page_loaded(), "账户管理表格未加载"

        logger.info("========== test_account_list_loads 通过 ==========")

    @allure.title("正向用例：切换到本方账户 Tab")
    @allure.severity(allure.severity_level.NORMAL)
    def test_account_switch_tab(self, page):
        logger.info("========== test_account_switch_tab 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()

        # 切换到本方账户
        account_page.switch_to_self_tab()
        assert account_page.is_page_loaded(), "切换 Tab 后表格应仍显示"

        # 切回往来账户
        account_page.switch_to_customer_tab()
        assert account_page.is_page_loaded(), "切回往来账户表格应仍显示"

        logger.info("========== test_account_switch_tab 通过 ==========")

    @allure.title("正向用例：新增往来账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_customer_account(self, page):
        logger.info("========== test_add_customer_account 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()
        account_page.switch_to_customer_tab()

        # 新增一条往来账户
        import time
        ts = str(int(time.time()))[-6:]  # 用时间戳后6位避免重复
        acct_no = "62" + ts
        acct_name = f"测试户名{ts}"

        account_page.add_account(
            acct_no=acct_no,
            acct_name=acct_name,
            bank_name="中国银行",
            remark="自动化测试",
            customer_name="腾讯",
            is_self=False,
        )

        # 搜索验证新增成功
        account_page.search_by_cust_name("腾讯")

        assert account_page.is_page_loaded(), "新增账户后表格应仍显示"
        logger.info(f"新增往来账户: {acct_no} / {acct_name}")

        logger.info("========== test_add_customer_account 通过 ==========")

    @allure.title("正向用例：新增本方账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_self_account(self, page):
        logger.info("========== test_add_self_account 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()
        account_page.switch_to_self_tab()

        # 新增一条本方账户
        import time
        ts = str(int(time.time()))[-6:]
        acct_no = ts
        acct_name = f"本方测试{ts}"

        account_page.add_account(
            acct_no=acct_no,
            acct_name=acct_name,
            bank_name="中国银行",
            remark="自动化本方测试",
            is_self=True,
        )

        assert account_page.is_page_loaded(), "新增本方账户后表格应仍显示"
        logger.info(f"新增本方账户: {acct_no} / {acct_name}")

        logger.info("========== test_add_self_account 通过 ==========")
