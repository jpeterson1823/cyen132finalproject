from tkinter import *
import logging
import threading
from time import sleep

from EnemyFrame import EnemyFrame
from FriendlyFrame import FriendlyFrame
from GPIOHandler import GPIOHandler
from NetworkHandler import NetworkHandler

# Contains the game loop and handles the network structuring
class Game:
    def __init__(self, window):
        # Create class logger
        self.log = logging.getLogger("Game")
        self.log.setLevel(logging.INFO)

        # Create flags
        self.exitFlag = False
        self.hostReadyFlag = False
        self.clientReadyFlag = False

        # Add Tkinter protocol to stop all parallel threads when closed
        window.protocol("WM_DELETE_WINDOW", self.closeThreads)

        # Store window in class member variable
        self.window = window

        # Start setup
        self.setup()

    
    # Sets up the game. Handles creating the connection between
    #   the machine and game loop setup
    def setup(self):
        self.log.info("Started class setup.")

        # Set constant for shots per turn
        self.SHOTS_PER_TURN = 3

        # Create game loop thread
        self.gameLoopThread = threading.Thread(target=self.loop)
        self.log.info("Created game loop thread.")

        # Create enemy and friendly ship frames
        self.enemyFrame = EnemyFrame(self, self.window)
        self.friendlyFrame = FriendlyFrame(self.window)
        self.log.info("Created enemy and friendly frames.")

        # Create network handler
        self.nethandler = NetworkHandler(self, machineType="host")
        self.log.info("Created network handler.")

        # Create GPIO handler
        self.gpioHandler = GPIOHandler()
        self.log.info("Created GPIO handler.")


        # Establish connection to other machine
        if self.nethandler.connect():
            self.log.info("Connection established to other machine.")
        else:
            self.log.error("Failed to establish connection to other machine.")

        # Update window to display frames
        self.window.update_idletasks()
        self.window.update()
        
        # Start threads
        self.log.info("Starting game loop thread...")
        self.gameLoopThread.start()
        self.log.info("Starting listen loop thread...")
        self.nethandler.listenThread.start()
        self.gpioHandler.buttonThread.start()
        self.log.info("Started buttonThread.")

    
    # Resets the game to the start
    def reset(self):
        self.log.info("Resetting game...")
        self.nethandler.strsend("RESETTING")
        self.endGame()
        self.log.info("Ending game...")
        self.gameLoopThread.join()
        self.log.info("Joined gameloop thread with main.")
        self.nethandler.listenThread.join()
        self.log.info("Joined listening thread thread with main.")
        
        # Reset all frames
        self.enemyFrame.destroy()
        self.friendlyFrame.destroy()
        self.log.info("Destroied Enemy and Friendly frames.")
        
        # Restart Game class setup
        self.setup()

    
    # Kills all threads by activating exit flags
    def closeThreads(self):
        self.log.info("Executed closeThreads()")
        self.exitFlag = True
        self.nethandler.exitFlag = True
        self.gpioHandler.exitFlag = True
        self.gameLoopThread.join()
        self.log.info("Joined game loop thread with main thread.")
        self.nethandler.listenThread.join()
        self.log.info("Joined nethandler listen thread with main...")
        self.gpioHandler.buttonThread.join()
        self.log.info("Joined gpio handler button thread with main...")
        self.window.destroy()
        self.log.info("Destroyed game window.")


    # Sends the desired shot locations to the other machine when it is the player's turn
    def shoot(self, desiredShots):
        # Convert desiredShots from a list of sets (which are the points) to a data string
        datastr = ''
        for shot in desiredShots:
            datastr += f'{shot[0]},{shot[1]};'
        # Remove the trailing ';' and add '|' terminator
        datastr = datastr[0:len(datastr)-1] + '|'


    # Processes game input received from network manager
    def process(self, datastr):
        self.log.info("Processing data...")
        complex_cmd = datastr.split('|')
        for data in complex_cmd:
            if data != '':
                self.__process(data)


    # Processes the received data from the other machine
    def __process(self, data):
        if data == "READY_UP":
            if self.nethandler.machineType == "host":
                print("ready up client")
                self.clientReadyFlag = True
            else:
                print("ready up host")
                self.hostReadyFlag = True
        elif data == "LOSS":
            self.gpioHandler.writeToLCD("YOU HAVE WON!")
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
        self.log.info("Checking hits...")
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
        self.log.info("Set hits if there were any.")
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
            self.gpioHandler.writeToLCD("YOU HAVE LOST")
            self.endGame()

        
    # Used to end the game without causing thread deadlock
    def endGame(self):
        self.log.info("Ending game...")
        self.nethandler.exitFlag = True
        self.exitFlag = True
        self.log.info("All thread exit flags have been raised.")
        self.log.info("Press restart button to continue.")


    # Checks the exitFlag and exits
    def checkExitFlag(self):
        if self.exitFlag:
            self.log.critical("Exit flag has been raised.")
            exit(0)

    # General game loop
    def loop(self):
        while True:
            self.checkWin()
            # Check for exit command
            self.checkExitFlag()

            # Enable player input for shots
            self.enemyFrame.enableInput()
            self.log.info("Enabled enemyFrame player input.")
            self.gpioHandler.writeToLCD("CHOOSE YOUR 3 SHOTS")

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
            self.log.info("Created datastring: " + datastr)

            # Reset EnemyFrame's desiredShots list
            self.enemyFrame.desiredShots = []
            self.log.info("Reset desiredShots.")
            # Disable player input for shots
            self.enemyFrame.disableInput()
            self.enemyFrame.ready = False
            self.log.info("Disabled player input.")

            self.gpioHandler.writeToLCD("PRESS FIRE BUTTON WHEN READY")
            self.log.info("Waiting on shoot button press...")
            # while the user has not pressed the shoot button
            while self.gpioHandler.shootFlag == False:
                self.checkExitFlag()
                self.checkWin()

            # Set machine ready flag
            if self.nethandler.machineType == "host":
                self.hostReadyFlag = True
            else:
                self.clientReadyFlag = True
            self.log.info("Set current machine's ready flag.")

            
            #Wait for other machine to be ready
            self.log.info("Waiting for other machine's ready flag...")
            if self.nethandler.machineType == "host":
                while self.clientReadyFlag == False:
                    self.checkWin()
                    self.checkExitFlag()
            else:
                while self.hostReadyFlag == False:
                    self.checkWin()
                    self.checkExitFlag()
            self.log.info("Received ready flag from other machine")

            # Reset ready flags
            self.clientReadyFlag = False
            self.hostReadyFlag = False

            # Send coords to other machine
            self.nethandler.strsend(datastr)
            self.log.info("Sent coord data string to other machine.")

            # Activate warning LEDs
            self.gpioHandler.displayWarning()
            self.gpioHandler.writeToLCD("INCOMING FIRE!!!")

            # Check for win
            self.checkWin()
