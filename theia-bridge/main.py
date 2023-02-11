import eye_tracker.datastream as ds
from eye_tracker.server import Server
import browser.webpage as web
import time

# Initialize software
server = Server()
# server.init()
driver = web.init()
ds.init(server.gaze_data_callback)

time.sleep(1000)
