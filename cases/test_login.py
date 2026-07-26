"""登录流程测试用例"""
import logging

import allure
import pytest

from pages.login_page import LoginPage
from pages.home_page import HomePage

logger = logging.getLogger("ui_auto")


@allure.feature("登录模块")
@allure.story("用户登录")
class TestLogin:

    @allure.title("正向用例：正确账号密码登录")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, page):
        """
        测试步骤：
        1. 访问登录页面
        2. 输入正确的账号密码
        3. 点击登录按钮
        4. 校验登录成功进入首页
        """
        logger.info("========== test_login_success 开始 ==========")

        # 1. 创建页面对象
        login_page = LoginPage(page)

        # 2. 执行登录
        login_page.login()

        # 3. 创建首页对象，校验首页加载
        home_page = HomePage(page)

        # 4. 断言：首页加载成功
        assert home_page.is_page_loaded(), (
            "登录后首页未成功加载，请检查截图。"
            "可能原因：1) 选择器不匹配 2) 登录失败 3) 网络超时"
        )

        # 5. 断言：页面标题不为空
        title = home_page.get_current_page_title()
        assert len(title) > 0, "页面标题为空，可能未成功进入系统"

        logger.info("========== test_login_success 通过 ==========")

    @allure.title("反向用例：错误密码登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, page):
        """
        测试步骤：
        1. 访问登录页面
        2. 输入正确账号 + 错误密码
        3. 点击登录
        4. 校验登录失败（停留在登录页或出现错误提示）
        """
        logger.info("========== test_login_wrong_password 开始 ==========")

        login_page = LoginPage(page)
        login_page.goto()

        login_page.fill_username("15926689137")
        login_page.fill_password("wrong_password_123")
        login_page.click_login_button()

        # 断言：登录失败应停留在登录页或有错误提示
        still_on_login = login_page.is_on_login_page()
        # 尝试检测错误提示（Ant Design message / notification）
        error_visible = page.locator(
            ".ant-message-error, .ant-message-notice, .ant-alert-error, [class*='error']"
        ).is_visible(timeout=3000) if not still_on_login else False

        assert still_on_login or error_visible, (
            "登录预期失败但页面行为不符合预期。"
            "请确认：1) 是否仍在登录页 2) 是否有错误提示"
        )

        logger.info("========== test_login_wrong_password 通过 ==========")
