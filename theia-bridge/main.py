import eye_tracker.datastream as ds
from eye_tracker.server import Server
import browser.webpage as web
import asyncio

stop_signal = asyncio.Future()

# Initialize software
async def keep_alive():
    await stop_signal # run until stop_signal is set

def cleanup():
    # Cleanup
    print("[0/3] Keyboard interrupt detected. Exiting...")
    ds.kill(server.gaze_data_callback)
    print("[1/3] Stopped datastream from eye tracker.")
    web.quit(driver)
    print("[2/3] Closed browser.")
    server.stop()
    print("[3/3] Closed websocket server.")

# Initialization
server = Server()
driver = web.init()
web.navigate(driver, "https://google.com")
ds.init(server.gaze_data_callback)

try:
    # Keep alive
    asyncio.get_event_loop().run_until_complete(keep_alive())
except KeyboardInterrupt:
    stop_signal.set_result(True)
    cleanup()
except:
    stop_signal.set_result(True)
    # Cleanup
    cleanup()
    raise
