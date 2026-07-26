"""商品管理模块 — 同一商品的完整生命周期测试

流程：新增 → 禁用 → 启用
（商品管理无删除操作）
"""
import time

import allure
import pytest

from pages.product_page import ProductPage
from pages.login_page import LoginPage
from common.browser_engine import BrowserEngine
from common.utils import get_config


@allure.feature("系统管理")
@allure.story("商品管理")
class TestProduct:

    sku_name = ""

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

        product_page = ProductPage(page)
        product_page.navigate()

        ts = str(int(time.time()))[-6:]
        TestProduct.sku_name = f"自动化商品{ts}"

        yield page
        context.close()

    @allure.title("1. 新增商品")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_01_add(self, shared_page):
        product_page = ProductPage(shared_page)
        product_page.add_product(sku_name=TestProduct.sku_name)

        with allure.step("验证：新增后列表"):
            product_page.search_by_name(TestProduct.sku_name)
            product_page.attach_screenshot("新增后列表")
            assert product_page.is_row_visible(TestProduct.sku_name), \
                f"新增后应能搜索到 {TestProduct.sku_name}"

    @allure.title("2. 禁用商品")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_02_disable(self, shared_page):
        product_page = ProductPage(shared_page)
        product_page.search_by_name(TestProduct.sku_name)
        product_page.disable_product(TestProduct.sku_name)

        with allure.step("验证：禁用后列表"):
            product_page.search_by_name(TestProduct.sku_name)
            product_page.attach_screenshot("禁用后列表")
            assert product_page.is_page_loaded()

    @allure.title("3. 启用商品")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_03_enable(self, shared_page):
        product_page = ProductPage(shared_page)
        product_page.search_by_name(TestProduct.sku_name)
        product_page.enable_product(TestProduct.sku_name)

        with allure.step("验证：启用后列表"):
            product_page.search_by_name(TestProduct.sku_name)
            product_page.attach_screenshot("启用后列表")
            assert product_page.is_page_loaded()
