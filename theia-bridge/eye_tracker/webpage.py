from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import exceptions
import os

def init():
    options = webdriver.ChromeOptions()
    extension_path = os.path.join(os.path.dirname(__file__), "..", "browser", "extension.crx")
    options.add_extension(extension_path)
    executable_path = ChromeDriverManager().install()
    print(executable_path)
    driver = webdriver.Chrome(options=options, executable_path=executable_path)
    driver.maximize_window()
    return driver

# Ensures that the driver is ready
def validate_driver(driver):
    if driver is None:
        raise ReferenceError("Invalid selenium driver provided.")

# Travels to a webpage
def navigate(driver, url):
    validate_driver(driver)

    # Navigate
    driver.get(url)

def get_window_size(driver):
    return driver.execute_script("return { width: window.innerWidth, height: window.innerHeight }")

def get_nodes(driver):
    validate_driver(driver)
    # simple method: get all tabbable elements
    
    # elements = driver.find_elements(By.CSS_SELECTOR, ":is(button, input, select, textarea, a, audio[controls], video[controls], details > summary:first-child, details, [contenteditable=true]):not([aria-hidden=true], [aria-expanded=false])")
    # elements = driver.find_elements(By.CSS_SELECTOR, "button, input, select, textarea, a, audio[controls], video[controls], details > summary:first-child, details, [contenteditable=true]")
    nodes = driver.execute_script("""
    return (()=>{
        nodes = []
        for(let el of document.querySelectorAll(":is(button, input, select, textarea, a, audio[controls], video[controls], details > summary:first-child, details, [contenteditable=true]):not([aria-hidden=true], [aria-expanded=false])")) {
            let rect = el.getBoundingClientRect()
            let x = (rect.x + rect.width/2) / window.innerWidth
            let y = (rect.y + rect.height/2) / window.innerHeight
            if(x || y) nodes.push({x,y})
        }
        return nodes
    })();
    """)
    
    # nodes = []
    # # filter information down to size and position
    # for element in elements:
    #     try:
    #         pos_x = (element.rect['x'] + element.rect['width']  / 2) / window['width']
    #         pos_y = (element.rect['y'] + element.rect['height'] / 2) / window['height']
    #         nodes.append({ "x": pos_x, "y": pos_y })
    #     except exceptions.StaleElementReferenceException:
    #         # Don't add the node, but don't error out.
    #         pass
    return nodes


def click(driver, x, y):
    validate_driver(driver)
    elem = driver.find_element(By.TAG_NAME, "body")
    window = get_window_size(driver)
    pos_x = round(x * window['width'])
    pos_y = round(y * window['height'])
    ActionChains(driver, 1).move_to_element_with_offset(elem, round(elem.rect['width'] / 2), round(elem.rect['height'] / 2)).move_by_offset(pos_x, pos_y).click().perform()
    print(f"Clicking at {pos_x}, {pos_y}")

def quit(driver):
    validate_driver(driver)
    driver.quit()