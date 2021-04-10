from tkinter import *
import socket, subprocess

# Used to switch between the client and host netcode
global MACHINE
MACHINE = 'HOST'
#MACHINE = 'CLIENT'

# Host will go first
global myTurn
myTurn = False

# Used to count how many shots has been taken
# Helps determine the current turn
global turnShotCounter
turnShotCounter = 0

# Shows all shots taken by the player and if they were a hit or miss
class ShotFrame(Frame):
    def __init__(self, parent, game):
        Frame.__init__(self, parent, bg="green", width=500, height=500)
        parent.attributes('-fullscreen', False)
        self.game = game
        self.setup()
       
    # Sets up the shot frame
    def setup(self):
        # Load and resize all images to 50x50 pixels
        RESCALE_MODIFIER = 10
        self.TILE_IMG = PhotoImage(file="sprites/enemy_tile.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.HIT_IMG = PhotoImage(file="sprites/hit2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.MISS_IMG = PhotoImage(file="sprites/miss2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)

        # initalize grid full of buttons
        self.shotGridButtons = [[Button(self, image=self.TILE_IMG, borderwidth=0, highlightthickness=0,
                                    command=lambda x=col, y=row:self.process(f'{x},{y}')) for row in range(10)] for col in range(10)]

        # initalize grid full of buttons' states
        # 'U' means unknown, 'M' means miss, and 'H' means hit
        self.shotGridStates = [['U' for x in range(10)] for y in range(10)]

        # Add buttons to frame
        for i in range(10):
            for j in range(10):
                self.shotGridButtons[i][j].grid(row=i, column=j, sticky=N+E+S+W)

        # pack the frame
        self.pack(side=LEFT, fill=X, expand=1, anchor=N)

    # Processes the button press of a shot cell and determines if
    # it was a hit or miss
    def process(self, buttonLoc):
        global myTurn, turnShotCounter
        if myTurn:
            print(f"Command recieved from {buttonLoc[0]},{buttonLoc[2]}")
            coord = [int(x) for x in buttonLoc.split(',')]
            # Check if spot is unknown
            if self.shotGridStates[coord[0]][coord[1]] == 'U':
                # Mark cell as known
                self.shotGridStates[coord[0]][coord[1]] = 'K'
                # Send move and get hit or miss back from other pi
                moveResult = self.game.sendMove(coord)
                if moveResult:
                    self.shotGridButtons[coord[0]][coord[1]].configure(image=self.HIT_IMG)
                else:
                    self.shotGridButtons[coord[0]][coord[1]].configure(image=self.MISS_IMG)
                turnShotCounter += 1
                if turnShotCounter == 5:
                    myTurn = False
                    turnShotCounter = 0
            else:
                print("Cell Already Known!")
        else:
            print("YO! It isn't your turn!")


# Shows all friendly ships and if/where they have been hit
class ShipFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg="blue", width=500, height=500)
        parent.attributes("-fullscreen", False)
        self.shipMap = self.getFormattedMap()
        self.setup()
        self.current_ship = "Carrier"
        self.preGame = True
    
    # Sets up the game
    def setup(self):
        # Load and resize all images to 50x50 pixels
        RESCALE_MODIFIER = 10

        # Load Tile Images
        self.TILE_IMG = PhotoImage(file="sprites/friendly_tile.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.HIT_IMG = PhotoImage(file="sprites/hit2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.MISS_IMG = PhotoImage(file="sprites/miss2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)

        # Load Verticle Ship Sprites
        self.SHIP_START_VERTICAL = PhotoImage(file="sprites/ship_start_vertical.png").subsample(2, 2)
        self.SHIP_MID_VERTICAL = PhotoImage(file="sprites/ship_mid_vertical.png").subsample(2, 2)
        self.SHIP_END_VERTICAL = PhotoImage(file="sprites/ship_end_vertical.png").subsample(2, 2)

        # Load Horizontal Ship Sprites
        self.SHIP_START_HORIZONTAL = PhotoImage(file="sprites/ship_start_horizontal.png").subsample(2, 2)
        self.SHIP_MID_HORIZONTAL = PhotoImage(file="sprites/ship_mid_horizontal.png").subsample(2, 2)
        self.SHIP_END_HORIZONTAL = PhotoImage(file="sprites/ship_end_horizontal.png").subsample(2, 2)

        # initalize grid full of buttons
        self.shipGridButtons = [[Button(self, image=self.TILE_IMG, borderwidth=0, highlightthickness=0,
                                    command=lambda x=col, y=row:self.process(x, y)) for row in range(10)] for col in range(10)]
        
        # Add buttons to frame
        for i in range(10):
            print(f"placing row {i} ship buttons")
            for j in range(10):
                self.shipGridButtons[i][j].grid(row=i, column=j, sticky=N+E+S+W)

        # create map for placing ships
        shipMap = self.placeShips()

        # Pack frame
        self.pack(side=RIGHT, fill=X, expand=1, anchor=E)
        return shipMap
    
    # Loads the premade map
    def getFormattedMap(self):
        rawMap = open("testmaps/a.map").readlines()
        formattedMap = []
        for line in rawMap:
            row = []
            for cell in line:
                row.append(cell)
            formattedMap.append(row)
        return formattedMap

    # Places all the ship tiles based on a premade map
    def placeShips(self):
        for row in range(len(self.shipMap)):
            for cell in range(len(self.shipMap)):
                if self.shipMap[row][cell] == 'o':
                    self.shipGridButtons[row][cell].configure(image=self.determineCellSprite(row, cell))

    # Determines the sprite of the current cell
    def determineCellSprite(self, row, cell):
        above = self.checkCellAbove(row, cell)
        below = self.checkCellBelow(row, cell)
        right = self.checkCellRight(row, cell)
        left = self.checkCellLeft(row, cell)

        if above and below:
            return self.SHIP_MID_VERTICAL
        elif above and not below:
            return self.SHIP_END_VERTICAL
        elif not above and below:
            return self.SHIP_START_VERTICAL

        elif right and left:
            return self.SHIP_MID_HORIZONTAL
        elif right and not left:
            return self.SHIP_START_HORIZONTAL
        else:
            return self.SHIP_END_HORIZONTAL

    # Checks above the cell of a ship pane
    # Used to decide what sprite should be used
    def checkCellAbove(self, row, cell):
        if row != 0:
            # If ship cell has another ship cell above
            if self.shipMap[row-1][cell] == 'o':
                return True
        return False
    
    # Checks below the cell of a ship pane
    # Used to decide what sprite should be used
    def checkCellBelow(self, row, cell):
        if row != 9:
            if self.shipMap[row+1][cell] == 'o':
                return True
        return False
    
    # Checks to the right of a cell ship pane
    # Used to decide what sprite should be used
    def checkCellRight(self, row, cell):
        if cell != 9:
            if self.shipMap[row][cell+1] == 'o':
                return True
        return False
    
    # Checks to the left for a cell ship pane
    # Used to decide what sprite should be used
    def checkCellLeft(self, row, cell):
        if cell != 0:
            if self.shipMap[row][cell-1] == 'o':
                return True
        return False

    # Changes the sprite of the cell to hit
    def hitCell(self, x, y):
        self.shipGridButtons[x][y].configure(image=self.HIT_IMG)
    
    # Filler Code for processing press of ship buttons
    def process(self, x, y):
        print(f"ShipFrame: ({x},{y})")


class Game:
    def __init__(self, window):
        global MACHINE
        self.window = window
        self.shotFrame = ShotFrame(window, self)
        self.shipFrame = ShipFrame(window)
        
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
        self.shotFrame = ShotFrame(self.window, self)
        self.shipFrame = ShipFrame(self.window)

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
            self.window.update()


def main():
    #create game window
    window = Tk()
    #set title
    window.title("BATTLESHIP: PI EDITION")
    #shotFrame = ShotFrame(window)
    #shipFrame = ShipFrame(window)
    #window.mainloop()

    # Start game
    Game(window)


if __name__ == "__main__":
    main()