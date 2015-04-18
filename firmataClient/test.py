from firmataClient import firmataClient
import time

# Parameters
LED_PIN = 9
DELAY = 0.5

# Main program
def main():

	firmata = firmataClient('/dev/ttyMFD1')
	firmata.pinMode(LED_PIN, firmataClient.MODE_OUTPUT)
	
	while 1:
		firmata.pinMode(LED_PIN, firmataClient.MODE_OUTPUT)
		firmata.digitalWrite(LED_PIN, 1)
		time.sleep(DELAY)
		firmata.digitalWrite(LED_PIN, 0)
		time.sleep(DELAY)
		firmata.pinMode(LED_PIN, firmataClient.MODE_PWM)
		firmata.analogWrite(LED_PIN, 10)
		time.sleep(DELAY)
		firmata.analogWrite(LED_PIN, 0)
		time.sleep(DELAY)

main()
