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

    def start_server(self):
        print("Starting server on port " + str(config.PORT))
        asyncio.run(self.create_server())

    async def create_server(self):
        async with serve(self.handle, "localhost", config.PORT):
            await asyncio.Future()  # run forever

    async def handle(self, websocket):
        async for message in websocket:
            print(message)
            handler = self.handlers.get(message)
            if(handler):
                await handler(websocket)
            else:
                await websocket.send('Unknown message')

    # handlers
    async def on_ready(self, websocket):
        await websocket.send('ready!')
    
    async def on_get(self, websocket):
        await websocket.send(json.dumps(self.latest_gaze_data))

    def gaze_data_callback(self, gaze_data):
        self.latest_gaze_data = gaze_data
        # Print gaze points of left and right eye
        print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
            gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
            gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))
