try:
    import tobii_research as tr
except ImportError:
    print("Warning! Tobii Research Python SDK not found. Please install it with `pip install tobii_research`. Using mock eye tracker instead.")
    from . import mock_tobii_research as tr
import time
import sys
import csv

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

def create_calibration(eyetracker):
    calibration = tr.ScreenBasedCalibration(eyetracker)
    return calibration

def start_calibration(eyetracker):
    calibration = create_calibration(eyetracker)
    return calibration

def calibrate(calibration, point):
    if(sys.platform == "darwin"):
        return True
    print("Show a point on screen at {0}.".format(point))

    time.sleep(0.3)

    print("Collecting data at {0}.".format(point))

    calibration_success = None
    
    for _ in range(0, 1):
        if calibration.collect_data(point.get('x'), point.get('y')) == tr.CALIBRATION_STATUS_SUCCESS:
            calibration_success = True
            print("Collected data at {0}.".format(point))
        else:
            calibration_success = False
            print("Failed to collect data at {0}.".format(point))
    
    print("Calibration result: {0}.".format(calibration_success))
    
    return calibration_success

def end_calibration(calibration):
    # calibration.compute_and_apply()
    print("Computing and applying calibration.")
    calibration_result = calibration.compute_and_apply()
    print("Compute and apply returned {0} and collected at {1} point.".
          format(calibration_result.status, len(calibration_result.calibration_points)))
    # print("Left calibration mode for eye tracker.")
    # calibration.leave_calibration_mode()

gaze_data_samples = []

# via https://developer.tobiipro.com/tobii.research/python/reference/1.11.1.1-alpha-gca866d08/calibration_during_gaze_recording_8py-example.html
def save_gaze_data(gaze_samples_list):
     if not gaze_samples_list:
         print("No gaze samples were collected. Skipping saving")
         return
     # To show what kinds of data are available in each sample's dictionary,
     # we print the available keys here.
     print("Sample dictionary keys:", gaze_samples_list[0].keys())
     # This is meant to serve as a simple example of how you can save
     # some of the gaze data - check the keys to see what else is available.
     file_handle = open("my_gaze_data.csv", "w")
     gaze_writer = csv.writer(file_handle)
     gaze_writer.writerow(["time_seconds", "left_x", "left_y", "right_x", "right_y"])
     start_time = gaze_samples_list[0]["system_time_stamp"]
     for recording_dict in gaze_samples_list:
         sample_time_from_start = recording_dict["system_time_stamp"] - start_time
         # convert from microseconds to seconds
         sample_time_from_start = sample_time_from_start / (10**(6))
         # x is horizontal coordinate on the screen
         # y is vertical coordinate on the screen
         left_x, left_y  = recording_dict["left_gaze_point_on_display_area"]
         right_x, right_y = recording_dict["right_gaze_point_on_display_area"]
         gaze_writer.writerow(
             [sample_time_from_start, left_x, left_y, right_x, right_y]
         )
     file_handle.close()


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
