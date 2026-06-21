from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver


class BaiduPage:
    URL = "https://www.baidu.com"

    SEARCH_BOX = (By.ID, "kw")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.URL)
        return self

    def search(self, keyword: str):
        """输入关键词并搜索（\n = 回车）"""
        box = self.wait.until(
            EC.presence_of_element_located(self.SEARCH_BOX)
        )
        box.clear()
        box.send_keys(f"{keyword}\n")
        return self

    def wait_title_contains(self, text: str):
        self.wait.until(EC.title_contains(text))
        return self

    @property
    def title(self):
        return self.driver.title