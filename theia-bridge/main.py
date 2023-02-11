import eye_tracker.datastream as ds
from eye_tracker.server import Server
import browser.webpage as web
import asyncio

# Initialize software
async def main():
    async with Server() as server:
        driver = web.init()
        web.navigate(driver, "https://google.com")
        ds.init(server.gaze_data_callback)
        try:
            await asyncio.Future() # run forever
        except KeyboardInterrupt:
            ds.kill(server.gaze_data_callback)
            web.quit(driver)

asyncio.run(main())
