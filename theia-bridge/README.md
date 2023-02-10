# Theia Bridge

Bridging software that connects the three primary components of Theia.

1. Physical eye-tracker
2. Machine learning model
3. Cursor input

This project leverages the [Tobii Pro SDK](https://developer.tobiipro.com/index.html). 

## Software Requirements

Theia Bridge has a number of requirements that need to be fulfilled.

1. The software must be able to connect to the eye-tracker.
2. The software must be able to receive information from the machine learning model.
3. The software must be able to drive the cursor input based on the current eye-tracked position.
4. The software must be able to add new calibration points to the model without interrupting the eye-tracking. 
5. The software must be able to continue driving cursor input while it is minimized or in the background.
6. The software must have a "kill switch" disabling the eye-tracked input.
7. The software may need to collect metrics for testing purposes.
8. The software may need to launch a controlled browser using Puppeteer or Selenium

## Research

Programming decisions that need to be made:

1. Language choice
2. Package type
   1. Will depend on limitations of interacting with the model and controlling the cursor
3. Interface    
   1. The system should have a GUI for initial calibration.
   2. There should be some research to identify a standardized calibration method

# System outline

### Initialization

1. coordinates of webpage -> getBoundingCoordinates
2. display initial calibrations on screen -> displayCalibrations
3. use this information to create a function that translates the web positional coordinate axis to the tobii coordinate axis
4. subscribe to read data and translate to a cursor position (getCursorPosition)

### Loop

5. identify what elements we are looking at (getElementsAtPoint)
6. upon looking at clickable element, get time to click (getTimeToClick)
7. draw shrinking circle on webpage, fixed to a specific point on the object
   1. if user gaze is interrupted from that object, ignore
   2. else, add calibration point and click (x,y)

Based on this workflow, we will need the following modules

1. browser -> draws on the webpage and extracts information from the browser
   1. webapi - deals with webpage stuff
   2. selenium - deals with browser stuff
2. eyetracker
   1. calibration - deals with initial and continuous calibration
   2. datastream - exports and outputs coordinate information, and attaches handlers