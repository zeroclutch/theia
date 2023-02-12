import asyncio
import threading

from . import config

from websockets import connect
from websockets import serve
import json

from queue import Queue


class Server:
    latest_gaze_data = None
    t = None
    stop_signal = None

    handlers = {}

    # run server in a separate thread
    def __init__(self):
        t = threading.Thread(target=self.start_server)
        t.daemon = True
        t.start()
        self.t = t

        self.handlers = {
            'ready': self.on_ready,
            'get': self.on_get,
        }

    # Function to be threaded
    def start_server(self):
        print("Starting server on port " + str(config.PORT))
        asyncio.run(self.create_server())

    # Creates the server and awaits the requests
    async def create_server(self):
        self.stop_signal = asyncio.Future()  # create a future to stop the server
        async with serve(self.handle, "localhost", config.PORT):
            await self.stop_signal  # run until stop_signal is set

    # Finds and attaches handlers for the various endpoints
    async def handle(self, websocket):
        async for message in websocket:
            print(message)
            handler = self.handlers.get(message)
            if(handler):
                await handler(websocket)
            else:
                await websocket.send('Unknown message')

    ### Handlers ###
    async def on_ready(self, websocket):
        if self.latest_gaze_data is not None:
            await websocket.send('ready!')
        else:
            await websocket.send('not ready!')
    
    async def on_get(self, websocket):
        await websocket.send(json.dumps(self.latest_gaze_data))

    ### End handlers ###

    # A function that is called every time there is new gaze data to be read.
    def gaze_data_callback(self, gaze_data):
        self.latest_gaze_data = gaze_data
        # Print gaze points of left and right eye
        print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
            gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
            gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))
        
    def stop(self):
        self.stop_signal.set_result(True)
        self.t.join()
