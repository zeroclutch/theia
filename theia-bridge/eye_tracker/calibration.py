try:
    import tobii_research as tr
except ImportError:
    print("Warning! Tobii Research Python SDK not found. Please install it with `pip install tobii_research`. Using mock eye tracker instead.")
    from . import mock_tobii_research as tr
import time
import sys

def init():
    eyetracker = get_eyetracker()
    return eyetracker

def get_eyetracker():
    found_eyetrackers = tr.find_all_eyetrackers()

    # Skip on macOS
    if(sys.platform == "darwin"):
        return found_eyetrackers[0]

    # Find eye tracker
    eyetracker = found_eyetrackers[0]
    print("Address: " + eyetracker.address)
    print("Model: " + eyetracker.model)
    print("Name: " + eyetracker.device_name)
    print("Serial number: " + eyetracker.serial_number)

    return eyetracker

def start_calibration(eyetracker):
    calibration = tr.ScreenBasedCalibration(eyetracker)
    calibration.enter_calibration_mode()
    return calibration

def calibrate(calibration, point):
    if(sys.platform == "darwin"):
        return True

    print("Entered calibration mode for eye tracker.")
    print("Show a point on screen at {0}.".format(point))

    time.sleep(0.5)

    print("Collecting data at {0}.".format(point))

    calibration_success = None
    
    for _ in range(0, 2):
        if calibration.collect_data(point.get('x'), point.get('y')) == tr.CALIBRATION_STATUS_SUCCESS:
            calibration_success = True
            print("Collected data at {0}.".format(point))
        else:
            calibration_success = False
            print("Failed to collect data at {0}.".format(point))
    
    print("Calibration result: {0}.".format(calibration_success))
    
    print("Computing and applying calibration.")
    calibration_result = calibration.compute_and_apply()
    print("Compute and apply returned {0} and collected at {1} point.".
          format(calibration_result.status, len(calibration_result.calibration_points)))
    
    return calibration_success

def end_calibration(calibration):
    calibration.leave_calibration_mode()
    print("Left calibration mode for eye tracker.")


# via https://developer.tobiipro.com/tobii.research/python/reference/1.10.2.17-alpha-g85317f98/classtobii__research_1_1ScreenBasedCalibration.html
def default_calibrate(eyetracker):

    # Perform calibration
    calibration = tr.ScreenBasedCalibration(eyetracker)
    
    # Enter calibration mode.
    calibration.enter_calibration_mode()
    print("Entered calibration mode for eye tracker with serial number {0}.".format(eyetracker.serial_number))
    
    # Define the points on screen we should calibrate at.
    # The coordinates are normalized, i.e. (0.0, 0.0) is the upper left corner and (1.0, 1.0) is the lower right corner.
    points_to_calibrate = [(0.5, 0.5), (0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9)]
    
    for point in points_to_calibrate:
        print("Show a point on screen at {0}.".format(point))
    
        # Wait a little for user to focus.
        time.sleep(0.7)
    
        print("Collecting data at {0}.".format(point))
        if calibration.collect_data(point[0], point[1]) != tr.CALIBRATION_STATUS_SUCCESS:
            # Try again if it didn't go well the first time.
            # Not all eye tracker models will fail at this point, but instead fail on ComputeAndApply.
            calibration.collect_data(point[0], point[1])
    
    print("Computing and applying calibration.")
    calibration_result = calibration.compute_and_apply()
    print("Compute and apply returned {0} and collected at {1} point.".
          format(calibration_result.status, len(calibration_result.calibration_points)))
    
    # Analyze the data and maybe remove points that weren't good.
    recalibrate_point = (0.1, 0.1)
    print("Removing calibration point at {0}.".format(recalibrate_point))
    calibration.discard_data(recalibrate_point[0], recalibrate_point[1])
    
    # Redo collection at the discarded point
    print("Show a point on screen at {0}.".format(recalibrate_point))
    calibration.collect_data(recalibrate_point[0], recalibrate_point[1])
    
    # Compute and apply again.
    print("Computing and applying calibration.")
    calibration_result = calibration.compute_and_apply()
    print("Compute and apply returned {0} and collected at {1} points.".
          format(calibration_result.status, len(calibration_result.calibration_points)))
    
    # See that you're happy with the result.
    
    # The calibration is done. Leave calibration mode.
    calibration.leave_calibration_mode()
    
    print("Left calibration mode.")
