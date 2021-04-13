from tkinter import *
from src.EnemyFrame import EnemyFrame
from src.FriendlyFrame import FriendlyFrame

class Game:
    def __init__(self, window):
        global MACHINE
        self.window = window
        self.shotFrame = EnemyFrame(window, self)
        self.shipFrame = FriendlyFrame(window)
        
        if MACHINE == "HOST":
            self.socket, self.connection, self.client_addr = self.setupHostNetcode()
        else:
            self.socket = self.setupClientNetcode()
        self.startGameLoop()
    
    # Sets up netcode for host machine
    def setupHostNetcode(self):
        # get current IPv4
        print("Getting current IPv4...", end=' ')
        SERVER_IP = self.getLocalIP()
        print(f'DONE\n\tIPv4 : {SERVER_IP}')

        # create TCP socket on port 10000 bound to IPv4
        print("Creating TCP Socket on port 10000...", end=' ')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((SERVER_IP, 10000))
        print("ESTABLISHED")

        # wait for connection
        print("Waiting for connection attempt by client pi...", end=' ')
        s.listen(1)
        connection, client_addr = s.accept()
        print("CONNECTED\n")

        # return the socket, connection, and client address
        return s, connection, client_addr

    # Sets up the netcode for client machine
    def setupClientNetcode(self):
        # Ask for input of host IPv4
        SERVER_IP = input("Please enter the IPv4 of host machine: ")
        # Confirm the provided IPv4
        confirm = input("IPv4 Recieved : " + SERVER_IP + "\nIs this correct? (y/n)")
        while confirm.lower() != 'y':
            print("You have canceled the previous entry.")
            confirm = input("Please enter the IPv4 of the host machine: ")
        print("IPv4 Confirmed by User. Continuing...")
        #
        # Create a socket object and connect to the host ip on port 10000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, 10000))

        # return the socket
        return s
    
    # Used to obtain the machine's IPv4
    def getLocalIP(self):
        return subprocess.check_output(['hostname', '--all-ip-addresses']).decode().strip()

    # Sends the location of the cell to shoot to the other machine    
    def sendMove(self, coord):
        global myTurn, turnShotCounter, MACHINE
        # send the location of the cell to shoot
        if MACHINE == "HOST":
            self.connection.sendall(str.encode(f'{coord[0]},{coord[1]}'))
            cellStatus = self.connection.recv(10).decode()
        else:
            self.socket.sendall(str.encode(f'{coord[0]},{coord[1]}'))
            cellStatus = self.socket.recv(10).decode()

        # determine hit or miss on cell
        if cellStatus == 'hit':
            return True
        else:
            return False
        
    # Receives the location of the cell to shoot and returns a hit or miss to the other machine
    def recvMove(self):
        print("receiving")
        global myTurn, MACHINE
        # split the incoming coord into x and y
        if MACHINE == "HOST":
            cellLoc = [int(x) for x in self.connection.recv(10).decode().split(',')]
        else:
            cellLoc = [int(x) for x in self.socket.recv(10).decode().split(',')]
        
        # Check if the chosen cell contains a hit or miss
        if self.shipFrame.shipMap[cellLoc[0]][cellLoc[1]] == 'o':
            if MACHINE == "HOST":
                self.connection.sendall(str.encode('hit'))
            else:
                self.socket.sendall(str.encode('hit'))
            self.shipFrame.hitCell(cellLoc[0], cellLoc[1])
        else:
            if MACHINE == "HOST":
                self.connection.sendall(str.encode('miss'))
            else:
                self.socket.sendall(str.encode('miss'))
        self.shipFrame.shipMap[cellLoc[0]][cellLoc[1]] = 'x'

    # Checks for loss    
    def checkForLoss(self):
        numOfShipSpaces = 0
        for i in range(len(self.shipFrame.shipMap)-1):
            for j in range(len(self.shipFrame.shipMap[0])-1):
                if self.shipFrame.shipMap[i][j] == 'o':
                    numOfShipSpaces += 1

        if numOfShipSpaces == 0:
            return True
        return False

    # Resets the game
    def reset(self):
        # Destroy the current frames
        self.shipFrame.destroy()
        self.shotFrame.destroy()
        # Replace the destroyed frames with new ones
        self.shotFrame = EnemyFrame(self.window, self)
        self.shipFrame = FriendlyFrame(self.window)

    # Starts the game loop instead of tk.mainloop()
    def startGameLoop(self):
        global myTurn, MACHINE
        firstStart = True if MACHINE == "CLIENT" else False
        # Start the game loop
        while True:
            if not myTurn:
                if not firstStart:
                    # listen for loss or continue signal
                    if MACHINE == "HOST":
                        gameStatus = self.connection.recv(10).decode()
                    else:
                        gameStatus = self.socket.recv(10).decode()
                    
                    #show win or continue
                    if gameStatus == 'loss':
                        print("You Win!")
                        exit(0)

                # Player gets 5 shots per round
                for i in range(5):
                    self.recvMove()

                # Send loss or continue signal
                if MACHINE == "HOST":
                    if self.checkForLoss():
                        self.connection.sendall(str.encode('loss'))
                        print("You Lose!")
                        exit(1)
                    else:
                        self.connection.sendall(str.encode('continue'))

                else:
                    if self.checkForLoss():
                        self.socket.sendall(str.encode('loss'))
                        print("You Lose!")
                        exit(1)
                    else:
                        self.socket.sendall(str.encode('continue'))
                myTurn = True
            firstStart = False

            # update the tkinter window and display changes
            self.window.update_idletasks()