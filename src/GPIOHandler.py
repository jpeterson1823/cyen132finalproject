import RPi.GPIO as gpio
from time import sleep
from threading import Thread
import logging
import IC2_LCD_driver.py

# Handles all GPIO input and output.
class GPIOHandler:
    def __init__(self):
        # Set class logger
        self.log = logging.getLogger("GPIOHandler")
        logging.getLogger("GPIOHandler").setLevel(logging.INFO)
        
        # Create flags checked by Game Class
        self.exitFlag = False
        self.startFlag = False
        self.shootFlag = False
        self.resetFlag = False
        self.forfeitFlag = False

        # Create button update thread
        self.buttonThread = Thread(target=self.__updateButtonStates)

        # Create counter to be updated by Game class
        self.shotCounter = 0
        # Set up GPIO
        self.__setupGPIO()


    # Sets up GPIO stuffs
    def __setupGPIO(self):
        # Define LED pins
        self.shotLEDs = [20, 21, 22]
        self.warnLights = 23
        # Define button pins
        self.start   =  24
        self.reset   =  25
        self.shoot   =  26
        self.forfeit = 27
        
        # Setting GPIO mode
        gpio.setmode(gpio.BCM)
        self.log.info("Set GPIO mode to BCM.")
        # Set led pins output
        gpio.setup([20, 21, 22, 23], gpio.OUT)
        # Set button pins to input
        gpio.setup([24, 25, 26, 27], gpio.IN)


    # Checks if any buttons are being pressed
    def __updateButtonStates(self):
        while self.exitFlag == False:
            if gpio.input(self.start) == gpio.HIGH:
                print("START")
                self.startFlag = True
            else:
                self.startFlag = False

            if gpio.input(self.shoot) == gpio.HIGH:
                print("SHOOT")
                self.shootFlag = True
            else:
                self.shootFlag = False

            if gpio.input(self.reset) == gpio.HIGH:
                print("RESET")
                self.resetFlag = True
            else:
                self.resetFlag = False
                
            if gpio.input(self.forfeit) == gpio.HIGH:
                print("FORFEIT")
                self.forfeitFlag = True
            else:
                self.forfeitFlag = False
        self.log.critical("Exit flag raised.")
        sleep(0.25)


    # Flashes the warning LEDs
    def __flashWarning(self):
        delay = 0.0625
        for i in range(10):
            gpio.output(self.warnLights, gpio.HIGH)
            sleep(delay)
            gpio.output(self.warnLights, gpio.LOW)
            sleep(delay)


    # Updates the shot selection LEDs' status
    def __updateShotLEDs(self):
        # Check if LEDs should be turned off
        if self.shotCounter == 0:
            for pin in self.shotLEDs:
                gpio.output(pin, gpio.LOW)
        # Turns necessary LEDs on
        for i in range(self.shotCounter):
            gpio.output(self.shotCounter[i], gpio.HIGH)


    # Creates a thread and flashes the warning LEDs
    def displayWarning(self):
        warnThread = Thread(target=self.__flashWarning)
        warnThread.start()


    # Updates the shot counter
    def updateShotCounter(self):
        if self.shotCounter < 3:
            self.log.info("Incremented shotCounter.")
            self.shotCounter += 1
        else:
            self.log.error("Attempted to increment shotCounter but cannot: Already at max.")
        
        # Turn on necessary LEDs
        self.__updateShotLEDs()
