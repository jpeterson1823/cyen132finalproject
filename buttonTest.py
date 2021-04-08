import RPi.GPIO as gpio
from time import sleep

# Not yet implemented error
class NotYetImplementedError(Exception):
    def __init__(self, process):
        self.process = process
        self.message = f'\'{process}\' is not yet implemented.'
        Exception.__init__(self.message)


# =====| Logger Class |========================================================================
# | Logs the flow and execution of the program throughout runtime.                            |
# =============================================================================================
class Logger:
    def __init__(self, processName: str, useFile:bool = False, outFile:str = None):
        # Formatting prefix for logger
        self.prefix = f"{processName} Logger: "
        # Create 'useFile' cmv (class member variable)
        self.useFile = useFile
        # Create 'outFile' cmv
        self.outFile = outFile
        self.log(f"Logger for {processName} instantiated.")
    
    # Either prints or writes the desired string with the log prefix.
    def log(self, string: str):
        if self.useFile == False:
            print(self.prefix + string)
        else:
            # TODO: Implement file logging
            raise NotYetImplementedError('File Logging')


# =====| ButtonHandler Class |=================================================================
# | Handles the monitoring of the buttons and their individual status.                        |
# =============================================================================================
class ButtonHandler:
    # Constructor
    def __init__(self, logger):
        # Create 'logger' cmv
        #   Will be called after every major point in the program
        self.logger = logger

        # Store the commands and the corresponding button pin numbers in a dictionary.
        self.buttons = {
                'left' : 17,
                'right': 16,
                'down'   : 13,
                'up' : 12
                }
        # Update logger
        self.logger.log('Buttons have been registered.')

        # Get list of button pins
        pins = list(self.buttons.values())
        # Set up GPIO for button pins
        gpio.setup(pins, gpio.IN, pull_up_down=gpio.PUD_DOWN)

        # Update logger
        self.logger.log('GPIO setup has completed.')

    # Checks the status of the buttons and executes the process command.
    def check(self):
        # Bool used to confirm if command was received or not.
        cmdReceived = False

        # Cycle through the possible commands
        for cmd in self.buttons.keys():
            # If button pressed
            if gpio.input(self.buttons[cmd]) == 1:   
                # Execute command
                self.process(cmd)    
                # Note that command was received
                cmdReceived = True
                # Update logger
                self.logger.log(f"\tButton pressed. Command Received: {cmd}")

        # Return true if cmdReceived, otherwise return False
        return cmdReceived
    
    # Takes a button's pin and executes the coresponding command.
    def process(self, cmd: str):
        # For now, just log the command for verification.
        self.logger.log("\t\t{COMMAND EXECUTION} " + cmd)

###############################################################################################
# Main Code

# Set GPIO type
gpio.setmode(gpio.BCM)

# Create button handler and its logger
buttonHandlerLogger = Logger("ButtonHandler")
buttonHandler = ButtonHandler(buttonHandlerLogger)

# Loop until 5 commands received
cmds = 0
while True:
    if buttonHandler.check():
        cmds += 1
    if cmds == 5:
        break
    sleep(0.25)

# Exit by printing 'Finished' to the console
print("Finished")
