from tkinter import *
import logging
import threading

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

        # Start setup
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
        self.nethandler = NetworkHandler(self, machineType="client")
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


    # Sends the desired shot locations to the other machine when it is the player's turn
    def shoot(self, desiredShots):
        # Convert desiredShots from a list of sets (which are the points) to a data string
        datastr = ''
        for shot in desiredShots:
            datastr += f'{shot[0]},{shot[1]};'
        # Remove the trailing ';'
        datastr = datastr[0:len(datastr)-1]

    # Checks if thread exit command has been given
    def checkExitFlag(self):
        if self.exitFlag:
            logging.info(self.__classStr + "Exit command received. Killing game loop thread...")
            exit(0)

    
    # Processes game input received from network manager
    def processData(self, data):
        logging.info(self.__classStr + "Processing data...")
        if data == "READY_UP":
            if self.nethandler.machineType == "host":
                print("ready up client")
                self.clientReadyFlag = True
            else:
                print("ready up host")
                self.hostReadyFlag = True
        else:
            print("coords and stuffs")
            data = data.replace("READY_UP", "")
            self.hitmiss = self.checkHits(data)
            # TODO: Send hit or miss to other machine
        
    
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

    # TODO: Resets the entire game
    def reset(self):
        logging.info(self.__classStr + "Resetting game...")
        self.closeThreads()
        self.gameLoopThread.join()
        logging.info(self.__classStr + "Joined game-loop thread with main.")
        ## TODO: Rest of reset

    # General game loop
    def loop(self):
        while True:
            # Check for exit command
            self.checkExitFlag()

            # Enable player input for shots
            self.enemyFrame.enableInput()
            logging.info(self.__classStr + "Enabled enemyFrame player input.")

            # Wait until player has chosen their 3 shots
            while self.enemyFrame.ready == False:
                # Check for exit command
                self.checkExitFlag()
            
            # Parse desired shots into transmittable data str
            datastr = ''
            for shot in self.enemyFrame.desiredShots:
                datastr += f'{shot[0]},{shot[1]};'
            # Remove trailing ';' from datastr
            datastr = datastr[:len(datastr)-1]
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

            # Send ready flag to ther machine
            logging.info(self.__classStr + "Sending ready flag to other machine.")
            self.nethandler.strsend("READY_UP")
            
            # Wait for other machine to be ready
            logging.info(self.__classStr + "Waiting for other machine's ready flag...")
            if self.nethandler.machineType == "host":
                while self.clientReadyFlag == False:
                    self.checkExitFlag()
            else:
                while self.hostReadyFlag == False:
                    self.checkExitFlag()
            logging.info(self.__classStr + "Received ready flag from other machine")

            # Reset ready flags
            self.clientReadyFlag = False
            self.hostReadyFlag = False

            # Send coords to other machine
            self.nethandler.strsend(datastr)
            logging.info(self.__classStr + "Sent coord data string to other machine.")
