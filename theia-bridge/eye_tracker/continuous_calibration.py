from . import calibration

class ContinuousCalibration:
    MAX_POINTS = 5 # Accuracy vs speed trade-off

    def __init__(self, eyetracker):
        self.eyetracker = eyetracker

        self.calibrations = [None] * self.MAX_POINTS
        self.calibration_points = 0

        for i in range(self.MAX_POINTS):
            self.calibrations[i] = calibration.create_calibration(eyetracker)
        
        self.calibrations[0].enter_calibration_mode()
            


    def get_current(self):
        return self.calibrations[0]
    
    def start(self):
        calibration.start_calibration(self.eyetracker)

    def compute(self):
        calibration.end_calibration(self.get_current())

    # We should generally not call this
    def stop(self):
        self.get_current().leave_calibration_mode()
        print("Left calibration mode for eye tracker.")

    def add_point(self, point):
        success = True

        print("Adding a point, number {0}".format(self.calibration_points))
        for i in range(0, self.calibration_points):
            # if any one fails, we consider it a failure
            success = success and calibration.calibrate(self.calibrations[i], point)
        
        # Update number of points collected
        if self.calibration_points < self.MAX_POINTS:
            self.calibration_points += 1
        else:
            # Shift
            self.shift_calibrations()

        return success


    def shift_calibrations(self):
        self.calibrations = self.calibrations[1:] + [calibration.create_calibration(self.eyetracker)]
        print(self.calibrations)

# Test case
if __name__ == "__main__":
    import calibration

    eyetracker = calibration.init()
    cc = ContinuousCalibration(eyetracker)
    pos = {'x': 0.5, 'y': 0.5}
    cc.start()
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.add_point(pos)
    cc.end()