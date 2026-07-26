"""首页功能校验测试用例"""
import logging

import allure
import pytest

from pages.login_page import LoginPage
from pages.home_page import HomePage

logger = logging.getLogger("ui_auto")


@allure.feature("首页模块")
@allure.story("首页功能校验")
class TestHome:

    @allure.title("正向用例：登录后首页基础元素校验")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_home_basic_elements(self, page):
        """
        测试步骤：
        1. 登录系统（含选择企业）
        2. 校验左侧菜单可见
        3. 校验顶部导航栏可见
        4. 校验页面标题正确
        """
        logger.info("========== test_home_basic_elements 开始 ==========")

        # 1. 登录
        login_page = LoginPage(page)
        login_page.login()

        # 2. 首页校验
        home_page = HomePage(page)
        assert home_page.is_page_loaded(), "首页加载失败"

        # 3. 左侧菜单可见
        assert home_page.is_side_menu_visible(), (
            "左侧菜单不可见，请检查：1) 登录是否成功 2) 企业是否已选择 3) 选择器是否匹配"
        )

        # 4. 顶部导航栏
        assert home_page.is_header_visible(), (
            "顶部导航栏不可见，请检查选择器是否匹配"
        )

        # 5. 页面标题校验
        title = home_page.get_current_page_title()
        logger.info(f"页面标题: {title}")
        assert title == "信企盈", f"页面标题应为'信企盈'，实际为'{title}'"

        logger.info("========== test_home_basic_elements 通过 ==========")

    @allure.title("正向用例：登录后主布局完整校验")
    @allure.severity(allure.severity_level.NORMAL)
    def test_home_layout_complete(self, page):
        """
        测试步骤：
        1. 登录系统（含选择企业）
        2. 校验整体布局元素齐全（侧栏 + 顶栏 + 内容区）
        """
        logger.info("========== test_home_layout_complete 开始 ==========")

        # 1. 登录
        login_page = LoginPage(page)
        login_page.login()

        # 2. 首页校验
        home_page = HomePage(page)
        assert home_page.is_page_loaded(), "首页加载失败"

        # 3. 各个布局元素
        assert home_page.is_side_menu_visible(), "左侧菜单不可见"
        assert home_page.is_header_visible(), "顶部导航栏不可见"

        logger.info("========== test_home_layout_complete 通过 ==========")
