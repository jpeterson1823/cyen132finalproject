from tkinter import *
import RPi.GPIO as GPIO
import logging
import threading
from time import sleep

from EnemyFrame import EnemyFrame
from FriendlyFrame import FriendlyFrame
from NetworkHandler import NetworkHandler

# Contains the game loop and handles the network structuring
class Game:
    def __init__(self, window):
        # Create exit flag for killing threads
        self.exitFlag = False

        # Create ready flags for determining when to move forward with the game
        self.hostReadyFlag = False
        self.clientReadyFlag = False

        # Add Tkinter protocol to stop all parallel threads when closed
        window.protocol("WM_DELETE_WINDOW", self.closeThreads)
        # String used to preface what class is doing what in the logger
        self.__classStr = 'Game: '

        # Store window in class member variable
        self.window = window

        # GPIO setup
        self.gpioSetup()

        # Start setup
        self.setup()


    # Sets up GPIO stuffs
    def setupGPIO(self):
        # Define button pins
        self.startb   =  24
        self.resetb   =  25
        self.shootb   =  26
        self.forfeitb = 27

        # Define button active states (AS)
        self.startAS   = gpio.HIGH
        self.resetAS   = gpio.HIGH
        self.shootAS   = gpio.HIGH
        self.forfeitAS = gpio.HIGH
        
        # Setting GPIO mode
        gpio.setmode(gpio.BCM)
        logging.info(self.__classStr + "Set GPIO mode.")
        # Set pins to input
        gpio.setup([24, 25, 26, 27], gpio.INPUT)
        logging.info(self.__classStr + "Set button pins to input.")

    
    # Sets up the game. Handles creating the connection between
    #   the machine and game loop setup
    def setup(self):
        logging.info(self.__classStr + "Started class setup.")

        # Set constant for shots per turn
        self.SHOTS_PER_TURN = 3

        # Create game loop thread
        self.gameLoopThread = threading.Thread(target=self.loop)
        logging.info(self.__classStr + "Created game loop thread.")

        # Create enemy and friendly ship frames
        self.enemyFrame = EnemyFrame(self, self.window)
        self.friendlyFrame = FriendlyFrame(self.window)
        logging.info(self.__classStr + "Created enemy and friendly frames.")

        # Create network handler
        self.nethandler = NetworkHandler(self, machineType="host")
        logging.info(self.__classStr + "Created network handler.")

        # Establish connection to other machine
        if self.nethandler.connect():
            logging.info(self.__classStr + "Connection established to other machine.")
        else:
            logging.error("Failed to establish connection to other machine.")

        # Update window to display frames
        self.window.update_idletasks()
        self.window.update()
        
        # Start game loop thread
        logging.info(self.__classStr + "Starting game loop thread...")
        self.gameLoopThread.start()
        logging.info(self.__classStr + "Starting listen loop thread...")
        self.nethandler.listenThread.start()

    
    # Resets the game to the start
    def resetGame(self):
        logging.info(self.__classStr + "Resetting game...")
        self.nethandler.strsend("RESETTING")
        self.endGame()
        logging.info(self.__classStr + "Ending game...")
        self.gameLoopThread.join()
        logging.info(self.__classStr + "Joined gameloop thread with main.")
        self.nethandler.listenThread.join()
        logging.info(self.__classStr + "Joined listening thread thread with main.")
        
        # Reset all frames
        self.enemyFrame.destroy()
        self.friendlyFrame.destroy()
        logging.info(self.__classStr + "Destroied Enemy and Friendly frames.")
        
        # Restart Game class setup
        self.setup()

    
    # Kills all threads by activating exit flags
    def closeThreads(self):
        logging.info(self.__classStr + "Executed closeThreads()")
        self.exitFlag = True
        self.nethandler.exitFlag = True
        self.gameLoopThread.join()
        logging.info(self.__classStr + "Joined game loop thread with main thread.")
        self.nethandler.listenThread.join()
        logging.info(self.__classStr + "Joined nethandler listen thread with main...")
        self.window.destroy()
        logging.info(self.__classStr + "Destroyed game window.")


    # Sends the desired shot locations to the other machine when it is the player's turn
    def shoot(self, desiredShots):
        # Convert desiredShots from a list of sets (which are the points) to a data string
        datastr = ''
        for shot in desiredShots:
            datastr += f'{shot[0]},{shot[1]};'
        # Remove the trailing ';' and add '|' terminator
        datastr = datastr[0:len(datastr)-1] + '|'


    # Checks if thread exit command has been given
    def checkExitFlag(self):
        if self.exitFlag:
            logging.info(self.__classStr + "Exit command received. Killing game loop thread...")
            exit(0)

    
    # Processes game input received from network manager
    def processData(self, datastr):
        logging.info(self.__classStr + "Processing data...")
        complex_cmd = datastr.split('|')
        for data in complex_cmd:
            if data != '':
                self.process(data)


    # Processes the received data from the other machine
    def process(self, data):
        if data == "READY_UP":
            if self.nethandler.machineType == "host":
                print("ready up client")
                self.clientReadyFlag = True
            else:
                print("ready up host")
                self.hostReadyFlag = True
        elif data == "LOSS":
            print("YOU WIN!")
            self.closeThreads()
        elif data[0:3] == "SR:":
            data = data.replace("SR:", "")
            self.showShots(data)
        else:
            print("coords and stuffs")
            data = data.replace("READY_UP", "")
            self.sendShotResults(self.checkHits(data))

    
    # Sends the shot statuses to the other machine
    def sendShotResults(self, hitmiss):
        data = 'SR:'
        # Convert true false list to data str
        for val in hitmiss:
            if val == True:
                data += '1;'
            else:
                data += '0;'
        # Remove trailing ';' and add '|' terminator
        data = data[0:len(data)-1] + '|'
        self.nethandler.strsend(data)

        
    # Checks the friendlyFrame board for a hit and updates the image
    def checkHits(self, data):
        logging.info(self.__classStr + "Checking hits...")
        hitmiss = []
        for coordstr in data.split(";"):
            print(coordstr)
            temp = coordstr.split(',')
            x = int(temp[0])
            y = int(temp[1])
            print(self.friendlyFrame.shipMap[y][x])
            if self.friendlyFrame.shipMap[y][x] != '-':
                print('hit')
                hitmiss.append(True)
                self.friendlyFrame.hitCell(x, y)
            else:
                hitmiss.append(False)
        logging.info(self.__classStr + "Set hits if there were any.")
        return hitmiss


    # Updates the enemyFrame to show if player's shots were a hit or miss
    def showShots(self, data):
        shotCounter = 0
        for status in data.split(';'):
            coord = self.previousDesiredShots[shotCounter]
            if status == '1':
                self.enemyFrame.updateCell(coord[0], coord[1], 1)
            else:
                self.enemyFrame.updateCell(coord[0], coord[1], 0)
            shotCounter += 1


    # Checks if there is a win and acts accordingly
    def checkWin(self):
        counter = 0
        for row in self.friendlyFrame.shipMap:
            for cell in row:
                if cell == 'x':
                    counter += 1
        # If every ship part has been hit
        if counter == 17:
            self.nethandler.strsend("LOSS|")
            print("YOU LOSE!")
            self.endGame()

        
    # Handles the buttons
    def checkButtons(self):
        start   = gpio.input(self.startb)
        reset   = gpio.input(self.resetb)
        shoot   = gpio.input(self.shootb)
        forfeit = gpio.input(self.forfeitb)

        if shoot == self.shootAS:
            logging.info("Shoot button has been pressed.")
            if self.enemyFrame.ready:
                # Send ready flag to ther machine
                logging.info(self.__classStr + "Sending ready flag to other machine.")
                self.nethandler.strsend("READY_UP|")
            else:
                logging.critical("Cannot send ready flag: 3 cells have not been selected")
            # Flip the activated status of button
            self.flipActiveStatus(self.shootAS)

        if reset == self.resetAS:
            self.resetGame()
            logging.critical("Reset button has been pressed.")
            # Flip the activated status of button
            self.flipActiveStatus(self.resetAS)
    

    # Flips the active status of a button
    def flipActiveStatus(self, buttonStatus):
        if buttonStatus == gpio.HIGH:
            buttonStatus = gpio.LOW
        else:
            buttonStatus = gpio.HIGH


    # Used to end the game without causing thread deadlock
    def endGame(self):
        logging.info(self.__classStr + "Ending game...")
        self.nethandler.exitFlag = True
        self.exitFlag = True
        logging.info(self.__classStr + "All thread exit flags have been raised.")
        logging.info(self.__classStr + "Press restart button to continue.")


    # General game loop
    def loop(self):
        while True:
            self.checkWin()
            # Check for exit command
            self.checkExitFlag()

            # Enable player input for shots
            self.enemyFrame.enableInput()
            logging.info(self.__classStr + "Enabled enemyFrame player input.")

            # Wait until player has chosen their 3 shots
            while self.enemyFrame.ready == False:
                # Check for exit command
                self.checkExitFlag()
                self.checkWin()

            self.previousDesiredShots = self.enemyFrame.desiredShots

            # Parse desired shots into transmittable data str
            datastr = ''
            for shot in self.enemyFrame.desiredShots:
                datastr += f'{shot[0]},{shot[1]};'
            # Remove trailing ';' from datastr and add '|' terminator
            datastr = datastr[:len(datastr)-1] + '|'
            logging.info(self.__classStr + "Created datastring: " + datastr)

            # Reset EnemyFrame's desiredShots list
            self.enemyFrame.desiredShots = []
            logging.info(self.__classStr + "Reset desiredShots.")
            # Disable player input for shots
            self.enemyFrame.disableInput()
            self.enemyFrame.ready = False
            logging.info(self.__classStr + "Disabled player input.")

            # Set machine ready flag
            if self.nethandler.machineType == "host":
                self.hostReadyFlag = True
            else:
                self.clientReadyFlag = True
            logging.info(self.__classStr + "Set current machine's ready flag.")

            
            
            # Wait for other machine to be ready
            logging.info(self.__classStr + "Waiting for other machine's ready flag...")
            if self.nethandler.machineType == "host":
                while self.clientReadyFlag == False:
                    self.checkWin()
                    self.checkExitFlag()
            else:
                while self.hostReadyFlag == False:
                    self.checkWin()
                    self.checkExitFlag()
            logging.info(self.__classStr + "Received ready flag from other machine")

            # Reset ready flags
            self.clientReadyFlag = False
            self.hostReadyFlag = False

            # Send coords to other machine
            self.nethandler.strsend(datastr)
            logging.info(self.__classStr + "Sent coord data string to other machine.")

            self.checkWin()
