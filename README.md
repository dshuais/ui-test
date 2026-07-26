# UI 自动化测试框架

基于 **Playwright + Pytest + Allure + PO 设计模式** 的 GGJX ERP 系统 UI 自动化测试。

## 技术栈

| 组件 | 用途 |
|------|------|
| Python 3.x | 编程语言 |
| Playwright | 浏览器驱动、元素定位、截图 |
| Pytest | 测试运行器、夹具管理 |
| Allure | 可视化测试报告 |
| PO 模式 | 页面对象分层（pages/cases 分离） |

## 目录结构

```
cc-test/
├── .claude/                  # Claude Code 全局编码规范
│   └── system_rule.md
├── common/                   # 公共底层（不需频繁修改）
│   ├── base_page.py          # PO 基类（等待、点击、输入、截图）
│   ├── browser_engine.py     # 浏览器启动/关闭
│   ├── logger.py             # 日志模块
│   └── utils.py              # 工具类（JSON 读取）
├── pages/                    # 页面对象层（元素定位 + 操作）
│   ├── login_page.py         # 登录页
│   └── home_page.py          # 首页
├── cases/                    # 测试用例层（流程 + 断言）
│   ├── test_login.py         # 登录用例
│   └── test_home.py          # 首页用例
├── data/                     # 配置与测试数据
│   ├── config.json           # 环境地址、浏览器配置
│   └── account.json          # 测试账号
├── reports/                  # 产物输出（自动生成）
│   ├── allure_raw/           # Allure 原始数据
│   ├── allure_html/          # Allure HTML 报告
│   ├── screenshots/          # 失败截图
│   └── logs/                 # 运行日志
├── conftest.py               # Pytest 全局夹具
├── pytest.ini                # Pytest 配置
├── requirements.txt          # 依赖清单
├── run_test.sh               # 一键执行（Mac/Linux）
├── run_test.bat              # 一键执行（Windows）
└── README.md                 # 本文档
```

## 环境安装

```bash
# 1. 进入项目目录
cd cc-test

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate     # Mac/Linux
# venv\Scripts\activate      # Windows

# 3. 安装 Python 依赖
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器内核（仅首次）
playwright install chromium
```

## 运行方式

### 执行全部用例

```bash
pytest cases/ -v -s
```

### 执行单个模块

```bash
pytest cases/test_login.py -v -s
```

### 生成 Allure 报告

```bash
# 执行用例并采集数据
pytest cases/ --alluredir=reports/allure_raw

# 生成 HTML 报告
allure generate reports/allure_raw -o reports/allure_html --clean

# 打开报告
allure open reports/allure_html
```

### 一键执行（含报告）

```bash
# Mac / Linux
bash run_test.sh

# Windows
run_test.bat
```

### 切换浏览器模式

修改 `data/config.json` 中的 `browser.headless`：
- `true` — 无头模式（后台运行，适合 CI/CD）
- `false` — 有头模式（可视化运行，适合调试）

## 新增页面 & 用例

### 1. 新增页面对象（PO）

在 `pages/` 下新建 `xxx_page.py`：

```python
from common.base_page import BasePage

class XxxPage(BasePage):
    # 元素定位器
    SEARCH_INPUT = "input[placeholder='搜索']"
    SEARCH_BUTTON = "button:has-text('查询')"

    # 操作方法
    def search(self, keyword: str):
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)
```

### 2. 新增测试用例

在 `cases/` 下新建 `test_xxx.py`：

```python
import allure
from pages.xxx_page import XxxPage

@allure.feature("XXX模块")
class TestXxx:
    def test_search(self, page):
        xxx_page = XxxPage(page)
        xxx_page.navigate("http://erp-dev.guanggujinxin.com/#/xxx")
        xxx_page.search("关键词")
        # 添加断言...
```

## 注意事项

1. **禁止修改 common/ 底层代码**，除非明确需要升级公共能力
2. **元素选择器优先级**：data-testid > CSS > 相对 xpath
3. **禁止使用 time.sleep()**，统一使用 BasePage 封装的显式等待方法
4. **测试数据和代码分离**，切换环境只改 data/ 下 JSON 文件
5. **用例失败自动截图**，查看 `reports/screenshots/` 目录
