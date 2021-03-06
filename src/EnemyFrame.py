from tkinter import *
from PIL import Image
from PIL import ImageTk
import logging

# Frame that shows where shots have been fired and there status
class EnemyFrame(Frame):
    def __init__(self, game, parent):
        # Create class logger
        self.log = logging.getLogger("EnemyFrame")
        logging.getLogger("EnemyFrame").setLevel(logging.INFO)

        self.parent = parent

        # Initialize with super constructor
        Frame.__init__(self, parent, bg='green', width=400, height=480)
        # Create member variables
        self.game = game
        # Create array used to store player's shots taken on their turn
        self.desiredShots = []
        # Create variable to control when input from player should be recorded
        self.inputEnabled = False
        # Create ready flag and set it to false on creation
        self.ready = False
        # Start GUI setup
        self.__setupGUI()

    # Sets up the gui
    def __setupGUI(self):
        # Rescale sprites so they fit on screen
        #RESCALE_MODIFIER = 14
        width = 38
        height = 46
        # Create resized PhotoImage objects
        #self.TILE_IMG = PhotoImage(file="../sprites/enemy_tile.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        img = Image.open("../sprites/enemy_tile.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.TILE_IMG = ImageTk.PhotoImage(img)

        img = Image.open("../sprites/enemy_tile_selected.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.SELECTED_IMG = ImageTk.PhotoImage(img)

        #self.HIT_IMG = PhotoImage(file="../sprites/hit2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        img = Image.open("../sprites/hit2_enemy.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.HIT_IMG = ImageTk.PhotoImage(img)

        #self.MISS_IMG = PhotoImage(file="../sprites/miss2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        img = Image.open("../sprites/miss2_enemy.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.MISS_IMG = ImageTk.PhotoImage(img)

        # Create a grid full of buttons
        self.grid = []
        for row in range(10):
            rowList = []
            for col in range(10):
                button = Button(self, image=self.TILE_IMG, bd=0,
                        highlightthickness=0, relief=FLAT, bg='black', fg='red',
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
        self.pack(side=LEFT, fill=X, expand=False, anchor=N)
    
    # Enables input to be taken from player
    def enableInput(self):
        self.inputEnabled = True
    
    # Disables input to be taken from player
    def disableInput(self):
        self.inputEnabled = False

    # Adds up to 3 shots to an array. Once the maximum amount
    #   of shots have been placed, it then passes the info to
    #   the game class.
    def process(self, x, y):
        if self.inputEnabled:
            if len(self.desiredShots) < self.game.SHOTS_PER_TURN:
                self.log.info("Recorded desired shot")
                self.desiredShots.append([x,y])
                self.grid[y][x].configure(image=self.SELECTED_IMG)
            
            if len(self.desiredShots) == 3:
                # Send ready flag to game
                self.ready = True
    
    # Updates a cell according to the status
    def updateCell(self, x, y, status):
        if status == 1:
            self.grid[y][x].configure(image=self.HIT_IMG)
        else:
            self.grid[y][x].configure(image=self.MISS_IMG)
        self.parent.update_idletasks()
        self.parent.update()
