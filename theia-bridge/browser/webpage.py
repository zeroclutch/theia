from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os

def init():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    return driver

# Ensures that the driver is ready
def validateDriver(driver):
    if driver is None:
        raise ReferenceError("Invalid selenium driver provided.")

# Travels to a webpage
def navigate(driver, url):
    validateDriver(driver)

    # Load scripts
    cursor_script_path = os.path.join(os.path.dirname(__file__), "scripts", "cursor.js")
    cursor_script = open(cursor_script_path, "r").read()

    # Navigate
    driver.get(url)

    # Inject scripts
    driver.execute_script(cursor_script)

def getWindowSize(driver):
    validateDriver(driver)
    size = driver.get_window_size()
    print("Window size:")
    print(size)
    return size
