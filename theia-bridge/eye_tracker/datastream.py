import tobii_research as tr
from . import calibration


all_notifications = (tr.EYETRACKER_NOTIFICATION_CONNECTION_LOST)

et = False

def notification_callback(notification, data):
    print("Notification {0} received at time stamp: {1}".format(notification, data.system_time_stamp))

def init(gaze_data_handler):
    et = calibration.init()
    et.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_handler, as_dictionary=True)
    # for notification in all_notifications:
    #     et.subscribe_to(notification,
    #         lambda x, notification=notification: notification_callback(notification, x))
    #     print("Subscribed to {0} for eye tracker with serial number {1}.".format(notification, et.serial_number))

def kill(et, gaze_data_handler):
    if et is None:
        return None
    else:
        et.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_handler)