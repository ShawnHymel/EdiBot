import mraa
import time

# Constants
MOTOR_1_PIN = 45
MOTOR_2_PIN = 32
MOTOR_3_PIN = 46
MOTOR_4_PIN = 33
RIGHT_TREAD_PIN = 20
LEFT_TREAD_PIN = 14

# Create PWM handlers
right_tread = mraa.Pwm(RIGHT_TREAD_PIN)
left_tread = mraa.Pwm(LEFT_TREAD_PIN)

# Setup PWM parameters
right_tread.period_us(1000)
right_tread.enable(True)
right_tread.write(0.0)
left_tread.period_us(1000)
left_tread.enable(True)
left_tread.write(0.0)

# Create motor direction handlers
motor_1 = mraa.Gpio(MOTOR_1_PIN)
motor_2 = mraa.Gpio(MOTOR_2_PIN)
motor_3 = mraa.Gpio(MOTOR_3_PIN)
motor_4 = mraa.Gpio(MOTOR_4_PIN)

# Set motor pin direction
motor_1.dir(mraa.DIR_OUT)
motor_2.dir(mraa.DIR_OUT)
motor_3.dir(mraa.DIR_OUT)
motor_4.dir(mraa.DIR_OUT)

def stopDriving():
	right_tread.write(0.0)
	left_tread.write(0.0)

def driveForward():
	motor_1.write(0)
	motor_2.write(0)
	motor_3.write(1)
	motor_4.write(1)
	right_tread.write(1.0)
	left_tread.write(1.0)

def driveBackward():
	motor_1.write(1)
	motor_2.write(1)
	motor_3.write(0)
	motor_4.write(0)
	right_tread.write(1.0)
	left_tread.write(1.0)

def driveForwardRight():
	motor_1.write(1)
	motor_2.write(0)
	motor_3.write(1)
	motor_4.write(1)
	right_tread.write(0.0)
	left_tread.write(1.0)

def driveForwardLeft():
	motor_1.write(0)
	motor_2.write(1)
	motor_3.write(1)
	motor_4.write(1)
	right_tread.write(1.0)
	left_tread.write(0.0)

def turnRight():
	motor_1.write(1)
	motor_2.write(0)
	motor_3.write(0)
	motor_4.write(1)
	right_tread.write(1.0)
	left_tread.write(1.0)

def turnLeft():
	motor_1.write(0)
	motor_2.write(1)
	motor_3.write(1)
	motor_4.write(0)
	right_tread.write(1.0)
	left_tread.write(1.0)

def driveTest():
	stopDriving()
	time.sleep(1.0)
	turnRight()
	time.sleep(1.0)
	driveForwardRight()
	time.sleep(1.0)
	driveForward()
	time.sleep(1.0)
	driveForwardLeft()
	time.sleep(1.0)
	turnLeft()
	time.sleep(1.0)
	driveBackward()
	time.sleep(1.0)

while (True) :
	stopDriving()
	time.sleep(1.0)
	driveForwardRight()
	time.sleep(1.0)
