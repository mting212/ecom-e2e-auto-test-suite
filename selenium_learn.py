import time
from selenium import webdriver

# 初始化Edge浏览器
driver = webdriver.Edge()
driver.get("https://www.baidu.com/")
# 调用maximize_window方法，使浏览器窗口最大化显示
driver.maximize_window()
# 设置浏览器的窗口位置
driver.set_window_position(1100, 20)
# 设置浏览器的窗口大小
driver.set_window_size(900, 900)
time.sleep(5)
# 获取页面源代码
page_content = driver.page_source
# 打印获取内容
print(page_content)