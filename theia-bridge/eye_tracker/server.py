import asyncio
import threading
import json

from . import config
from . import calibration

from . import cursor as cur
from . import gravity as grav
from . import webpage as web

from websockets import serve

cursor = cur.Cursor()
gravity = grav.Gravity()

# States
CURSOR_FIXATION = 0
CURSOR_SACCADE = 1

class Server:
    # Initialized in __init__
    t = None
    eyetracker = None
    driver = None
    handlers = None
    
    # Initialized in start_server
    latest_gaze_data = None
    cursor = None
    latest_cursor_pos = None
    latest_cursor_state = None # 0: fixation. 1: saccade
    stop_signal = None

    # State
    state = 'awaiting_calibration'
    calibration_state = 0 
    calibration = None

    # run server in a separate thread
    def __init__(self, eyetracker, driver):
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
        self.driver = driver
        self.cursor = cursor
        self.gravity = gravity

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
                    await self.on_calibrate(json.loads(message), websocket)


    async def send(self, data, websocket):
        print("Sending {0}".format(data))
        return await websocket.send(data)

    ### Handlers ###


    async def on_awaiting_calibration(self, message, websocket):
        print(self.state)
        if self.state == 'ready':
            # If we've already calibrated, go to ready state
            await self.send('ready!', websocket)
        else:
            self.state = 'calibrate'
            self.calibration = calibration.start_calibration(self.eyetracker)
            await self.send('calibrate!', websocket)

    async def on_calibrate(self, message, websocket):
        if message == 'ready':
            calibration.end_calibration(self.calibration)
            self.on_ready(self, message, websocket)
        elif message == 'calibrate':
            self.calibration_state = 0
            await self.send(str(self.calibration_state), websocket)
        else:
            # If the last calibration was successful, do the next one
            if calibration.calibrate(self.calibration, message) is True:
                self.calibration_state += 1
            await self.send(str(self.calibration_state), websocket)

    async def on_ready(self, message, websocket):
        # Register and update nodes
        self.gravity.set_nodes(web.get_nodes(self.driver))

        if self.latest_cursor_pos is not None:
            self.state = 'ready'
            await self.send('ready!', websocket)
        else:
            await self.send('not ready!', websocket)
    
    async def on_get(self, message, websocket):
        cursor_pos = self.latest_cursor_pos
        if self.latest_cursor_state == CURSOR_FIXATION:
            # TODO: use gravitational model
            pass
        elif self.latest_cursor_state == CURSOR_SACCADE:
            pass
            # do nothing
        await self.send(json.dumps([cursor_pos, self.latest_cursor_state]), websocket)

    ### End handlers ###

    # A function that is called every time there is new gaze data to be read.
    def gaze_data_callback(self, gaze_data):
        self.latest_gaze_data = gaze_data
        if(self.cursor is not None):
            self.cursor.update(gaze_data)
            self.latest_cursor_pos = self.cursor.get_new_pos()
            self.latest_cursor_state = self.cursor.get_new_state()
        
    def stop(self):
        self.stop_signal.set_result(True)
        self.t.join()
