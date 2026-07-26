"""往来客户模块测试用例

基于 src/pages/system/basic/customers-management/ 代码分析自动生成
"""
import logging

import allure
import pytest

from pages.customers_page import CustomersPage
from pages.login_page import LoginPage

logger = logging.getLogger("ui_auto")


@allure.feature("系统管理")
@allure.story("往来客户")
class TestCustomers:

    @allure.title("正向用例：客户列表页面加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_customer_list_loads(self, page):
        """
        测试步骤：
        1. 登录系统（含选择企业）
        2. 导航到往来客户列表页
        3. 校验表格加载
        """
        logger.info("========== test_customer_list_loads 开始 ==========")

        # 1. 登录
        login_page = LoginPage(page)
        login_page.login()

        # 2. 导航到客户列表
        customers_page = CustomersPage(page)
        customers_page.navigate()

        # 3. 断言表格加载
        assert customers_page.is_table_loaded(), "客户列表表格未加载，请检查页面或选择器"

        logger.info("========== test_customer_list_loads 通过 ==========")

    @allure.title("正向用例：按客户名称搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_customer_search_by_name(self, page):
        """
        测试步骤：
        1. 登录系统
        2. 导航到客户列表
        3. 输入关键词搜索
        4. 校验搜索后有结果或显示空态
        """
        logger.info("========== test_customer_search_by_name 开始 ==========")

        # 1. 登录
        login_page = LoginPage(page)
        login_page.login()

        # 2. 导航到客户列表
        customers_page = CustomersPage(page)
        customers_page.navigate()

        # 3. 搜索
        customers_page.search_by_name("测试")

        # 4. 校验表格仍然加载（不论有无数据）
        assert customers_page.is_table_loaded(), "搜索后表格应仍然显示"

        logger.info("========== test_customer_search_by_name 通过 ==========")
