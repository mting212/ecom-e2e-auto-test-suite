# pages/baidu_page.py
"""搜索页 Page Object —— 使用 DuckDuckGo（对 headless 友好）"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver


class SearchPage:
    """DuckDuckGo 搜索页 —— headless 可稳定运行"""

    URL = "https://duckduckgo.com"

    SEARCH_BOX = (By.NAME, "q")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.URL)
        return self

    def search(self, keyword: str):
        box = self.wait.until(EC.element_to_be_clickable(self.SEARCH_BOX))
        box.clear()
        box.send_keys(f"{keyword}\n")
        return self

    def wait_title_contains(self, text: str):
        self.wait.until(EC.title_contains(text))
        return self

    @property
    def title(self):
        return self.driver.title
