import sys

import SimpleCV
sys.path.append('/usr/local/lib/i386-linux-gnu/python2.7/site-packages/')
import mraa
import time

# Constants
MOTOR_1_PIN = 45
MOTOR_2_PIN = 32
RIGHT_TREAD_PIN = 20
LEFT_TREAD_PIN = 14

# Create PWM handlers
right_tread = mraa.Pwm(RIGHT_TREAD_PIN)
left_tread = mraa.Pwm(LEFT_TREAD_PIN)

# Setup PWM parameters
right_tread.period_us(700)
right_tread.enable(True)
right_tread.write(0.0)
left_tread.period_us(700)
left_tread.enable(True)
left_tread.write(0.0)

# Create motor direction handlers
motor_1 = mraa.Gpio(MOTOR_1_PIN)
motor_2 = mraa.Gpio(MOTOR_2_PIN)

# Set motor pin direction
motor_1.dir(mraa.DIR_OUT)
motor_2.dir(mraa.DIR_OUT)

def stopDriving():
	right_tread.write(0.0)
	left_tread.write(0.0)

def driveForward():
	motor_1.write(0)
	motor_2.write(0)
	right_tread.write(1.0)
	left_tread.write(1.0)

def driveForwardRight():
	motor_1.write(1)
	motor_2.write(0)
	right_tread.write(0.0)
	left_tread.write(1.0)

def driveForwardLeft():
	motor_1.write(0)
	motor_2.write(1)
	right_tread.write(1.0)
	left_tread.write(0.0)

# Setup
stopDriving()
cam = SimpleCV.Camera(0, {"width": 160, "height": 90})
cam_w = cam.getProperty("width")
cam_h = cam.getProperty("height")
left_section = 60
center_section = 100
right_section = 160

print "Camera online. w=" + `cam_w` + " h=" + `cam_h`

# Loop
while(True):

	# Take a picture and search for red circles. Depending on where the
	# circle is in the frame (x axis), drive toward the red circle
	img = cam.getImage()
	dist = img.hueDistance(SimpleCV.Color.RED).dilate(2)
	segmented = dist.invert().stretch(230, 255)
	blobs = segmented.findBlobs()
	if blobs:
		circles = blobs.filter([b.isCircle(0.2) for b in blobs])
		if circles:
			if 0 <= circles[-1].x < left_section:
				driveForwardLeft()
				time.sleep(0.5)
			elif left_section <= circles[-1].x <= center_section:
				driveForward()
				time.sleep(0.5)
			elif center_section < circles[-1].x <= right_section:
				driveForwardRight()
				time.sleep(0.5)
			else:
				stopDriving()
		else:
			stopDriving()	
	else:
		stopDriving()
