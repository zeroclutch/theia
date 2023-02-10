import asyncio
import threading
import random

PORT = 8888

# run server in a separate thread
def init():
    threading.Thread(target=start_server).start()

def start_server():
    print("Starting server")
    asyncio.run(create_server())

async def create_server():
    server = await asyncio.start_server(
        handle_connection,
        None,
        PORT,
    )
    async with server:
        await server.serve_forever()

async def handle_connection(reader, writer):
    print("Someone is connected!")
    while request != 'quit':
        request = (await reader.read(255)).decode('utf8')
        response = str(eval(request)) + '\n'
        writer.write(response.encode('utf8'))
        writer.drain()



def gaze_data_callback(gaze_data):
    # Print gaze points of left and right eye
    if(random() > 0.95):
        print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
            gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
            gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))
