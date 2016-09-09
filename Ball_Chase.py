import subprocess
import signal
import sys
import time
import mraa
import cv2

# Debugging options
VERBOSE = True
SHOW_IMAGE = False

# Motor parameters. Set to 1 or -1 to change default direction
dirA = -1
dirB = -1

# Motor speed (between 0.0 and 1.0)
SPEED = 1.0

# Webcam manufacturer
WEBCAM_MAKE = 'Logitech'

# HSV color thresholds for YELLOW
THRESHOLD_LOW = (15, 215, 50);
THRESHOLD_HIGH = (35, 255, 255);

# Robot will move to maintain a blob between these sizes
MIN_SIZE = 30
MAX_SIZE = 50

# Camera resolution
CAMERA_WIDTH = 432
CAMERA_HEIGHT = 240

# Blob detector options
detectorParams = cv2.SimpleBlobDetector_Params()
detectorParams.minThreshold = 10
detectorParams.maxThreshold = 200
detectorParams.filterByArea = True
detectorParams.minArea = 40
detectorParams.maxArea = 70000
detectorParams.filterByCircularity = False
detectorParams.minCircularity = 0.1
detectorParams.filterByConvexity = False
detectorParams.minConvexity = 0.5
detectorParams.filterByInertia = False
detectorParams.minInertiaRatio = 0.5
detectorParams.filterByColor = False

# Create global blob detector
detector = cv2.SimpleBlobDetector(detectorParams)

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
def diffDrive(speedA, speedB):

    # Make sure the speeds are within the bounds
    if speedA < -1.0:
        speedA = -1.0
    if speedA > 1.0:
        speedA = 1.0
    if speedB < -1.0:
        speedB = -1.0
    if speedB > 1.0:
        speedB = 1.0

    # Set motor speeds
    speedA = dirA * speedA
    speedB = dirB * speedB
    if speedA < 0:
         a1.write(0)
         a2.write(1)
         pwmA.write(abs(speedA))
    else:
        a1.write(1)
        a2.write(0)
        pwmA.write(speedA)
    if speedB < 0:
        b1.write(0)
        b2.write(1)
        pwmB.write(abs(speedB))
    else:
        b1.write(1)
        b2.write(0)
        pwmB.write(speedB)

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
def findColorBlob(img):

    # Blur image to remove noise
    img = cv2.GaussianBlur(img, (3, 3), 0)
    
    # Convert image from BGR to HSV
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Set pixels to white if in color range, others to black
    img = cv2.inRange(img, THRESHOLD_LOW, THRESHOLD_HIGH)
    
    # Dilate image to make white blobs larger
    img = cv2.dilate(img, None, iterations = 1)
    
    # Find the largest blob
    keypoints = detector.detect(255 - img)
    blob = None
    blobSize = 0
    if keypoints:
        for k in keypoints:
            if k.size > blobSize:
                blob = k
                blobSize = k.size

    # Return the keypoint for the largest blob
    return img, blob

# React to the blob's position in the frame (turn, back up, etc.)
def chaseBlob(camWidth, x, size):
   
    # Divide the frame up into 5 segments
    seg = camWidth / 5

    # If blob is on far left, spin left
    if 0 <= x < (seg * 1):
        diffDrive(SPEED, -SPEED)
        if VERBOSE:
            print "Spin left"

    # If blob is on the left, turn to the left
    elif (seg * 1) <= x < (seg * 2):
        if 0 <= size < MIN_SIZE:
            diffDrive(SPEED, 0.0)
            if VERBOSE:
                print "Forward left"
        elif MIN_SIZE <= size <= MAX_SIZE:
            diffDrive(0.0, 0.0)
            if VERBOSE:
                print "Stop"
        else:
            diffDrive(0.0, -SPEED)
            if VERBOSE:
                print "Back right"

    # If blob is in the center, try to maintain a certain size in the frame
    elif (seg * 2) <= x < (seg * 3):
        if 0 <= size < MIN_SIZE:
            diffDrive(SPEED, SPEED)
            if VERBOSE:
                print "Forward"
        elif MIN_SIZE <= size <= MAX_SIZE:
            diffDrive(0.0, 0.0)
            if VERBOSE:
                print "Stop"
        else:
            diffDrive(-SPEED, -SPEED)
            if VERBOSE:
                print "Back"

    # If blob is on the right, turn to the right
    elif (seg * 3) <= x < (seg * 4):
        if 0 <= size < MIN_SIZE:
            diffDrive(0.0, SPEED)
            if VERBOSE:
                print "Forward right"
        elif MIN_SIZE <= size <= MAX_SIZE:
            diffDrive(0.0, 0.0)
            if VERBOSE:
                print "Stop"
        else:
            diffDrive(-SPEED, 0.0)
            if VERBOSE:
                print "Back left"

    # If blob is on the far right, spin right
    elif (seg * 4) <= x <= (seg * 5):
        diffDrive(-SPEED, SPEED)
        if VERBOSE:
            print "Spin right"

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
        img, blob = findColorBlob(frame)

        # React to the blob
        if blob != None:
            chaseBlob(camWidth, blob.pt[0], blob.size)
            if VERBOSE:
                print "(" + str(round(blob.pt[0], 2)) + \
                        "," + str(round(blob.pt[1], 2)) + ") " + \
                        str(round(blob.size, 2))
        else:
            diffDrive(0.0, 0.0)

        # Show image window (if debugging)
        if SHOW_IMAGE:
            img = cv2.drawKeypoints(img, [blob])
            cv2.imshow('my webcam', img)
            cv2.waitKey(1) 

if __name__ == "__main__":
    main()
