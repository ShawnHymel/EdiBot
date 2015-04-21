import signal
import sys
import time
import SimpleCV
from firmataClient import firmataClient

# Parameters
DEBUG = 1
SPEED = 50
COLOR = SimpleCV.Color.RED
CAMERA_WIDTH = 160
CAMERA_HEIGHT = 120
MIN_BLOB_SIZE = 20
MIN_AREA = 1500
MAX_AREA = 3000

# Pins
CH1_PWM_PIN = 3
CH1_DIR_PIN = 2
CH2_PWM_PIN = 9
CH2_DIR_PIN = 4
CH3_PWM_PIN = 11
CH3_DIR_PIN = 6
CH4_PWM_PIN = 10
CH4_DIR_PIN = 5

# Global variables
firmata = firmataClient('/dev/ttyMFD1')

##############################################################################
# Functions
##############################################################################

def signalHandler(signal, frame):
	if DEBUG:
		print("Exiting...")
	sys.exit(0)

def initPins():
	firmata.pinMode(CH1_PWM_PIN, firmata.MODE_PWM)
	firmata.pinMode(CH1_DIR_PIN, firmata.MODE_OUTPUT)
	firmata.pinMode(CH2_PWM_PIN, firmata.MODE_PWM)
	firmata.pinMode(CH2_DIR_PIN, firmata.MODE_OUTPUT)
	firmata.pinMode(CH3_PWM_PIN, firmata.MODE_PWM)
	firmata.pinMode(CH3_DIR_PIN, firmata.MODE_OUTPUT)
	firmata.pinMode(CH4_PWM_PIN, firmata.MODE_PWM)
	firmata.pinMode(CH4_DIR_PIN, firmata.MODE_OUTPUT)

def stopDriving():
	firmata.digitalWrite(CH1_DIR_PIN, 0)
	firmata.digitalWrite(CH2_DIR_PIN, 0)
	firmata.digitalWrite(CH3_DIR_PIN, 0)
	firmata.digitalWrite(CH4_DIR_PIN, 0)
	firmata.analogWrite(CH1_PWM_PIN, 0)
	firmata.analogWrite(CH2_PWM_PIN, 0)
	firmata.analogWrite(CH3_PWM_PIN, 0)
	firmata.analogWrite(CH4_PWM_PIN, 0)

def driveForward(speed):
	firmata.digitalWrite(CH1_DIR_PIN, 0)
	firmata.digitalWrite(CH2_DIR_PIN, 0)
	firmata.digitalWrite(CH3_DIR_PIN, 1)
	firmata.digitalWrite(CH4_DIR_PIN, 1)
	firmata.analogWrite(CH1_PWM_PIN, speed)
	firmata.analogWrite(CH2_PWM_PIN, speed)
	firmata.analogWrite(CH3_PWM_PIN, speed)
	firmata.analogWrite(CH4_PWM_PIN, speed)

def driveBackward(speed):
	firmata.digitalWrite(CH1_DIR_PIN, 1)
	firmata.digitalWrite(CH2_DIR_PIN, 1)
	firmata.digitalWrite(CH3_DIR_PIN, 0)
	firmata.digitalWrite(CH4_DIR_PIN, 0)
	firmata.analogWrite(CH1_PWM_PIN, speed)
	firmata.analogWrite(CH2_PWM_PIN, speed)
	firmata.analogWrite(CH3_PWM_PIN, speed)
	firmata.analogWrite(CH4_PWM_PIN, speed)

def forwardLeft(speed):
	firmata.digitalWrite(CH1_DIR_PIN, 0)
	firmata.digitalWrite(CH2_DIR_PIN, 0)
	firmata.digitalWrite(CH3_DIR_PIN, 1)
	firmata.digitalWrite(CH4_DIR_PIN, 1)
	firmata.analogWrite(CH1_PWM_PIN, speed)
	firmata.analogWrite(CH2_PWM_PIN, 0)
	firmata.analogWrite(CH3_PWM_PIN, speed)
	firmata.analogWrite(CH4_PWM_PIN, 0)

def forwardRight(speed):
	firmata.digitalWrite(CH1_DIR_PIN, 0)
	firmata.digitalWrite(CH2_DIR_PIN, 0)
	firmata.digitalWrite(CH3_DIR_PIN, 1)
	firmata.digitalWrite(CH4_DIR_PIN, 1)
	firmata.analogWrite(CH1_PWM_PIN, 0)
	firmata.analogWrite(CH2_PWM_PIN, speed)
	firmata.analogWrite(CH3_PWM_PIN, 0)
	firmata.analogWrite(CH4_PWM_PIN, speed)

def backwardLeft(speed):
	firmata.digitalWrite(CH1_DIR_PIN, 1)
	firmata.digitalWrite(CH2_DIR_PIN, 1)
	firmata.digitalWrite(CH3_DIR_PIN, 0)
	firmata.digitalWrite(CH4_DIR_PIN, 0)
	firmata.analogWrite(CH1_PWM_PIN, speed)
	firmata.analogWrite(CH2_PWM_PIN, 0)
	firmata.analogWrite(CH3_PWM_PIN, speed)
	firmata.analogWrite(CH4_PWM_PIN, 0)

def backwardRight(speed):
	firmata.digitalWrite(CH1_DIR_PIN, 1)
	firmata.digitalWrite(CH2_DIR_PIN, 1)
	firmata.digitalWrite(CH3_DIR_PIN, 0)
	firmata.digitalWrite(CH4_DIR_PIN, 0)
	firmata.analogWrite(CH1_PWM_PIN, 0)
	firmata.analogWrite(CH2_PWM_PIN, speed)
	firmata.analogWrite(CH3_PWM_PIN, 0)
	firmata.analogWrite(CH4_PWM_PIN, speed)

def spinLeft(speed):
	firmata.digitalWrite(CH1_DIR_PIN, 0)
	firmata.digitalWrite(CH2_DIR_PIN, 1)
	firmata.digitalWrite(CH3_DIR_PIN, 1)
	firmata.digitalWrite(CH4_DIR_PIN, 0)
	firmata.analogWrite(CH1_PWM_PIN, speed)
	firmata.analogWrite(CH2_PWM_PIN, speed)
	firmata.analogWrite(CH3_PWM_PIN, speed)
	firmata.analogWrite(CH4_PWM_PIN, speed)

def spinRight(speed):
	firmata.digitalWrite(CH1_DIR_PIN, 1)
	firmata.digitalWrite(CH2_DIR_PIN, 0)
	firmata.digitalWrite(CH3_DIR_PIN, 0)
	firmata.digitalWrite(CH4_DIR_PIN, 1)
	firmata.analogWrite(CH1_PWM_PIN, speed)
	firmata.analogWrite(CH2_PWM_PIN, speed)
	firmata.analogWrite(CH3_PWM_PIN, speed)
	firmata.analogWrite(CH4_PWM_PIN, speed)

def chaseBlob(cam_w, x, area):
	seg = cam_w / 5
	if 0 <= x < (seg * 1):
		spinLeft(SPEED)
	elif (seg * 1) <= x < (seg * 2):
		if 0 <= area < MIN_AREA:
			forwardLeft(SPEED)
		elif MIN_AREA <= area <= MAX_AREA:
			stopDriving()
		else:
			backwardRight(SPEED)
	elif (seg * 2) <= x < (seg * 3):
		if 0 <= area < MIN_AREA:
			driveForward(SPEED)
		elif MIN_AREA <= area <= MAX_AREA:
			stopDriving()
		else:
			driveBackward(SPEED)
	elif (seg * 3) <= x < (seg * 4):
		if 0 <= area < MIN_AREA:
			forwardRight(SPEED)
		elif MIN_AREA <= area <= MAX_AREA:
			stopDriving()
		else:
			backwardLeft(SPEED)
	elif(seg * 3) <= x <= (seg * 5):
		spinRight(SPEED)

def driveTest():
	driveForward(SPEED)
	time.sleep(1.0)
	driveBackward(SPEED)
	time.sleep(1.0)
	forwardLeft(SPEED)
	time.sleep(1.0)
	forwardRight(SPEED)
	time.sleep(1.0)
	backwardLeft(SPEED)
	time.sleep(1.0)
	backwardRight(SPEED)
	time.sleep(1.0)
	spinLeft(SPEED)
	time.sleep(1.0)
	spinRight(SPEED)
	time.sleep(1.0)
	stopDriving()
	time.sleep(1.0)

##############################################################################
# Main
##############################################################################

def main():

	# Register Ctrl+C
	signal.signal(signal.SIGINT, signalHandler)

	# Setup
	initPins()
	cam = SimpleCV.Camera(0, {"width": CAMERA_WIDTH, \
		"height": CAMERA_HEIGHT})
	cam_w = cam.getProperty("width")
	cam_h = cam.getProperty("height")
	if DEBUG:
		print "Camera online. w=" + `cam_w` + " h=" + `cam_h`

	# Loop
	while True:
		
		# Take a picture and look for blobs
		img = cam.getImage()
		img = img.hueDistance(COLOR).dilate(2)
		img = img.invert().stretch(230, 255)
		blobs = img.findBlobs()
		i = 0
		max_i = 0
		max_area = 0
		max_x = 0

		# Largest blob is always the last in the array
		if blobs:
			if DEBUG:
				print "Blob " + `blobs[-1].coordinates()` + \
					" area=" + `blobs[-1].area()`
			if blobs[-1].area() >= MIN_BLOB_SIZE:
				if DEBUG:
					print "Chasing x=" + \
					`blobs[-1].coordinates()[0]`
				chaseBlob(cam_w, blobs[-1].coordinates()[0], \
					blobs[-1].area())
		else:
			stopDriving()

# Start here
main()
