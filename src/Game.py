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
        window.protocol("WM_DELETE_WINDOW", self.closeGame)

        # Store window in class member variable
        self.window = window

        # Start setup
        self.setup()

    
    # Sets up the game. Handles creating the connection between
    #   the machine and game loop setup
    def setup(self, resetting=False):
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
        if not resetting:
            self.nethandler = NetworkHandler(self, machineType="host", resetting=resetting)
            self.log.info("Created network handler.")
        else:
            self.log.info("Resetting, skipped network handler setup...")

        # Create GPIO handler
        if not resetting:
            self.gpioHandler = GPIOHandler()
            self.log.info("Created GPIO handler.")
        else:
            self.log.info("Resetting, skipped gpio handler setup...")

        # Establish connection to other machine
        if not resetting:
            if self.nethandler.connect():
                self.log.info("Connection established to other machine.")
            else:
                self.log.error("Failed to establish connection to other machine.")
        else:
            self.log.info("Resetting, skipped nethandler connection step...")

        # Update window to display frames
        self.window.update_idletasks()
        self.window.update() 

        if not resetting:
            # Start threads
            self.log.info("Starting game loop thread...")
            self.gameLoopThread.start()
            self.log.info("Starting listen loop thread...")
            self.nethandler.listenThread.start()
            self.gpioHandler.buttonThread.start()
            self.log.info("Started buttonThread.")
        else:
            self.log.info("Resetting, starting threads...")
            self.restartThreads()
            self.nethandler.restartThreads()
            self.gpioHandler.restartThreads()


    # Restarts the classes threads
    def restartThreads(self):
        self.gameLoopThread = threading.Thread(target=self.loop)
        self.gameLoopThread.start()
    
    # Kills all threads by activating exit flags
    def closeGame(self):
        self.log.info("Executed closeGame()")
        self.exitFlag = True
        self.nethandler.exitFlag = True
        self.gpioHandler.exitFlag = True
        self.nethandler.osock.close()
        self.nethandler.isock.close()
        if self.nethandler.machineType == 'host':
            self.nethandler.oconnection.close()
            self.nethandler.iconnection.close()


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
            self.exitFlag = True
            self.gpioHandler.writeToLCD("ENEMY DESTROIED!")
            self.gpioHandler.writeToLCD("    YOU WIN!", 2)
            sleep(1)
            self.endGame()
        elif data == "FORFEIT":
            self.exitFlag = True
            self.gpioHandler.writeToLCD("OPPONENT FORFEIT")
            self.gpioHandler.writeToLCD("    YOU WIN!", 2)
            sleep(1)
            self.endGame()
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
        self.gpioHandler.writeToLCD('Ending Game...')
        self.log.info("Press restart button to continue.")
        self.gpioHandler.writeToLCD("Press RESTART to")
        self.gpioHandler.writeToLCD("   play again!", 2)
        while self.gpioHandler.resetFlag == False:
            pass
        self.__reset()

    def __reset(self):
        self.gpioHandler.writeToLCD("RESTARTING...")
        self.exitFlag = True
        self.nethandler.exitFlag = True
        self.gpioHandler.exitFlag = True
        self.log.info("Sleeping for 2 sec...")
        sleep(2)
        self.enemyFrame.destroy()
        self.friendlyFrame.destroy()
        sleep(2)

        self.log.info("Resetting flags")
        self.exitFlag = False
        self.nethandler.exitFlag = False
        self.gpioHandler.exitFlag = False

        self.log.info("Starting game setup again")
        self.setup(resetting=True)


    # Checks the exitFlag and exits
    def checkExitFlag(self):
        if self.exitFlag:
            self.log.critical("Exit flag has been raised.")
            exit(0)
        
    # Checks the GPIO forfeit flag's status and acts accordingly
    def checkForfeit(self):
        if self.gpioHandler.forfeitFlag == True:
            self.nethandler.strsend("FORFEIT|")
            self.gpioHandler.writeToLCD("YOU FORFEIT")
            self.endGame()
            exit(0)

    # General game loop
    def loop(self):
        while True:
            # Check for win or lose condition
            self.checkWin()
            # Check for exit command
            self.checkExitFlag()
            # Check for forfeit button
            self.checkForfeit()

            # Enable player input for shots
            self.enemyFrame.enableInput()
            self.log.info("Enabled enemyFrame player input.")
            self.gpioHandler.writeToLCD("SELECT TARGETS")

            # Wait until player has chosen their 3 shots
            while self.enemyFrame.ready == False:
                # Check for exit command
                self.checkExitFlag()
                self.checkWin()
                self.checkForfeit()
                # Update shot status leds
                self.gpioHandler.updateShotLEDs(len(self.enemyFrame.desiredShots))

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
            
            self.gpioHandler.writeToLCD(" CANNONS ARMED")
            self.gpioHandler.writeToLCD("Fire when ready", 2)
            self.log.info("Waiting on shoot button press...")
            # while the user has not pressed the shoot button
            while self.gpioHandler.shootFlag == False:
                self.checkExitFlag()
                self.checkWin()
                self.checkForfeit()

            # Reset shot status LEDs
            self.gpioHandler.updateShotLEDs(0)

            # Set machine ready flag
            if self.nethandler.machineType == "host":
                self.hostReadyFlag = True
            else:
                self.clientReadyFlag = True
            self.log.info("Set current machine's ready flag.")

            self.nethandler.strsend("READY_UP|")

            
            #Wait for other machine to be ready
            self.log.info("Waiting for other machine's ready flag...")
            if self.nethandler.machineType == "host":
                while self.clientReadyFlag == False:
                    self.checkWin()
                    self.checkExitFlag()
                    self.checkForfeit()
            else:
                while self.hostReadyFlag == False:
                    self.checkWin()
                    self.checkExitFlag()
                    self.checkForfeit()
            self.log.info("Received ready flag from other machine")

            # Reset ready flags
            self.clientReadyFlag = False
            self.hostReadyFlag = False

            # Send coords to other machine
            self.nethandler.strsend(datastr)
            self.log.info("Sent coord data string to other machine.")

            # Activate warning LEDs
            self.gpioHandler.displayWarning()
            self.gpioHandler.writeToLCD("INCOMING FIRE!")
