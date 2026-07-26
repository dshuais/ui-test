"""地址管理模块 — 同一地址的完整生命周期测试

流程：新增（客户地址）→ 禁用 → 启用 → 删除
"""
import time

import allure
import pytest

from pages.address_page import AddressPage
from pages.login_page import LoginPage
from common.browser_engine import BrowserEngine
from common.utils import get_config


@allure.feature("系统管理")
@allure.story("地址管理")
class TestAddress:

    address_name = ""

    @pytest.fixture(scope="class")
    def shared_page(self, browser_engine: BrowserEngine):
        browser, context, page = browser_engine.new_context()

        try:
            page.goto(get_config("base_url"), wait_until="domcontentloaded")
            page.evaluate("() => { localStorage.setItem('debug_micro_apps', 'web-erp'); }")
        except Exception:
            pass

        login_page = LoginPage(page)
        login_page.login()

        address_page = AddressPage(page)
        address_page.navigate()
        address_page.switch_to_customer_tab()

        ts = str(int(time.time()))[-6:]
        TestAddress.address_name = f"自动化地址{ts}"

        yield page
        context.close()

    @allure.title("1. 新增客户地址")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_01_add(self, shared_page):
        address_page = AddressPage(shared_page)
        address_page.add_address(address_name=TestAddress.address_name)

        with allure.step("验证：新增后列表"):
            address_page.attach_screenshot("新增后列表")
            assert address_page.is_row_visible(TestAddress.address_name), \
                f"新增后应能搜索到 {TestAddress.address_name}"

    @allure.title("2. 禁用地址")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_02_disable(self, shared_page):
        address_page = AddressPage(shared_page)
        address_page.disable_address(TestAddress.address_name)

        with allure.step("验证：禁用后列表"):
            address_page.attach_screenshot("禁用后列表")
            assert address_page.is_page_loaded()

    @allure.title("3. 启用地址")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_03_enable(self, shared_page):
        address_page = AddressPage(shared_page)
        address_page.enable_address(TestAddress.address_name)

        with allure.step("验证：启用后列表"):
            address_page.attach_screenshot("启用后列表")
            assert address_page.is_page_loaded()

    @allure.title("4. 删除地址")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_04_delete(self, shared_page):
        address_page = AddressPage(shared_page)

        address_page.disable_address(TestAddress.address_name)
        address_page.delete_address(TestAddress.address_name)

        with allure.step("验证：删除后列表"):
            address_page.attach_screenshot("删除后列表")
            assert not address_page.is_row_visible(TestAddress.address_name), \
                f"删除后不应再搜索到 {TestAddress.address_name}"
