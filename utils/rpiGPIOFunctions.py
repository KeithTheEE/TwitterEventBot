




'''

Keith Murray 
email: kmurrayis@gmail.com


Pin Numbers	RPi.GPIO	Raspberry Pi Name	    BCM2835		USED AS
P1_01		1		    3V3	 
P1_02		2		    5V0	 
P1_03		3		    SDA0			    GPIO0
P1_04		4		    DNC	 
P1_05		5		    SCL0			    GPIO1
P1_06		6		    GND	 				GND
P1_07		7		    GPIO7			    GPIO4
P1_08		8		    TXD			        GPIO14		TXD
P1_09		9		    DNC	 
P1_10		10		    RXD			        GPIO15		RXD
P1_11		11		    GPIO0			    GPIO17	
P1_12		12		    GPIO1			    GPIO18
P1_13		13		    GPIO2		 	    GPIO21
P1_14		14		    DNC	 
P1_15		15		    GPIO3			    GPIO22
P1_16		16		    GPIO4			    GPIO23
P1_17		17		    DNC	 
P1_18		18		    GPIO5			    GPIO24
P1_19		19		    SPI_MOSI		    GPIO10
P1_20		20		    DNC	 
P1_21		21		    SPI_MISO		    GPIO9
P1_22		22		    GPIO6			    GPIO25
P1_23		23		    SPI_SCLK		    GPIO11
P1_24		24		    SPI_CE0_N		    GPIO8
P1_25		25		    DNC	 
P1_26		26		    SPI_CE1_N		    GPIO7
P1_27		27
P1_28		28
P1_29		29
P1_30		30
P1_31		31
P1_32		32
P1_33		33
P1_34		34
P1_35		35
P1_36		36
P1_37		37
P1_38		38
P1_39		39
P1_40		40


pin setup on PI 
	    1   2 
	    3   4
	    5   6  --GND
BUTTON-	7   8  
  VCC--	9  10  
	    11 12  --RED 
YELLOW-	13 14
 BLUE--	15 16  --HEARTBEAT
	    17 18  --GREEN
	    19 20
	    21 22 
	    23 24
	    25 26
        27 28
        29 30
        31 32
        33 34
        35 36
        37 38
        39 40

-  ---  ---   |
|_|USB||USB|__|
-  ---  ---
'''

import time
import os
import logging


try:
    import RPi.GPIO as GPIO
    rPI = True
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup( 12, GPIO.OUT) # RED
    GPIO.setup( 13, GPIO.OUT) # YELLOW
    GPIO.setup( 15, GPIO.OUT) # BLUE
    GPIO.setup( 16, GPIO.OUT) # WHITE
    GPIO.setup( 18, GPIO.OUT) # GREEN
    GPIO.setup( 7, GPIO.IN)   # 
    
    # Setup DIP Switch Inputs

except:
    logging.debug("Could not import RPi.GPIO, Not on the pi")
    rPI = False




def checkHardware():
    return rPI

def ledCycle():
    """
    Runs through each LED on the display to verify its function
    Cycle order should be (right to left) White, Red, Yellow, Blue, 
    Green. The same order they are in the bread board
    Notes
    -----
    This is largely just so I can be sure that the LEDs still work. 
    """
    def blink(pin):
        pinState = False
        for i in range(6):
            pinState = not pinState
            GPIO.output(pin, pinState)
            time.sleep(0.15)
        GPIO.output(pin, False)

    white = 16
    red = 12
    yellow = 13
    blue = 15
    green = 18
    if rPI:
        blink(white)
        blink(red)
        blink(yellow)
        blink(blue)
        blink(green)
    return


def myLED(theLED):
    red = 12
    yellow = 13
    blue = 15
    green = 18
    if rPI == True:
        if theLED == "RED":
            GPIO.output(red, True)
            GPIO.output(yellow, False)
            GPIO.output(blue, False)
            GPIO.output(green, False)
                # Consider running a wifi reconnect script now
                
            #print "RED"
        if theLED == "YELLOW":
            GPIO.output(red, False)
            GPIO.output(yellow, True)
            GPIO.output(blue, False)
            GPIO.output(green, False)
            #print "YELLOW"
        if theLED == "BLUE":
            # Fix this call
            GPIO.output(red, False)
            GPIO.output(yellow, False)
            GPIO.output(blue, True)
            GPIO.output(green, False)
            #print "BLUE"
        if theLED == "EVENT":
            GPIO.output(red, False)
            GPIO.output(yellow, False)
            GPIO.output(green, False)
            GPIO.output(blue, True)
            time.sleep(0.15)
            GPIO.output(blue, False)
            time.sleep(0.15)
            GPIO.output(blue, True)
            time.sleep(0.15)
            GPIO.output(blue, False)
            time.sleep(0.15)
            GPIO.output(blue, True)
            time.sleep(0.15)
            GPIO.output(blue, False)
            time.sleep(0.15)
            GPIO.output(blue, True)
            #print "EVENT"
        if theLED == "SLEEP":
            GPIO.output(red, False)
            GPIO.output(yellow, False)
            GPIO.output(blue, False)
            GPIO.output(green, True)
        if theLED == "KDEPREP":
            GPIO.output(red, False)
            GPIO.output(yellow, True)
            GPIO.output(blue, False)
            GPIO.output(green, True)
                
	    #print "GREEN"
    return

def heartBeat():
    # Toggles an LED to verify the program is running
    # Lets the pi run without owner needing a monitor 
    logging.debug("in heartBeat Function")
    while True:
        if rPI:
            GPIO.output(16, True)
            # print "BEAT"
        time.sleep(1)
        if rPI:
            GPIO.output(16, False)
        time.sleep(1)
    return
	    
def buttonListener(testing=False):
    red = 12
    yellow = 13
    blue = 15
    green = 18
    # For restart and shutdown
    # This is super inelegant. But I think it'll work so there we go
    if rPI:
        oldState = GPIO.input(7)
    buttonPress = False
    longHoldDuration = 7
    while True:
        if rPI:
            curState = GPIO.input(7)
            
            if curState != oldState:
                # Debounce
                time.sleep(0.003)
                if curState != oldState:
                    if buttonPress == True:
                        buttonPress = False
                        duration = time.time() - startTime
                        if duration <= 7:	
                            GPIO.output(yellow, True)
                            time.sleep(.1)
                            if testing:
                                print("Short Hold")
                                return
                            else:
                                os.system("sudo reboot")
                    else:		
                        buttonPress = True
                oldState = curState
                startTime = time.time()
                #print startTime
                # Turn on "I'm responding" LED Combo
                GPIO.output(green, True)
                GPIO.output(blue, True)
            time.sleep(.001)
            if buttonPress:
                duration = time.time() - startTime
                if duration > longHoldDuration:
                    # Shutdown condition
                    GPIO.output(red, True)
                    time.sleep(.1)
                    GPIO.output(red, False)
                    time.sleep(.1)
                    GPIO.output(red, True)
                    time.sleep(.5)
                    if testing:
                        print("Long Hold")
                        return
                    else:
                        os.system("sudo shutdown -h now")
    return
	
	

def verifyPinConnections():
    """
    Runs through each LED on the display to verify its function
    Cycle order should be (right to left) White, Red, Yellow, Blue, 
    Green. The same order they are in the perf board

    Notes
    -----
    This is largely just so I can be sure that the LEDs still work. 
    """
    def blink(pin):
        pinState = False
        for i in range(6):
            pinState = not pinState
            GPIO.output(pin, pinState)
            time.sleep(0.15)
        GPIO.output(pin, False)

    white = 16
    red = 12
    yellow = 13
    blue = 15
    green = 18
    blink(white)
    blink(red)
    blink(yellow)
    blink(blue)
    blink(green)

    print("Quickly Press the button")
    buttonListener(testing=True)
    print("Hold the button for a bit")
    buttonListener(testing=True)
    print("All tests concluded")
    
    GPIO.output(12, False)
    GPIO.output(13, False)
    GPIO.output(15, False)
    GPIO.output(16, False)
    GPIO.output(18, False)
    return



if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup( 12, GPIO.OUT)
    GPIO.setup( 13, GPIO.OUT)
    GPIO.setup( 15, GPIO.OUT)
    GPIO.setup( 16, GPIO.OUT)
    GPIO.setup( 18, GPIO.OUT)
    GPIO.setup( 7, GPIO.IN)
    try:
        verifyPinConnections()
    except:
        GPIO.output(12, False)
        GPIO.output(13, False)
        GPIO.output(15, False)
        GPIO.output(16, False)
        GPIO.output(18, False)
        
