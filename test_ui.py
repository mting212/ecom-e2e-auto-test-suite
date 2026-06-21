# test_ui.py
"""Selenium UI 自动化测试"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="module")
def driver():
    """启动浏览器，所有用例共用一个浏览器实例"""
    options = Options()
    options.add_argument("--headless")       # 无界面模式（WSL 必须）
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    yield driver
    driver.quit()  # 测试结束关浏览器


def test_open_baidu(driver):
    """打开百度，断言标题包含'百度'"""
    driver.get("https://www.baidu.com")
    assert "百度" in driver.title
    print(f"页面标题: {driver.title}")

def test_baidu_search(driver):
    """百度搜索 python，断言结果页包含搜索结果"""
    driver.get("https://www.baidu.com")

    # 找到搜索框，输入关键词
    search_box = driver.find_element("id", "kw")
    search_box.clear()
    search_box.send_keys("python\n")  # \n 回车 = 点击搜索

    # 等待页面加载（简单方式，后面学显式等待）
    import time
    time.sleep(2)

    # 断言：页面标题变了
    assert "python" in driver.title

    # 断言：搜索结果里有关键词
    page_text = driver.find_element("tag name", "body").text
    assert "python" in page_text.lower()
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert


def test_baidu_search_with_wait(driver):
    """百度搜索 —— 用显式等待替代 time.sleep"""
    driver.get("https://www.baidu.com")

    # 等待搜索框出现并可输入
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "kw"))
    )
    search_box.send_keys("pytest\n")

    # 等待结果页标题变化
    WebDriverWait(driver, 10).until(
        EC.title_contains("pytest")
    )

    assert "pytest" in driver.title  


# ===== Day 14：Page Object 模式 =====
from pages.the_internet_page import JavaScriptAlertsPage


def test_po_alert_accept(driver):
    """Page Object 版：弹窗 — 点确定"""
    page = JavaScriptAlertsPage(driver)  # 创建页面对象

    page.open()                          # 打开页面
    page.click_js_alert()               # 点击按钮

    alert_text = page.accept_alert()     # 接受弹窗，拿到弹窗文字
    assert "I am a JS Alert" in alert_text

    result = page.get_result_text()
    assert "You successfully clicked an alert" in result


def test_po_alert_dismiss(driver):
    """Page Object 版：弹窗 — 点取消"""
    page = JavaScriptAlertsPage(driver)

    page.open().click_js_confirm()       # 链式调用：打开 + 点击
    page.dismiss_alert()

    assert "You clicked: Cancel" in page.get_result_text()


def test_po_alert_prompt(driver):
    """Page Object 版：弹窗 — 输入+确定"""
    page = JavaScriptAlertsPage(driver)

    page.open().click_js_prompt()
    page.input_and_accept_alert("Hello Page Object")

    assert "You entered: Hello Page Object" in page.get_result_text()


from pages.baidu_page import BaiduPage


def test_po_baidu_search(driver):
    """Page Object 版：百度搜索"""
    page = BaiduPage(driver)
    page.open().search("selenium webdriver").wait_title_contains("selenium")

    assert "selenium" in page.title