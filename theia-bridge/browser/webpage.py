from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def init():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    return driver

def validateDriver(driver):
    if driver is None:
        raise ReferenceError("Invalid selenium driver provided.")

def navigate(driver, url):
    validateDriver(driver)
    driver.get(url)

def getWindowSize(driver):
    validateDriver(driver)
    size = driver.get_window_size()
    print("Window size:")
    print(size)
    return size
