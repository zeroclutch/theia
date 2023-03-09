from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os

def init():
    options = webdriver.ChromeOptions()
    options.add_extension('./extension.crx')
    ChromeDriverManager().install()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# Ensures that the driver is ready
def validate_driver(driver):
    if driver is None:
        raise ReferenceError("Invalid selenium driver provided.")

# Travels to a webpage
def navigate(driver, url):
    validate_driver(driver)

    # Load scripts
    cursor_script_path = os.path.join(os.path.dirname(__file__), "scripts", "cursor.js")
    cursor_script = open(cursor_script_path, "r").read()

    # Navigate
    driver.get(url)

    # Inject scripts
    driver.execute_script(cursor_script)

def getWindowSize(driver):
    validate_driver(driver)
    size = driver.get_window_size()
    print("Window size:")
    print(size)
    return size

def quit(driver):
    validate_driver(driver)
    driver.quit()