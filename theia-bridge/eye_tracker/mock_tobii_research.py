# Dummy functions for Apple Silicon systems (not supported by Tobii)

ScreenBasedCalibration = {
    "find_all_eyetrackers": lambda: None,
    "enter_calibration_mode": lambda: None,
    "collect_data": lambda: None,
    "leave_calibration_mode": lambda: None,
    "compute_and_apply": lambda: None,
}

eyetracker = {
    "subscribe_to": lambda: None,
    "unsubscribe_from": lambda: None,
    "address": "mock",
    "model": "mock",
    "device_name": "mock",
    "serial_number": "mock",
}

def find_all_eyetrackers():
    return [eyetracker]