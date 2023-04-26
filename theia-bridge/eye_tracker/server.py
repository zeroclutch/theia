import asyncio
import threading
import json

from . import config
from . import continuous_calibration

from . import cursor as cur
from . import webpage as web

from websockets import serve

cursor = cur.Cursor()

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

    # Settings
    continuous_calibration_type = 'none' # Either 'none', 'tobii', or 'geometric'

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
            'click': self.on_click,
        }

        self.eyetracker = eyetracker
        self.driver = driver
        self.cursor = cursor

        self.calibration = continuous_calibration.ContinuousCalibration(self.eyetracker, self.continuous_calibration_type)

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
            # print("Received message: " + message)
            handler = self.handlers.get(message)
            
            if self.state == 'calibrate':
                await self.on_calibrate(message, websocket)
            elif(handler):
                await handler(message, websocket)
            else:
                pass
                # TODO: Consider error handling invalid messages


    async def send(self, data, websocket):
        # print("Sending {0}".format(data))
        return await websocket.send(data)

    ### Handlers ###


    async def on_awaiting_calibration(self, message, websocket):
        # Empty node list on nav
        self.cursor.gravity.set_nodes([])

        if self.state == 'ready':
            # If we've already calibrated, go to ready state
            await self.send('ready!', websocket)
        else:
            self.state = 'calibrate'
            self.calibration.start()
            await self.send('calibrate!', websocket)

    async def on_calibrate(self, message, websocket):
        if message == 'ready':
            self.calibration.compute()
            # with open('calibration.bin', 'wb') as f:
            #     f.write(self.eyetracker.retrieve_calibration_data())
            await self.on_ready(message, websocket)
        elif message == 'calibrate':
            self.calibration_state = 0
            await self.send(str(self.calibration_state), websocket)
        else:
            # If the last calibration was successful, do the next one
            message = json.loads(message)
            if self.calibration.add_point(message) is True:
                self.calibration_state += 1
            await self.send(str(self.calibration_state), websocket)

    async def on_ready(self, message, websocket):
        # Register and update nodes
        self.cursor.gravity.set_nodes(web.get_nodes(self.driver))

        if self.cursor.get_new_pos() is not None:
            self.state = 'ready'
            await self.send('ready!', websocket)
        else:
            await self.send('not ready!', websocket)
    
    async def on_get(self, message, websocket):
        (cursor_pos, cursor_state) = self.get_cursor_data()
        
        if self.cursor.should_click():
            # self.click(cursor_pos)
            pass

        await self.send(json.dumps([cursor_pos, cursor_state]), websocket)

    async def on_click(self, message, websocket):
        (cursor_pos, cursor_state) = self.get_cursor_data()
        self.click(cursor_pos)
        await self.send("{}", websocket)
    
    ### End handlers ###
    def get_cursor_data(self):
        cursor_pos = None
        cursor_state = self.cursor.get_new_state()

        if cursor_state == cur.CURSOR_FIXATION:
            cursor_pos = self.cursor.get_adjusted_pos()
        else:
            cursor_pos = self.cursor.get_new_pos() 
        
        return (cursor_pos, cursor_state)

    def click(self, cursor_pos):
        print(f"Should be clicking! {cursor_pos[0]} {cursor_pos[1]}")

        # Perform click actions
        web.click(self.driver, cursor_pos[0], cursor_pos[1])

        # Update nodes on click
        self.cursor.gravity.set_nodes(web.get_nodes(self.driver))

        if self.continuous_calibration_type == 'tobii':
            # Calibrate a single point
            self.calibration.start()
            self.calibration.add_point({
                'x': cursor_pos[0],
                'y': cursor_pos[1]
            }) 
            current_calibration = self.calibration.get_current()
            # TODO: This is not removing old points. This might be ok for short testing but we should figure that out.
            compute_thread = threading.Thread(target=self.calibration.compute)
            compute_thread.daemon = True
            compute_thread.start()
        elif self.continuous_calibration_type == 'geometric':
            # Use correction matrix
            pass
        else:
            # No form of continuous calibration (for testing)
            pass

    # A function that is called every time there is new gaze data to be read.
    def gaze_data_callback(self, gaze_data):
        if(self.cursor is not None):
            self.cursor.update(gaze_data)
            
        
    def stop(self):
        self.stop_signal.set_result(True)
        self.t.join()
