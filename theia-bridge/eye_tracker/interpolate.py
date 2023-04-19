import numpy as np
from scipy.interpolate import RegularGridInterpolator
from eye_tracker.data.points import x,y

class Interpolator:
    H_DIM = 9
    W_DIM = 16
    def __init__(self):
        # Standard Deviation classifier
        # For our 16:9 grid, we used the middle 16 columns on a grid width of 18
        # We also used the middle 9 rows on a grid height of 11
        x_axis = [i for i in range(1, self.W_DIM + 1)]
        y_axis = [i for i in range(1, self.H_DIM + 1)]
        self.get_x = RegularGridInterpolator((y_axis, x_axis), x, bounds_error=False, fill_value=None)
        self.get_y = RegularGridInterpolator((y_axis, x_axis), y, bounds_error=False, fill_value=None)

    def get(self, x, y):
        x *= self.W_DIM + 1
        y *= self.H_DIM + 1
        print("Looking at:", x, y)
        return (
            self.get_x(np.array([y, x]))[0],
            self.get_y(np.array([y, x]))[0]
        )
