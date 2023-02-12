try:
    import tobii_research as tr
except ImportError:
    print("Warning! Tobii Research Python SDK not found. Please install it with `pip install tobii_research`. Using mock eye tracker instead.")
    from . import mock_tobii_research as tr
from . import calibration

import sys

def init(eyetracker, gaze_data_handler):
    if(sys.platform == "darwin"):
        return True

    eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_handler, as_dictionary=True)

def kill(eyetracker, gaze_data_handler):
    if eyetracker is None:
        return None
    else:
        eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_handler)
        return True
    
def notification_callback(notification, data):
    print("Notification {0} received at time stamp: {1}".format(notification, data.system_time_stamp))

def attach_notifications(eyetracker, all_notifications):
    if(sys.platform == "darwin"):
        return True
    
    for notification in all_notifications:
        eyetracker.subscribe_to(notification,
            lambda x, notification=notification: notification_callback(notification, x))
        print("Subscribed to {0} for eye tracker with serial number {1}.".format(notification, eyetracker.serial_number))