from tkinter import *
import socket

# Host will go first
global myTurn
myTurn = True

# Shows all shots taken by the player and if they were a hit or miss
class ShotFrame(Frame):
    def __init__(self, parent, game):
        Frame.__init__(self, parent, bg="green", width=500, height=500)
        parent.attributes('-fullscreen', False)
        self.game = game
        self.setup()
       
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

    
    def process(self, buttonLoc):
        global myTurn
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
                # Change turns
                myTurn = False
            else:
                print("Cell Already Known!")
        else:
            print("YO! It isn't your turn!")


# Shows all friendly ships and if/where they have been hit
class ShipFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg="blue", width=500, height=500)
        parent.attributes("-fullscreen", False)
        self.setup()
    
    def setup(self):
        # To Be Implemented
        RESCALE_MODIFIER = 10
        self.TILE_IMG = PhotoImage(file="sprites/friendly_tile.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.HIT_IMG = PhotoImage(file="sprites/hit2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.MISS_IMG = PhotoImage(file="sprites/miss2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)

        # initalize grid full of buttons
        self.shipGridButtons = [[Button(self, image=self.TILE_IMG, borderwidth=0, highlightthickness=0,
                                    command=lambda x=col, y=row:self.process(x, y)) for row in range(10)] for col in range(10)]
        

        # Add buttons to frame
        for i in range(10):
            for j in range(10):
                self.shipGridButtons[i][j].grid(row=i, column=j, sticky=N+E+S+W)

        # create map for placing ships
        self.shipMap = self.placeShips()

        # Pack frame
        self.pack(side=RIGHT, fill=X, expand=1, anchor=E)


class Game:
    def __init__(self, window):
        self.machine = 'Determined in Netcode Setup'
        
        # Make sure not to start panel GUIs before creating socket
        self.socket, self.connection, self.client_addr = self.setupHostNetcode()
        #self.socket = self.setupClientNetcode()
        shotFrame = ShotFrame(window, self)
        shipFrame = ShipFrame(window)
        self.startGameLoop(window)
    

    def setupHostNetcode(self):
        # set the machine to host
        self.machine = 'CLIENT'

        # get current IPv4
        print("Getting current IPv4...", end=' ')
        SERVER_IP = socket.gethostbyname(socket.gethostname())  #Not working on Raspbian for some reason. Need another way
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

    
    def setupClientNetcode(self):
        # set the machine to client
        self.machine = "CLIENT"

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


    # Sends the location of the cell to shoot to the other machine    
    def sendMove(self, coord):
        # send the location of the cell to shoot
        self.socket.sendall(str.encode(f'{coord[0]},{coord[1]}'))
        cellStatus = self.socket.recv(10).decode()

        # determine hit or miss on cell
        if cellStatus == 'hit':
            return True
        else:
            return False


    # Receives the location of the cell to shoot and returns a hit or miss to the other machine
    def recvMove(self):
        global myTurn
        # split the incoming coord into x and y
        cellLoc = [int(x) for x in self.connection.recv(10).decode().split(',')]
        
        # test setups
        if cellLoc[0] == 5 and cellLoc[1] == 0:
            self.connection.sendall(str.encode('hit'))
        elif cellLoc[0] == 5 and cellLoc[1] == 0:
            self.connection.sendall(str.encode('hit'))
        else:
            self.connection.sendall(str.encode('miss'))
        
        # After receiving a coord, it must be your turn.
        myTurn = TRUE


    # Starts the game loop instead of tk.mainloop()
    def startGameLoop(self, window):
        # Create the grids for both game frames
        shotFrame = ShotFrame(window, self)
        shipFrame = ShipFrame(window)

        # Start the game loop
        while True:
            # update the tkinter window and display changes
            window.update_idletasks()
            window.update()


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