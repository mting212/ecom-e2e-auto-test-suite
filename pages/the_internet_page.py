# pages/the_internet_page.py
"""The-Internet 弹窗练习页 —— Page Object"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver


class JavaScriptAlertsPage:
    """https://the-internet.herokuapp.com/javascript_alerts"""

    URL = "https://the-internet.herokuapp.com/javascript_alerts"

    # ===== 元素定位符（集中管理，改这里就全改了）=====
    BTN_JS_ALERT = (By.CSS_SELECTOR, "button[onclick='jsAlert()']")
    BTN_JS_CONFIRM = (By.CSS_SELECTOR, "button[onclick='jsConfirm()']")
    BTN_JS_PROMPT = (By.CSS_SELECTOR, "button[onclick='jsPrompt()']")
    RESULT_TEXT = (By.ID, "result")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # ===== 页面操作（方法）=====
    def open(self):
        self.driver.get(self.URL)
        return self  # 返回 self 支持链式调用

    def click_js_alert(self):
        self.driver.find_element(*self.BTN_JS_ALERT).click()
        return self

    def click_js_confirm(self):
        self.driver.find_element(*self.BTN_JS_CONFIRM).click()
        return self

    def click_js_prompt(self):
        self.driver.find_element(*self.BTN_JS_PROMPT).click()
        return self

    def get_result_text(self):
        """等待结果文字出现，返回文字"""
        el = self.wait.until(
            EC.visibility_of_element_located(self.RESULT_TEXT)
        )
        return el.text

    # ===== Alert 操作封装 =====
    def accept_alert(self):
        alert = self.driver.switch_to.alert
        text = alert.text
        alert.accept()
        return text  # 返回弹窗文字供断言

    def dismiss_alert(self):
        alert = self.driver.switch_to.alert
        text = alert.text
        alert.dismiss()
        return text

    def input_and_accept_alert(self, text: str):
        alert = self.driver.switch_to.alert
        alert.send_keys(text)
        alert.accept()