# Implements the cursor repositioning using the gravitational model

import math
import time

# States
CURSOR_FIXATION = 1
CURSOR_SACCADE = 0

# nodes = [] # node list for clickable elements
# consider a more useful structure like a graph
class Cursor:
    buffer = []
    buffer_index = -1
    
    MAX_BUFFER_SIZE = 30
    BUFFER_DURATION = MAX_BUFFER_SIZE / 60 # 60Hz

    # Clicking
    CLICK_TIMEOUT = 1500
    CLICK_DELAY = 1000
    fixation_start = None
    last_click = None

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
    
    def ms(self):
        return round(time.time() * 1000)

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
            return CURSOR_FIXATION
        else:
            return CURSOR_SACCADE
    
    # Returns true if we should click at the current cursor position
    def should_click(self):
        if self.get_new_state() == CURSOR_FIXATION:
            if self.fixation_start is not None:
                if (self.ms() - self.fixation_start) >= self.CLICK_DELAY:
                    # Warning: this might accidentally click if we lag and don't update the state.
                    self.fixation_start = self.ms() + self.CLICK_TIMEOUT
                    return True
            else:
                self.fixation_start = self.ms()
        else:
            self.fixation_start = None
        return False



