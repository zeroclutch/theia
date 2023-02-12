import asyncio
import threading
import json

from . import config
from . import calibration

from websockets import serve



class Server:
    # Initialized in __init__
    t = None
    eyetracker = None
    handlers = None
    
    # Initialized in start_server
    latest_gaze_data = None
    stop_signal = None

    # State
    state = 'awaiting_calibration'
    calibration_state = 0

    # run server in a separate thread
    def __init__(self, eyetracker):
        t = threading.Thread(target=self.start_server)
        t.daemon = True
        t.start()
        self.t = t

        self.handlers = {
            'ready': self.on_ready,
            'get': self.on_get,
            'awaiting_calibration': self.on_awaiting_calibration,
            'calibrate': self.on_calibrate,
        }

        self.eyetracker = eyetracker

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
            print("Received message: " + message)
            handler = self.handlers.get(message)
            if(handler):
                await handler(message, websocket)
            else:
                if self.state == 'calibrate':
                    await self.on_calibrate(message, websocket)

    ### Handlers ###

    async def on_awaiting_calibration(self, message, websocket):
        self.state = 'calibrate'
        await websocket.send('calibrate!')

    async def on_calibrate(self, message, websocket):
        if message == 'ready':
            self.state = 'ready'
            self.on_ready(self, websocket)
        elif message == 'calibrate':
            self.calibration_state = 0
            await websocket.send(str(self.calibration_state))
        else:
            # If the last calibration was successful, do the next one
            if calibration.calibrate(self.eyetracker, message) is True:
                self.calibration_state += 1
            await websocket.send(str(self.calibration_state))

    async def on_ready(self, message, websocket):
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
