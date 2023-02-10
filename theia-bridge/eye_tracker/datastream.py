import tobii_research as tr
from . import calibration
import time

all_notifications = (tr.EYETRACKER_NOTIFICATION_CONNECTION_LOST)

et = False

def notification_callback(notification, data):
    print("Notification {0} received at time stamp: {1}".format(notification, data.system_time_stamp))

def gaze_data_callback(gaze_data):
    # Print gaze points of left and right eye
    print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
        gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
        gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))

def init():
    et = calibration.init()
    et.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    # for notification in all_notifications:
    #     et.subscribe_to(notification,
    #         lambda x, notification=notification: notification_callback(notification, x))
    #     print("Subscribed to {0} for eye tracker with serial number {1}.".format(notification, et.serial_number))

def kill():
    if et is False:
        return False
    else:
        et.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)