from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
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
    validate_driver(driver)
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
    if x > 1 or x < 0 or y > 1 or y < 0:
        return 0
    
    try:
        elem = driver.find_element(By.TAG_NAME, "html")
        window = get_window_size(driver)
        
        # Target position
        pos_x = round(x * window['width'])
        pos_y = round(y * window['height'])

        # Offset position
        offset_x = -round(elem.rect['x'] + elem.rect['width']  / 2)
        offset_y = -round(elem.rect['y'] + elem.rect['height'] / 2)

        # print(f"Offset at {offset_x}, {offset_y}")
        # print(f"Clicking at {pos_x}, {pos_y}")

        # ActionChains(driver).move_to_element_with_offset(elem, offset_x, offset_y).move_by_offset(pos_x, pos_y).click().perform()
        action = ActionBuilder(driver, duration=1)
        action.pointer_action.move_to_location(pos_x, pos_y)
        action.pointer_action.click()
        action.perform()
        # print("Clicked!!!!")

        # Continuous calibration
        # Flow: Queue click -> flash element -> log eye values + wait a minimum of 250ms -> perform click -> recompute calibration model
    except:
        raise

def quit(driver):
    validate_driver(driver)
    driver.quit()