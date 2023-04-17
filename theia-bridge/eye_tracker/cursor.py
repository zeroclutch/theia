# Implements the cursor repositioning using the gravitational model

import math
import time
import numpy

from scipy.interpolate import RegularGridInterpolator

from . import gravity as g

gravity = g.Gravity()

# States
CURSOR_FIXATION = 1
CURSOR_SACCADE = 0

# nodes = [] # node list for clickable elements
# consider a more useful structure like a graph
class Cursor:
    buffer = []
    buffer_index = -1

    std_x_buffer = []
    std_y_buffer = []

    w, h = 16, 9
    mat_y = 0
    mat_x = 0
    done = False

    last_cursor_pos = []
    
    MAX_BUFFER_SIZE = 10 # can modify
    BUFFER_DURATION = MAX_BUFFER_SIZE / 60 # 60Hz

    WEIGHTED_AVG_FACTOR = 0.8 # can modify
    OLD_COEFFICIENT = 1 - WEIGHTED_AVG_FACTOR / (MAX_BUFFER_SIZE - 1)
    LATEST_COEFFICIENT = 1 + WEIGHTED_AVG_FACTOR

    MAX_STD_X = 0.0
    MAX_STD_Y = 0.0
    MAX_DIST = 0.1

    # Clicking
    CLICK_TIMEOUT = 1500
    CLICK_DELAY = 1000
    # CLICK_TIMEOUT = 0
    # CLICK_DELAY = 100
    fixation_start = None
    last_click = None

    state = CURSOR_SACCADE

    gravity = None

    def __init__(self):
        self.buffer = [None] * self.MAX_BUFFER_SIZE
        self.gravity = gravity

        # Calibration stuff
        self.std_x_matrix = [[0 for x in range(self.w)] for y in range(self.h)] 
        self.std_y_matrix = [[0 for x in range(self.w)] for y in range(self.h)] 

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
        self.last_cursor_pos = self.buffer[self.buffer_index]
        return self.last_cursor_pos
    
    def get_adjusted_pos(self):
        self.last_cursor_pos = self.gravity.apply_gravity(self.last_cursor_pos)
        return self.last_cursor_pos
    
    def dist(self, a, b):
        return math.sqrt( math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2) )

    def get_new_state(self):
        count = self.MAX_BUFFER_SIZE
        max = (self.buffer_index + (count - 1)) % self.MAX_BUFFER_SIZE
        i = self.buffer_index

        # Find the standard deviation of the last 5 points
        sum_x = 0
        sum_y = 0

        # If we are too far from the target point, cancel the fixation
        if self.dist(self.buffer[i], self.last_cursor_pos) > self.MAX_DIST:
            return CURSOR_SACCADE
            
        while i != max:
            # Weighted average/std dev
            # Care more about recent values
            # coefficient = self.OLD_COEFFICIENT
            # if i == self.buffer_index:
            #     coefficient = self.LATEST_COEFFICIENT

            x, y = self.buffer[i]

            # Add coefficients
            # x *= coefficient
            # y *= coefficient

            # Calculate mean and std dev
            sum_x += x
            sum_y += y
            i += 1
            i %= self.MAX_BUFFER_SIZE
        
        mean_x = sum_x / count
        mean_y = sum_y / count

        var_x = 0
        var_y = 0

        # Make another pass to calculate std dev
        i = self.buffer_index
        while i != max:
            x, y = self.buffer[i]

            var_x += (x - mean_x) ** 2
            var_y += (y - mean_y) ** 2

            i += 1
            i %= self.MAX_BUFFER_SIZE

        std_x = math.sqrt(var_x / count)
        std_y = math.sqrt(var_y / count)

        print(std_x)
        
        if not math.isnan(std_x):
            self.std_x_buffer.append(std_x)
        if not math.isnan(std_y):
            self.std_y_buffer.append(std_y)
        
        if(len(self.std_x_buffer) > 120):
            input(f"Look at the coordinates ({self.mat_x+1}, {self.mat_y+1}). Hit enter when you're looking at it. Then stare at it for 2 seconds. ")

            self.mat_x += 1
            if self.mat_x == len(self.std_x_matrix[self.mat_y]):
                self.mat_x = 0
                self.mat_y += 1

                if self.mat_y == len(self.std_x_matrix):
                    print("done!")
                    print(self.std_x_matrix)
                    print(self.std_y_matrix)
                    print("Copy the two arrays above and save them.")
                    self.done = True
                
            # Remove the first 10 values of the buffers
            del self.std_x_buffer[:10]
            del self.std_y_buffer[:10]
            
            self.std_x_matrix[self.mat_y][self.mat_x] = numpy.average(a=self.std_x_buffer)
            self.std_y_matrix[self.mat_y][self.mat_x] = numpy.average(a=self.std_y_buffer)
            
            self.std_x_buffer = []
            self.std_y_buffer = []
            
        
        # print("std_x: {0}, std_y: {1}".format(std_x, std_y))

        # If the standard deviation is too high, the cursor is moving too fast
        if std_x < self.MAX_STD_X or std_y < self.MAX_STD_Y:
            self.state = CURSOR_FIXATION
        else:
            self.state = CURSOR_SACCADE

        return self.state
    
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



