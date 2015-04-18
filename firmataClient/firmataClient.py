#! /usr/bin/env python

"""firmataClient - A python class to interface with an Arduino running firmata
Author: Shawn Hymel @ SparkFun Electronics
Date: April 18, 2015

Based on the Firmata Client by Jim Lindblom.

Distributed as-is; no warranty is given.
"""

import serial

class firmataClient:
	
	# Modes
	MODE_INPUT = 0
	MODE_OUTPUT = 1
	MODE_ANALOG = 2
	MODE_PWM = 3
	MODE_SERVO = 4
	MODE_SHIFT = 5
	MODE_I2C = 6

	# Message Types
	ANALOG_MESSAGE = 0xE0
	DIGITAL_MESSAGE = 0x90
	REPORT_ANALOG = 0xC0
	REPORT_DIGITAL = 0xD0
	START_SYSEX = 0xF0
	SET_PIN_MODE = 0xF4
	END_SYSEX = 0xF7
	REPORT_VERSION = 0xF9
	SYSTEM_RESET = 0xFF

	def __init__(self, serial_port):
		self.ser = serial.Serial(serial_port, 57600, timeout=0.02)
		
	# Turn on reporting for the pin and set the desired mode
	def pinMode(self, pin, mode):
		self.ser.write(chr(self.REPORT_DIGITAL | pin) + chr(1))
		self.ser.write(chr(self.SET_PIN_MODE) + chr(pin) + chr(mode))

	# Write a digital value to a pin
	def digitalWrite(self, pin, value):
		port = (pin >> 3) & 0x0F
		data = 0
	
		if value:
			data |= (1 << (pin & 0x07))
		else:
			data &= ~(1 << (pin & 0x07))

		self.ser.write(chr(self.DIGITAL_MESSAGE | port) + \
			chr(data & 0x7F) + chr(data >> 7))

	# Write PWM (analog) value to a pin
	def analogWrite(self, pin, value):
		self.ser.write(chr(self.ANALOG_MESSAGE | (pin & 0x0F)) + \
				chr(value & 0x7F) + chr(value >> 7))
