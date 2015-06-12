# Twitch Plays AVC
# Based on https://www.sevadus.tv/forums/index.php?/topic/774-simple-python-irc-bot/
# Shawn Hymel @ SparkFun Electronics
# May 23, 2015

import re
import signal
import time
import socket
import os
import sys
from firmataClient import firmataClient

# Connection parameters. Get oauth at http://www.twitchapps.com/tmi/
HOST = 'irc.twitch.tv'
PORT = 6667
NICK = '<USERNAME>'
OAUTH = 'oauth:<OAUTH>'
STREAM_KEY = "live_<STREAM KEY>"

# Camera parameters
CAMERA = "/dev/video0"
PIX_FMT = "yuv420p"
INRES = "640x480"
OUTRES = "640x480"
FPS = "15"
GOP="30" # i-frame interval, should be double of FPS, 
GOPMIN="15" # min i-frame interval, should be equal to fps, 
THREADS="2" # max 6
CBR="500k" # constant bitrate (should be between 1000k - 3000k)
QUALITY="ultrafast"  # one of the many FFMPEG preset
AUDIO_RATE="44100"
SERVER="live-lax" # twitch server http://twitchstatus.com/

# Messages
HELLO = "Start! Send me 'w', 'a', 's', and 'd' to move me."

# Derived parameters
CHAN = '#' + NICK.lower()

# Parameters
DEBUG = 0
PUSH_TO_START = False
SPEED = 100

# Pins
CH1_PWM_PIN = 3
CH1_DIR_PIN = 2
CH2_PWM_PIN = 9
CH2_DIR_PIN = 4
CH3_PWM_PIN = 11
CH3_DIR_PIN = 6
CH4_PWM_PIN = 10
CH4_DIR_PIN = 5
STATUS_LED_PIN = 7
START_BUTTON_PIN = 0

# Constants
ADC_OFFSET = 14

# Global variables
firmata = firmataClient("/dev/ttyMFD1")

##############################################################################
# IRC Functions
##############################################################################

def sendMessage(msg):

    con.send(bytes(str('PRIVMSG %s :%s\r\n' % \
        (CHAN, msg)).encode('UTF-8')))

def sendNick(nick):
    con.send(bytes(str('NICK %s\r\n' % nick).encode('UTF-8')))

def sendPass(password):
    con.send(bytes(str('PASS %s\r\n' % password).encode('UTF-8')))

def joinChannel(chan):
    con.send(bytes(str('JOIN %s\r\n' % chan).encode('UTF-8')))

def getMessage(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result.lstrip(':')
    return result

##############################################################################
# Drive Fucntions
##############################################################################

def initPins():

    firmata.pinMode(CH1_PWM_PIN, firmata.MODE_PWM)
    firmata.pinMode(CH1_DIR_PIN, firmata.MODE_OUTPUT)
    firmata.pinMode(CH2_PWM_PIN, firmata.MODE_PWM)
    firmata.pinMode(CH2_DIR_PIN, firmata.MODE_OUTPUT)
    firmata.pinMode(CH3_PWM_PIN, firmata.MODE_PWM)
    firmata.pinMode(CH3_DIR_PIN, firmata.MODE_OUTPUT)
    firmata.pinMode(CH4_PWM_PIN, firmata.MODE_PWM)
    firmata.pinMode(CH4_DIR_PIN, firmata.MODE_OUTPUT)
    #firmata.pinMode((VSEN_PIN + ADC_OFFSET), firmata.MODE_ANALOG)
    firmata.pinMode(STATUS_LED_PIN, firmata.MODE_OUTPUT)
    firmata.pinMode(START_BUTTON_PIN, firmata.MODE_ANALOG)

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

##############################################################################
# Other Functions
#############################################################################

# Kill program on Ctrl+C
def signalHandler(signal, frame):
	if DEBUG:
		print "Exiting..."
	sys.exit(0)

##############################################################################
# Main
##############################################################################

# register Ctrl+C
loop = True
signal.signal(signal.SIGINT, signalHandler)

# Initialize pins and status LED
initPins()
if PUSH_TO_START:
    status_led = 0
    firmata.digitalWrite(STATUS_LED_PIN, status_led)

# Set up video stream to Twitch channel
os.system('ffmpeg -f video4linux2 -s "%s" -r "%s" -i %s -f flv -ac 2 \
    -vcodec libx264 -g %s -keyint_min %s -b:v %s -minrate %s -maxrate %s \
    -pix_fmt %s -s %s -preset %s -tune film -threads %s -strict normal \
    -bufsize %s "rtmp://%s.twitch.tv/app/%s" &' \
    % (INRES, FPS, CAMERA, GOP, GOPMIN, CBR, CBR, CBR, PIX_FMT, OUTRES, \
    QUALITY, THREADS, CBR, SERVER, STREAM_KEY))

# Wait for a button push to start taking commands
if PUSH_TO_START:
    wait_loop = True
    while wait_loop:
        if firmata.analogRead(START_BUTTON_PIN) == 0:
            wait_loop = False
        status_led = status_led ^ 1
        firmata.digitalWrite(STATUS_LED_PIN, status_led)
        time.sleep(0.2)
    firmata.digitalWrite(STATUS_LED_PIN, 1)

# Connect to Twitch channel
con = socket.socket()
con.connect((HOST, PORT))
sendPass(OAUTH)
sendNick(NICK)
joinChannel(CHAN)

# Send hello message
sendMessage(HELLO)

# Main loop. Ctrl-C to exit
data = ""
while True:
    try:

        # Look for new messages in the IRC channel
        data += con.recv(1024).decode('UTF-8')
        data_split = re.split(r"[~\r\n]+", data)
        data = data_split.pop()

        # Parse the message
        for line in data_split:
            line = str.rstrip(str(line))
            line = str.split(str(line))

            if len(line) >= 1:

                # Look for w, a, s, or d and drive based on the command
                if line[1] == 'PRIVMSG':
                    message = getMessage(line)
                    if message == 'w ':
                        print "Go forward"
                        driveForward(SPEED)
                        time.sleep(0.5)
                        stopDriving()
                    elif message == 'a ':
                        print "Turn left"
                        spinLeft(SPEED)
                        time.sleep(0.5)
                        stopDriving()
                    elif message == 's ':
                        print "Go backward"
                        driveBackward(SPEED)
                        time.sleep(0.5)
                        stopDriving()
                    elif message == 'd ':
                        print "Turn right"
                        spinRight(SPEED)
                        time.sleep(0.5)
                        stopDriving()

    except socket.error:
        print("Socket died")

    except socket.timeout:
        print("Socket timeout")
