from . import selenium

def init():
    driver = selenium.getDriver()
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    