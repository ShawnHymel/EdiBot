from firmataClient import firmataClient
import time

# Parameters
LED_PIN = 9
ADC_PIN = 0
DELAY = 0.5

# Main program
def main():

	firmata = firmataClient('/dev/ttyMFD1')
	firmata.pinMode(LED_PIN, firmataClient.MODE_OUTPUT)
	firmata.pinMode(ADC_PIN + 14, firmataClient.MODE_ANALOG)
	
	while 1:
		firmata.pinMode(LED_PIN, firmataClient.MODE_OUTPUT)
		firmata.digitalWrite(LED_PIN, 1)
		val = firmata.analogRead(ADC_PIN)
		val = (3.3 / 1024) * val
		print(val)
		time.sleep(DELAY)
		
		firmata.digitalWrite(LED_PIN, 0)
		val = firmata.analogRead(ADC_PIN)
                val = (3.3 / 1024) * val
                print(val)
		time.sleep(DELAY)
		
		firmata.pinMode(LED_PIN, firmataClient.MODE_PWM)
		firmata.analogWrite(LED_PIN, 10)
		val = firmata.analogRead(ADC_PIN)
                val = (3.3 / 1024) * val
                print(val)
		time.sleep(DELAY)

		firmata.analogWrite(LED_PIN, 0)
		val = firmata.analogRead(ADC_PIN)
                val = (3.3 / 1024) * val
                print(val)
		time.sleep(DELAY)

main()
