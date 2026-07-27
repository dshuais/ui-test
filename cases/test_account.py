"""账户管理模块 — 完整测试覆盖

基于 src/pages/system/basic/account-management/ 源码分析生成
覆盖范围：
  - Tab 切换（往来账户 / 本方账户）
  - 列表加载（两个 Tab）
  - 搜索功能（往来账户按客户名、本方账户按户名）
  - 往来账户生命周期：新增 → 禁用 → 启用 → 删除（共享一条数据）
  - 本方账户生命周期：新增 → 禁用 → 启用 → 删除（共享一条数据）
"""
import logging
import time

import allure
import pytest

from pages.account_page import AccountPage
from pages.login_page import LoginPage
from common.browser_engine import BrowserEngine
from common.utils import get_config

logger = logging.getLogger("ui_auto")


# ══════════════════════════════════════════════════════════════
# 模块级功能测试（Tab 切换、列表加载、搜索）
# 每条用例独立，使用 conftest 的 function 级 page fixture
# ══════════════════════════════════════════════════════════════

@allure.feature("系统管理")
@allure.story("账户管理")
class TestAccountFeatures:

    # ─── Tab 切换 ───────────────────────────────────────

    @allure.title("正向用例：Tab 切换 - 往来账户 / 本方账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tab_switch(self, page):
        """
        测试步骤：
        1. 登录系统
        2. 导航到账户管理
        3. 切换到本方账户 Tab → 校验表格加载
        4. 切换到往来账户 Tab → 校验表格加载
        """
        logger.info("========== test_tab_switch 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()

        # 切换到本方账户
        account_page.switch_to_self_tab()
        self_tab_loaded = account_page.is_table_loaded()
        assert self_tab_loaded, "切换至本方账户后列表未加载"

        # 切换到往来账户
        account_page.switch_to_customer_tab()
        cust_tab_loaded = account_page.is_table_loaded()
        assert cust_tab_loaded, "切换至往来账户后列表未加载"

        logger.info("========== test_tab_switch 通过 ==========")

    # ─── 列表加载 ───────────────────────────────────────

    @allure.title("正向用例：往来账户列表加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_customer_list_loads(self, page):
        """
        测试步骤：
        1. 登录系统
        2. 导航到账户管理
        3. 默认在往来账户 Tab → 校验表格加载
        """
        logger.info("========== test_customer_list_loads 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()

        assert account_page.is_table_loaded(), "往来账户列表表格未加载"

        logger.info("========== test_customer_list_loads 通过 ==========")

    @allure.title("正向用例：本方账户列表加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_self_list_loads(self, page):
        """
        测试步骤：
        1. 登录系统
        2. 导航到账户管理
        3. 切换到本方账户 Tab → 校验表格加载
        """
        logger.info("========== test_self_list_loads 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()
        account_page.switch_to_self_tab()

        assert account_page.is_table_loaded(), "本方账户列表表格未加载"

        logger.info("========== test_self_list_loads 通过 ==========")

    # ─── 搜索 ───────────────────────────────────────────

    @allure.title("正向用例：往来账户按客户名搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_customer_search_by_name(self, page):
        """
        测试步骤：
        1. 登录系统
        2. 导航到账户管理 → 往来账户 Tab
        3. 输入往来客户名搜索
        4. 校验搜索后表格仍显示
        """
        logger.info("========== test_customer_search_by_name 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()

        account_page.search_customer_by_name("腾讯")

        assert account_page.is_table_loaded(), "往来账户搜索后表格应仍然显示"

        logger.info("========== test_customer_search_by_name 通过 ==========")

    @allure.title("正向用例：本方账户按户名搜索")
    @allure.severity(allure.severity_level.NORMAL)
    def test_self_search_by_name(self, page):
        """
        测试步骤：
        1. 登录系统
        2. 导航到账户管理 → 本方账户 Tab
        3. 输入户名搜索
        4. 校验搜索后表格仍显示
        """
        logger.info("========== test_self_search_by_name 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        account_page = AccountPage(page)
        account_page.navigate()
        account_page.switch_to_self_tab()

        account_page.search_self_by_name("测试")

        assert account_page.is_table_loaded(), "本方账户搜索后表格应仍然显示"

        logger.info("========== test_self_search_by_name 通过 ==========")


# ══════════════════════════════════════════════════════════════
# 往来账户生命周期测试
# 同一条数据贯穿：新增 → 禁用 → 启用 → 删除
# ══════════════════════════════════════════════════════════════

@allure.feature("系统管理")
@allure.story("账户管理 - 往来账户")
class TestAccountCustomer:

    acct_no = ""
    acct_name = ""

    @pytest.fixture(scope="class")
    def shared_page(self, browser_engine: BrowserEngine):
        """共享一个 page，四个用例串行执行"""
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

        # 生成唯一测试数据（62 开头的银联卡号格式）
        ts = str(int(time.time()))[-6:]
        TestAccountCustomer.acct_no = "62" + ts
        TestAccountCustomer.acct_name = f"自动化测试{ts}"

        yield page
        context.close()

    @allure.title("【往来账户】1. 新增往来账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_01_add(self, shared_page):
        account_page = AccountPage(shared_page)

        account_page.add_customer_account(
            acct_no=TestAccountCustomer.acct_no,
            acct_name=TestAccountCustomer.acct_name,
            bank_name="中国银行",
            remark="自动化测试-往来账户",
        )

        with allure.step("验证：新增后列表中应出现该账户"):
            account_page.attach_screenshot("往来账户-新增后列表")
            # 新增后表格已刷新，直接验证行存在
            assert account_page.is_table_loaded(), "新增后表格应正常加载"
            assert account_page.is_row_visible(TestAccountCustomer.acct_name), \
                f"新增后表格中应包含 {TestAccountCustomer.acct_name}"

    @allure.title("【往来账户】2. 禁用往来账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_02_disable(self, shared_page):
        account_page = AccountPage(shared_page)

        account_page.disable_account(TestAccountCustomer.acct_name)

        with allure.step("验证：禁用后列表正常"):
            account_page.attach_screenshot("往来账户-禁用后列表")
            assert account_page.is_table_loaded(), "禁用后表格应正常加载"

    @allure.title("【往来账户】3. 启用往来账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_03_enable(self, shared_page):
        account_page = AccountPage(shared_page)

        account_page.enable_account(TestAccountCustomer.acct_name)

        with allure.step("验证：启用后列表正常"):
            account_page.attach_screenshot("往来账户-启用后列表")
            assert account_page.is_table_loaded(), "启用后表格应正常加载"

    @allure.title("【往来账户】4. 删除往来账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_04_delete(self, shared_page):
        account_page = AccountPage(shared_page)

        # 必须先禁用才能删除（源码规则：启用状态不可删除）
        account_page.disable_account(TestAccountCustomer.acct_name)

        account_page.delete_account(TestAccountCustomer.acct_name)

        with allure.step("验证：删除后列表中不应再出现该账户"):
            account_page.attach_screenshot("往来账户-删除后列表")
            account_page.reset_search_customer()
            assert not account_page.is_row_visible(TestAccountCustomer.acct_name), \
                f"删除后表格中不应再包含 {TestAccountCustomer.acct_name}"


# ══════════════════════════════════════════════════════════════
# 本方账户生命周期测试
# 同一条数据贯穿：新增 → 禁用 → 启用 → 删除
# ══════════════════════════════════════════════════════════════

@allure.feature("系统管理")
@allure.story("账户管理 - 本方账户")
class TestAccountSelf:

    acct_no = ""
    acct_name = ""

    @pytest.fixture(scope="class")
    def shared_page(self, browser_engine: BrowserEngine):
        """共享一个 page，四个用例串行执行"""
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
        account_page.switch_to_self_tab()

        # 生成唯一测试数据
        ts = str(int(time.time()))[-6:]
        TestAccountSelf.acct_no = "99" + ts
        TestAccountSelf.acct_name = f"自动化账户{ts}"

        yield page
        context.close()

    @allure.title("【本方账户】1. 新增本方账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_01_add(self, shared_page):
        account_page = AccountPage(shared_page)

        account_page.add_self_account(
            acct_no=TestAccountSelf.acct_no,
            acct_name=TestAccountSelf.acct_name,
            bank_name="中国银行",
            remark="自动化测试-本方账户",
        )

        with allure.step("验证：新增后列表中应出现该账户"):
            account_page.attach_screenshot("本方账户-新增后列表")
            account_page.search_self_by_name(TestAccountSelf.acct_name)
            assert account_page.is_row_visible(TestAccountSelf.acct_name), \
                f"新增后表格中应包含 {TestAccountSelf.acct_name}"

    @allure.title("【本方账户】2. 禁用本方账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_02_disable(self, shared_page):
        account_page = AccountPage(shared_page)

        account_page.search_self_by_name(TestAccountSelf.acct_name)
        account_page.disable_account(TestAccountSelf.acct_name)

        with allure.step("验证：禁用后列表正常"):
            account_page.search_self_by_name(TestAccountSelf.acct_name)
            account_page.attach_screenshot("本方账户-禁用后列表")
            assert account_page.is_table_loaded(), "禁用后表格应正常加载"

    @allure.title("【本方账户】3. 启用本方账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_03_enable(self, shared_page):
        account_page = AccountPage(shared_page)

        account_page.search_self_by_name(TestAccountSelf.acct_name)
        account_page.enable_account(TestAccountSelf.acct_name)

        with allure.step("验证：启用后列表正常"):
            account_page.search_self_by_name(TestAccountSelf.acct_name)
            account_page.attach_screenshot("本方账户-启用后列表")
            assert account_page.is_table_loaded(), "启用后表格应正常加载"

    @allure.title("【本方账户】4. 删除本方账户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_04_delete(self, shared_page):
        account_page = AccountPage(shared_page)

        # 必须先禁用才能删除
        account_page.search_self_by_name(TestAccountSelf.acct_name)
        account_page.disable_account(TestAccountSelf.acct_name)

        account_page.search_self_by_name(TestAccountSelf.acct_name)
        account_page.delete_account(TestAccountSelf.acct_name)

        with allure.step("验证：删除后列表中不应再出现该账户"):
            account_page.reset_search_self()
            account_page.search_self_by_name(TestAccountSelf.acct_name)
            account_page.attach_screenshot("本方账户-删除后列表")
            assert not account_page.is_row_visible(TestAccountSelf.acct_name), \
                f"删除后表格中不应再包含 {TestAccountSelf.acct_name}"
