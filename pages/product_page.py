"""商品管理页面对象

基于 src/pages/system/basic/product-management/ 分析生成。
- 列表页: 搜索(商品名称/品种/品类/状态)、新建按钮、行操作(编辑/禁用/启用/详情)
- 新增页: 独立路由，16个字段（行业/品种/品类/名称/品牌/规格/型号/重量单位/是否标品/是否计件/计件单位/单件重量/长/宽/高/材质）
"""
import logging

import allure
from playwright.sync_api import Page

from common.base_page import BasePage
from common.utils import get_config

logger = logging.getLogger("ui_auto")


class ProductPage(BasePage):
    """商品管理 PO 对象"""

    SIDER = "aside.ant-layout-sider"
    MENU_BASIC = f"{SIDER} li:has-text('基础配置')"
    MENU_PRODUCT = f"{SIDER} li.ant-menu-item:has-text('商品管理')"

    # 列表页
    SEARCH_SKU_NAME = "input[placeholder='请输入商品名称']"
    BTN_SEARCH = "button:has-text('查 询')"
    BTN_NEW = "button:has-text('新 建')"
    TABLE = ".ant-table, .fe-table-wrapper"
    TABLE_ROWS = ".ant-table-tbody tr.ant-table-row"

    # 行操作
    BTN_DISABLE = "span.fe-link:has-text('禁用')"
    BTN_ENABLE = "span.fe-link:has-text('启用')"

    # 确认弹窗
    CONFIRM_MODAL = ".ant-modal-confirm"
    CONFIRM_OK = f"{CONFIRM_MODAL} button.ant-btn-primary, {CONFIRM_MODAL} .ant-btn-primary"

    # ─── 导航 ───────────────────────────────────────

    @allure.step("导航到商品管理")
    def navigate(self) -> None:
        basic = self.page.locator(self.MENU_BASIC).first
        basic.click()
        self.page.wait_for_timeout(800)
        self.click(self.MENU_PRODUCT)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    def is_page_loaded(self) -> bool:
        return self.is_visible(self.TABLE, timeout=15000)

    def is_row_visible(self, text: str) -> bool:
        return self.is_visible(f"{self.TABLE_ROWS}:has-text('{text}')", timeout=5000)

    # ─── 搜索 ───────────────────────────────────────

    @allure.step("搜索商品: {name}")
    def search_by_name(self, name: str) -> None:
        self.fill(self.SEARCH_SKU_NAME, name)
        self.click(self.BTN_SEARCH)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    # ─── 新增商品 ───────────────────────────────────

    @allure.step("打开新增页面")
    def go_to_add_page(self) -> None:
        self.click(self.BTN_NEW)
        self.page.wait_for_timeout(3000)
        self.wait_for_network_idle()

    def _pick_labeled_select(self, label_text: str) -> None:
        """通过 label 文字找到 select 并选择第一项"""
        row = self.page.locator(f".ant-form-item:has(.ant-form-item-label:has-text('{label_text}'))").first
        row.locator('.ant-select-selector').first.click()
        self.page.wait_for_timeout(800)
        option = self.page.locator('.ant-select-item-option:visible').first
        if option.is_visible():
            option.click()
            self.page.wait_for_timeout(500)
        else:
            self.page.keyboard.press('Escape')
            self.page.wait_for_timeout(300)

    @allure.step("填写商品表单: {sku_name}")
    def fill_product_form(self, sku_name: str, brand: str = "测试品牌", spec: str = "测试规格") -> None:
        # 等 auto-select 行业
        self.page.wait_for_timeout(2000)

        # 品种
        self._pick_labeled_select("所属品种")
        self.page.wait_for_timeout(1500)

        # 品类
        self._pick_labeled_select("所属品类")

        # 商品名称
        self.page.locator("input[id*='skuName']").first.fill(sku_name)
        # 品牌
        self.page.locator("input[id*='skuBrandName']").first.fill(brand)
        # 规格
        self.page.locator("input[id*='skuSpecification']").first.fill(spec)

        # 重量单位
        self._pick_labeled_select("重量单位")

        # 计件单位（标品默认=是 → isPiece=是 → 计件单位必填），等 autoset
        self.page.wait_for_timeout(1000)
        self._pick_labeled_select("计件单位")

        # 单件重量
        weight_input = self.page.locator("input[id*='pieceWeight']").first
        if weight_input.is_visible():
            weight_input.fill("1")

    @allure.step("提交商品")
    def submit_product(self) -> None:
        self.click("button:has-text('确 认')")
        # 提交后会跳回列表，等待页面重新渲染
        self.page.wait_for_timeout(5000)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)

    @allure.step("新增商品: {sku_name}")
    def add_product(self, sku_name: str) -> None:
        self.go_to_add_page()
        self.fill_product_form(sku_name=sku_name)
        self.submit_product()

    # ─── 行操作 ─────────────────────────────────────

    def _click_row_action(self, row_text: str, button_selector: str) -> None:
        self.wait_for_visible(f"{self.TABLE_ROWS}:has-text('{row_text}')", timeout=10000)
        self.page.wait_for_timeout(500)
        row = self.page.locator(f"{self.TABLE_ROWS}:has-text('{row_text}')").first
        btn = row.locator(button_selector).first
        btn.scroll_into_view_if_needed()
        btn.click()

    def _confirm(self) -> None:
        self.page.wait_for_timeout(500)
        ok_btn = self.page.locator(self.CONFIRM_OK).first
        if ok_btn.is_visible(timeout=3000):
            ok_btn.click()
            self.wait_for_network_idle()
            self.page.wait_for_timeout(1500)

    @allure.step("禁用商品: {sku_name}")
    def disable_product(self, sku_name: str) -> None:
        self._click_row_action(sku_name, self.BTN_DISABLE)
        self._confirm()

    @allure.step("启用商品: {sku_name}")
    def enable_product(self, sku_name: str) -> None:
        self._click_row_action(sku_name, self.BTN_ENABLE)
        self._confirm()

    def attach_screenshot(self, name: str) -> None:
        try:
            allure.attach(
                self.page.screenshot(full_page=True),
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
