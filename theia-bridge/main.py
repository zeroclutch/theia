import eye_tracker.datastream as ds
import eye_tracker.server as server
import browser.webpage as web
import time

# Initialize software
server.init()
driver = web.init()
ds.init(server.gaze_data_callback)

time.sleep(10)
