from tkinter import *
import logging

# Frame that shows where shots have been fired and there status
class EnemyFrame(Frame):
    def __init__(self, game, parent):
        # Used for logger
        self.__classStr = 'EnemyFrame: '

        # Initialize with super constructor
        Frame.__init__(self, parent, bg='green', width=484//2, height=500)
        # Create member variables
        self.game = game
        # Create array used to store player's shots taken on their turn
        self.desiredShots = []
        # Create variable to control when input from player should be recorded
        self.inputEnabled = False
        # Create ready flag and set it to false on creation
        self.ready = False
        # Start GUI setup
        self.setupGUI()

    # Sets up the gui
    def setupGUI(self):
        # Rescales the ../sprites so they are about 23x23 pixels
        RESCALE_MODIFIER = 21
        # Create resized PhotoImage objects
        self.TILE_IMG = PhotoImage(file="../sprites/enemy_tile.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.HIT_IMG = PhotoImage(file="../sprites/hit2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.MISS_IMG = PhotoImage(file="../sprites/miss2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)

        # Create a grid full of buttons
        self.grid = []
        for row in range(10):
            rowList = []
            for col in range(10):
                button = Button(self, image=self.TILE_IMG, borderwidth=0, highlightthickness=0,
                                command=lambda x=col, y=row: self.process(x, y))
                rowList.append(button)
            self.grid.append(rowList)
        
        # Create an array that stores the status of every cell in the grid
        self.statusGrid = [[0 for a in range(10)] for b in range(10)]

        # Add the buttons to the frame
        for i in range(10):
            for j in range(10):
                self.grid[i][j].grid(row=i, column=j, sticky=N+E+S+W)
            
        # Pack the frame
        self.pack(side=LEFT, fill=X, expand=1, anchor=N)
    
    # Enables input to be taken from player
    def enableInput(self):
        self.inputEnabled = True
    
    # Disables input to be taken from player
    def disableInput(self):
        self.inputEnabled = False

    # Sets the ready flag to a status, telling the game class that the player
    #   has given their input.
    def setReady(self, status):
        self.ready = status
    
    # Adds up to 3 shots to an array. Once the maximum amount
    #   of shots have been placed, it then passes the info to
    #   the game class.
    def process(self, x, y):
        if self.inputEnabled:
            if len(self.desiredShots) < self.game.SHOTS_PER_TURN:
                logging.info(self.__classStr + "Recorded desired shot")
                self.desiredShots.append([x,y])
            
            if len(self.desiredShots) == 3:
                # Send ready flag to game
                self.setReady(True)