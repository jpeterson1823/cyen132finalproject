from tkinter import *
import logging

# Shows all friendly ships and if/where they have been hit
class FriendlyFrame(Frame):
    def __init__(self, parent):
        self.parent = parent
        # Used for logging
        self.__classStr = 'FriendlyFrame: '
        
        Frame.__init__(self, parent, bg="blue", width=500, height=500)
        parent.attributes("-fullscreen", False)
        self.shipMap = self.getFormattedMap()
        self.setup()
        self.preGame = True
    
    # Sets up the game
    def setup(self):
        # Load and resize all images to 23x23 pixels
        RESCALE_MODIFIER = 21

        # Load Tile Images
        self.TILE_IMG = PhotoImage(file="../sprites/friendly_tile.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.HIT_IMG = PhotoImage(file="../sprites/hit2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.MISS_IMG = PhotoImage(file="../sprites/miss2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)

        # Load Verticle Ship Sprites
        self.SHIP_START_VERTICAL = PhotoImage(file="../sprites/ship_start_vertical.png").subsample(5, 5)
        self.SHIP_MID_VERTICAL = PhotoImage(file="../sprites/ship_mid_vertical.png").subsample(5, 5)
        self.SHIP_END_VERTICAL = PhotoImage(file="../sprites/ship_end_vertical.png").subsample(5, 5)

        # Load Horizontal Ship Sprites
        self.SHIP_START_HORIZONTAL = PhotoImage(file="../sprites/ship_start_horizontal.png").subsample(5, 5)
        self.SHIP_MID_HORIZONTAL = PhotoImage(file="../sprites/ship_mid_horizontal.png").subsample(5, 5)
        self.SHIP_END_HORIZONTAL = PhotoImage(file="../sprites/ship_end_horizontal.png").subsample(5, 5)

        # initalize grid full of buttons
        self.shipGridButtons = [[Button(self, image=self.TILE_IMG, borderwidth=0, highlightthickness=0, relief=SUNKEN,
                                    command=lambda x=col, y=row:self.process(x, y)) for row in range(10)] for col in range(10)]
        
        # Add buttons to frame
        for i in range(10):
            for j in range(10):
                #self.shipGridButtons[i][j]['state'] = 'disabled'
                self.shipGridButtons[i][j].grid(row=i, column=j, sticky=N+E+S+W)

        # create map for placing ships
        self.placeShips()

        # Pack frame
        self.pack(side=RIGHT, fill=X, expand=1, anchor=E)
    
    # Loads the premade map
    def getFormattedMap(self):
        rawMap = open("../testmaps/a.map").readlines()
        formattedMap = []
        for line in rawMap:
            row = []
            for cell in line.strip():
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
        self.shipGridButtons[y][x].configure(image=self.HIT_IMG)
        self.shipMap[y][x] = 'x'
        self.parent.update_idletasks()
        self.parent.update()
    
    # Filler Code for processing press of ship buttons
    def process(self, x, y):
        logging.info(self.__classStr + f"Button pressed ({x},{y})")