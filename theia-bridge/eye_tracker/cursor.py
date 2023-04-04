# Implements the cursor repositioning using the gravitational model

import math

# nodes = [] # node list for clickable elements
# consider a more useful structure like a graph
class Cursor:
    buffer = []
    buffer_index = -1
    
    MAX_BUFFER_SIZE = 30
    BUFFER_DURATION = MAX_BUFFER_SIZE / 60 # 60Hz

    def __init__(self):
        self.buffer = [None] * self.MAX_BUFFER_SIZE

    def update(self, gaze_data):
        self.buffer_index += 1
        if self.buffer_index >= self.MAX_BUFFER_SIZE:
            self.buffer_index = 0

        x = self.avg(gaze_data['left_gaze_point_on_display_area'][0], gaze_data['right_gaze_point_on_display_area'][0])
        y = self.avg(gaze_data['left_gaze_point_on_display_area'][1], gaze_data['right_gaze_point_on_display_area'][1])

        self.buffer[self.buffer_index] = (x, y)

        return self.buffer_index

    def avg (self, a, b):
        return (a + b) / 2

    def get_new_pos(self):
        return self.buffer[self.buffer_index]

    def get_new_state(self):
        count = self.MAX_BUFFER_SIZE
        max = (self.buffer_index + (count - 1)) % self.MAX_BUFFER_SIZE
        i = self.buffer_index

        # Find the standard deviation of the last 5 points
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        while i != max:
            x, y = self.buffer[i]
            sum_x += x
            sum_y += y
            sum_x2 += x ** 2
            sum_y2 += y ** 2
            i += 1
            i %= self.MAX_BUFFER_SIZE
        

        mean_x = sum_x / count
        mean_y = sum_y / count
        std_x = math.sqrt(sum_x2 / count - mean_x ** 2)
        std_y = math.sqrt(sum_y2 / count - mean_y ** 2)

        # print (std_x, std_y)
        # print("std_x: {0}, std_y: {1}".format(std_x, std_y))

        # If the standard deviation is too high, the cursor is moving too fast
        if std_x < 0.1 or std_y < 0.1:
            return 1
        else:
            return 0





