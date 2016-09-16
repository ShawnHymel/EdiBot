# Debugging options
VERBOSE = False
SHOW_IMAGE = False
RUN_MOTORS = True

import subprocess
import signal
import sys
import time
import cv2

# Only import mraa if we have motors turned on
if RUN_MOTORS:
    import mraa

# False: A is right, True: A is left
swapMotors = True

# Motor parameters. Set to 1 or -1 to change default direction
leftDir = 1
rightDir = 1

# Motor speed (between 0.0 and 1.0)
SPEED = 1.0

# Webcam manufacturer
WEBCAM_MAKE = 'Logitech'

# HSV color thresholds for YELLOW
THRESHOLD_LOW = (15, 210, 20);
THRESHOLD_HIGH = (35, 255, 255);

# Robot will move to maintain a blob between these sizes
MIN_SIZE = 30
MAX_SIZE = 40

# Camera resolution
CAMERA_WIDTH = 160
CAMERA_HEIGHT = 120

# Minimum enclosing area (radius) of colored object
MIN_AREA = 1

if RUN_MOTORS:

    # PWM A (pin 12) is on pin 20 in MRAA
    pwmA = mraa.Pwm(20)
    pwmA.period_us(1000)
    pwmA.enable(True)

    # PWM B (pin 13) is on pin 14 in MRAA
    pwmB = mraa.Pwm(14)
    pwmB.period_us(1000)
    pwmB.enable(True)

    # Direction pins A1 and A2 are on GPIO 48 and 47 (33 and 46 in MRAA)
    a1 = mraa.Gpio(33)
    a1.dir(mraa.DIR_OUT)
    a1.write(1)
    a2 = mraa.Gpio(46)
    a2.dir(mraa.DIR_OUT)
    a2.write(1)

    # Direction pins B1 and B2 are on GPIO 15 and 14 (48 and 36 in MRAA)
    b1 = mraa.Gpio(48)
    b1.dir(mraa.DIR_OUT)
    b1.write(1)
    b2 = mraa.Gpio(36)
    b2.dir(mraa.DIR_OUT)
    b2.write(1)

    # Assign left and right motors
    if swapMotors:
        leftPwm = pwmB
        left1 = b1
        left2 = b2
        rightPwm = pwmA
        right1 = a1
        right2 = a2
    else:
        leftPwm = pwmA
        left1 = a1
        left2 = a2
        rightPwm = pwmB
        right1 = b1
        right2 = b2

    # Standby pin is GPIO 49 (47 in MRAA)
    standby = mraa.Gpio(47)
    standby.dir(mraa.DIR_OUT)
    standby.write(1)

###############################################################################
# Functions
###############################################################################

# Exit on a ctrl+c event
def signalHandler(signal, frame):
    if VERBOSE:
        print "Exiting..."
    sys.exit(0)

# Put the motor driver into standby mode
def standby(mode):
    if standby:
        standby.write(0)
    else:
        standby.write(1)

# Differential drive. A and B can be -1 to 1.
def diffDrive(leftSpeed, rightSpeed):

    # Make sure the speeds are within the bounds
    if leftSpeed < -1.0:
        leftSpeed = -1.0
    if leftSpeed > 1.0:
        leftSpeed = 1.0
    if rightSpeed < -1.0:
        rightSpeed = -1.0
    if rightSpeed > 1.0:
        rightSpeed = 1.0

    # Set motor speeds
    leftSpeed = leftDir * leftSpeed
    rightSpeed = rightDir * rightSpeed
    if leftSpeed < 0:
        left1.write(0)
        left2.write(1)
        leftPwm.write(abs(leftSpeed))
    else:
        left1.write(1)
        left2.write(0)
        leftPwm.write(leftSpeed)
    if rightSpeed < 0:
        right1.write(0)
        right2.write(1)
        rightPwm.write(abs(rightSpeed))
    else:
        right1.write(1)
        right2.write(0)
        rightPwm.write(rightSpeed)

# Wait for the webcam to show up in the USB devices list
def waitForCamera():
        while True:

                # Parse the `lsusb` command
                proc = subprocess.Popen(['lsusb'], stdout=subprocess.PIPE)
                out = proc.communicate()[0]
                lines = out.split('\n')

                # Look for the webcam manufacturer
                for line in lines:
                        if WEBCAM_MAKE in line:
                                if VERBOSE:
                                    print "Camera found!"
                                time.sleep(1.0)
                                return
                if VERBOSE:
                    print "Waiting for camera..."
                time.sleep(1.0)

# Find the largest blob of the desired color
def findColor(img):

    # Blur image to remove noise
    img = cv2.GaussianBlur(img, (3, 3), 0)
    
    # Convert image from BGR to HSV
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Set pixels to white if in color range, others to black
    img = cv2.inRange(img, THRESHOLD_LOW, THRESHOLD_HIGH)
    
    # Dilate image to make white blobs larger
    #img = cv2.erode(img, None, iterations = 2)
    img = cv2.dilate(img, None, iterations = 1)

    # Find center of object using contours instead of blob detection. From:
    # http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
    cnts = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    radius = 0
    
    # Find the largest contour and use it to compute the min enclosing circle
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M["m00"] > 0:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius < MIN_AREA:
                center = None

    # Return the keypoint for the largest blob
    return img, center, radius

# React to the blob's position in the frame (turn, back up, etc.)
def chaseBlob(camWidth, x, size):
   
    # Divide the frame up into 3 segments
    seg3 = camWidth / 3

    # If blob is far away, chase it
    if 0 <= size < MIN_SIZE:
        if 0 <= x < (seg3 * 1):
            diffDrive(SPEED, 0.0)
            if VERBOSE:
                print "Forward left"
        elif (seg3 * 1) <= x < (seg3 * 2):
            diffDrive(SPEED, SPEED)
            if VERBOSE:
                print "Forward"
        elif (seg3 * 2) <= x <= (seg3 * 3):
            diffDrive(0.0, SPEED)
            if VERBOSE:
                print "Forward right"

    # If blob is the correct distance away, turn to face it
    elif MIN_SIZE <= size <= MAX_SIZE:
        if 0 <= x < (seg3 * 1):
            diffDrive(SPEED, 0.0)
            if VERBOSE:
                print "Forward left"
        elif (seg3 * 1) <= x < (seg3 * 2):
            diffDrive(0.0, 0.0)
            if VERBOSE:
                print "Stop"
        elif (seg3 * 2) <= x <= (seg3 * 3):
            diffDrive(0.0, SPEED)
            if VERBOSE:
                print "Forward right"

    # If blob is near, face it and back away
    else:
        if 0 <= x < (seg3 * 1):
            diffDrive(0.0, -SPEED)
            if VERBOSE:
                print "Back right"
        elif (seg3 * 1) <= x < (seg3 * 2):
            diffDrive(-SPEED, -SPEED)
            if VERBOSE:
                print "Back"
        elif (seg3 * 2) <= x <= (seg3 * 3):
            diffDrive(-SPEED, 0.0)
            if VERBOSE:
                print "Back left"
        
###############################################################################
# Main
###############################################################################

def main():

    # Register Ctrl+C
    signal.signal(signal.SIGINT, signalHandler)

    # Wait for the webcam to finish initializeing
    waitForCamera()

    # Initialize camera
    cam = cv2.VideoCapture(0)
    cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    camWidth = cam.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    camHeight = cam.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    if VERBOSE:
        print "Camera initialized: (" + str(camWidth) + ", " + \
            str(camHeight) + ")"

    # Main loop
    while True:
    
        # Get image from camera
        ret_val, frame = cam.read()
        
        # Filter the image and find the largest blob
        img, center, radius = findColor(frame)

        # React to the blob: chase if it exists in frame, otherwise stop
        if center != None:
            if RUN_MOTORS:
                chaseBlob(camWidth, center[0], radius)
            if VERBOSE:
                print "(" + str(round(center[0], 2)) + \
                        "," + str(round(center[1], 2)) + ") " + \
                        str(round(radius, 2))
        else:
            if RUN_MOTORS:
                diffDrive(0.0, 0.0)

        # Show image window (if debugging)
        if SHOW_IMAGE:
            #img = cv2.drawKeypoints(img, center)
            cv2.imshow('my webcam', img)
            cv2.waitKey(1) 

if __name__ == "__main__":
    main()
