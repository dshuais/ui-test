"""待开票列表模块测试用例

基于 src/pages/invoicing/uninvoiced/uninvoiced-list.tsx 分析自动生成
"""
import logging

import allure
import pytest

from pages.uninvoiced_page import UninvoicedPage
from pages.login_page import LoginPage

logger = logging.getLogger("ui_auto")


@allure.feature("开票管理")
@allure.story("待开票列表")
class TestUninvoiced:

    @allure.title("正向用例：待开票列表页面加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_uninvoiced_list_loads(self, page):
        """
        测试步骤：
        1. 登录（含选择企业）
        2. 通过菜单导航到待开票列表
        3. 校验表格加载
        """
        logger.info("========== test_uninvoiced_list_loads 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        uninvoiced_page = UninvoicedPage(page)
        uninvoiced_page.navigate()

        assert uninvoiced_page.is_table_loaded(), "待开票列表表格未加载"

        logger.info("========== test_uninvoiced_list_loads 通过 ==========")

    @allure.title("正向用例：按车牌号搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_uninvoiced_search_by_plate(self, page):
        """
        测试步骤：
        1. 登录
        2. 导航到待开票列表
        3. 输入车牌号搜索
        4. 校验表格仍显示
        """
        logger.info("========== test_uninvoiced_search_by_plate 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        uninvoiced_page = UninvoicedPage(page)
        uninvoiced_page.navigate()

        uninvoiced_page.search_by_plate_no("鄂A12345")

        assert uninvoiced_page.is_table_loaded(), "搜索后表格应仍然显示"

        logger.info("========== test_uninvoiced_search_by_plate 通过 ==========")

    @allure.title("正向用例：点击刷新按钮")
    @allure.severity(allure.severity_level.NORMAL)
    def test_uninvoiced_refresh(self, page):
        """
        测试步骤：
        1. 登录
        2. 导航到待开票列表
        3. 点击刷新按钮
        4. 校验表格重新加载
        """
        logger.info("========== test_uninvoiced_refresh 开始 ==========")

        login_page = LoginPage(page)
        login_page.login()

        uninvoiced_page = UninvoicedPage(page)
        uninvoiced_page.navigate()

        uninvoiced_page.click_refresh()

        assert uninvoiced_page.is_table_loaded(), "刷新后表格应仍然显示"

        logger.info("========== test_uninvoiced_refresh 通过 ==========")
