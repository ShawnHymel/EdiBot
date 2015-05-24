# Twitch Listener
# Based on https://www.sevadus.tv/forums/index.php?/topic/774-simple-python-irc-bot/
# Shawn Hymel @ SparkFun Electronics
# May 23, 2015

import os
import re
import time
import socket
from firmataClient import firmataClient

# Connection parameters. Get oauth at http://www.twitchapps.com/tmi/
HOST = 'irc.twitch.tv'
PORT = 6667
NICK = '<USERNAME>'
OAUTH = 'oauth:xxxxxxxxxxxxxxxxxxxxxx'
STREAM_KEY = "live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

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
HELLO = "EdiBot online. Send me 'w', 'a', 's', and 'd' to move me!"

# Derived parameters
CHAN = '#' + NICK.lower()

# Parameters
DEBUG = 0
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
VSEN_PIN = 0
LED_PIN = 8

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
	firmata.pinMode((VSEN_PIN + ADC_OFFSET), firmata.MODE_ANALOG)
	firmata.pinMode(LED_PIN, firmata.MODE_OUTPUT)

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
# Main
##############################################################################

# Set up video stream to Twitch channel
os.system('ffmpeg -f video4linux2 -s "%s" -r "%s" -i %s -f flv -ac 2 \
    -vcodec libx264 -g %s -keyint_min %s -b:v %s -minrate %s -maxrate %s \
    -pix_fmt %s -s %s -preset %s -tune film -threads %s -strict normal \
    -bufsize %s "rtmp://%s.twitch.tv/app/%s" &' \
    % (INRES, FPS, CAMERA, GOP, GOPMIN, CBR, CBR, CBR, PIX_FMT, OUTRES, \
    QUALITY, THREADS, CBR, SERVER, STREAM_KEY))

# Connect to Twitch channel
con = socket.socket()
con.connect((HOST, PORT))
sendPass(OAUTH)
sendNick(NICK)
joinChannel(CHAN)

# Send hello message
sendMessage(HELLO)

# Set up robot pins
initPins()

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
