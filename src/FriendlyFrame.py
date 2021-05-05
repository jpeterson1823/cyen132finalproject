from tkinter import *
from PIL import Image
from PIL import ImageTk
import logging

# Shows all friendly ships and if/where they have been hit
class FriendlyFrame(Frame):
    def __init__(self, parent):
        # Create class logger
        self.log = logging.getLogger("FriendlyFrame")
        logging.getLogger("FriendlyFrame").setLevel(logging.INFO)

        self.parent = parent
        
        Frame.__init__(self, parent, bg="blue", width=400, height=480)
        self.shipMap = self.__getFormattedMap()
        self.setup()
        self.preGame = True
    
    # Sets up the game
    def setup(self):
        # Load and resize all images to 23x23 pixels
        #RESCALE_MODIFIER = 13
        width = 38
        height = 46

        # Load Tile Images
        #self.TILE_IMG = PhotoImage(file="../sprites/friendly_tile.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        #self.HIT_IMG = PhotoImage(file="../sprites/hit2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        #self.MISS_IMG = PhotoImage(file="../sprites/miss2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        
        img = Image.open("../sprites/friendly_tile.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.TILE_IMG = ImageTk.PhotoImage(img)

        img = Image.open("../sprites/hit2.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.HIT_IMG = ImageTk.PhotoImage(img)

        img = Image.open("../sprites/miss2.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.MISS_IMG = ImageTk.PhotoImage(img)

        # Load Verticle Ship Sprites
        #self.SHIP_START_VERTICAL = PhotoImage(file="../sprites/ship_start_vertical.png").subsample(5, 5)
        #self.SHIP_MID_VERTICAL = PhotoImage(file="../sprites/ship_mid_vertical.png").subsample(5, 5)
        #self.SHIP_END_VERTICAL = PhotoImage(file="../sprites/ship_end_vertical.png").subsample(5, 5)
        img = Image.open("../sprites/ship_start_vertical.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.SHIP_START_VERTICAL = ImageTk.PhotoImage(img)

        img = Image.open("../sprites/ship_mid_vertical.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.SHIP_MID_VERTICAL = ImageTk.PhotoImage(img)

        img = Image.open("../sprites/ship_end_vertical.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.SHIP_END_VERTICAL = ImageTk.PhotoImage(img)


        # Load Horizontal Ship Sprites
        #self.SHIP_START_HORIZONTAL = PhotoImage(file="../sprites/ship_start_horizontal.png").subsample(5, 5)
        #self.SHIP_MID_HORIZONTAL = PhotoImage(file="../sprites/ship_mid_horizontal.png").subsample(5, 5)
        #self.SHIP_END_HORIZONTAL = PhotoImage(file="../sprites/ship_end_horizontal.png").subsample(5, 5)
        img = Image.open("../sprites/ship_start_horizontal.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.SHIP_START_HORIZONTAL = ImageTk.PhotoImage(img)

        img = Image.open("../sprites/ship_mid_horizontal.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.SHIP_MID_HORIZONTAL = ImageTk.PhotoImage(img)

        img = Image.open("../sprites/ship_end_horizontal.png")
        img = img.resize((width, height), Image.ANTIALIAS)
        self.SHIP_END_HORIZONTAL = ImageTk.PhotoImage(img)


        # initalize grid full of buttons
        self.shipGridButtons = [[Button(self, image=self.TILE_IMG, bd=0, 
                                highlightthickness=0, relief=FLAT, bg='black',
                                command=lambda x=col, y=row:self.__process(x, y)) 
                                for row in range(10)] for col in range(10)]
        
        # Add buttons to frame
        for i in range(10):
            for j in range(10):
                #self.shipGridButtons[i][j]['state'] = 'disabled'
                self.shipGridButtons[i][j].grid(row=i, column=j, sticky=N+E+S+W)

        # create map for placing ships
        self.__placeShips()

        # Pack frame
        self.pack(side=LEFT, fill=X, expand=1, anchor=E)
    
    # Loads the premade map
    def __getFormattedMap(self):
        rawMap = open("../testmaps/a.map").readlines()
        formattedMap = []
        for line in rawMap:
            row = []
            for cell in line.strip():
                row.append(cell)
            formattedMap.append(row)
        return formattedMap

    # Places all the ship tiles based on a premade map
    def __placeShips(self):
        for row in range(len(self.shipMap)):
            for cell in range(len(self.shipMap)):
                if self.shipMap[row][cell] == 'o':
                    self.shipGridButtons[row][cell].configure(image=self.__determineCellSprite(row, cell))

    # Determines the sprite of the current cell
    def __determineCellSprite(self, row, cell):
        above = self.__checkCellAbove(row, cell)
        below = self.__checkCellBelow(row, cell)
        right = self.__checkCellRight(row, cell)
        left = self.__checkCellLeft(row, cell)

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
    def __checkCellAbove(self, row, cell):
        if row != 0:
            # If ship cell has another ship cell above
            if self.shipMap[row-1][cell] == 'o':
                return True
        return False
    
    # Checks below the cell of a ship pane
    # Used to decide what sprite should be used
    def __checkCellBelow(self, row, cell):
        if row != 9:
            if self.shipMap[row+1][cell] == 'o':
                return True
        return False
    
    # Checks to the right of a cell ship pane
    # Used to decide what sprite should be used
    def __checkCellRight(self, row, cell):
        if cell != 9:
            if self.shipMap[row][cell+1] == 'o':
                return True
        return False
    
    # Checks to the left for a cell ship pane
    # Used to decide what sprite should be used
    def __checkCellLeft(self, row, cell):
        if cell != 0:
            if self.shipMap[row][cell-1] == 'o':
                return True
        return False

    # Changes the sprite of the cell to hit
    def __hitCell(self, x, y):
        self.shipGridButtons[y][x].configure(image=self.HIT_IMG)
        self.shipMap[y][x] = 'x'
        self.parent.update_idletasks()
        self.parent.update()
    
    # Filler Code for __processing press of ship buttons
    def __process(self, x, y):
        self.log.info(f"Button pressed ({x},{y})")

    # Checks the friendlyFrame board for a hit and updates the image
    def checkHits(self, data):
        self.log.info("Checking hits...")
        hitmiss = []
        for coordstr in data.split(";"):
            print(coordstr)
            temp = coordstr.split(',')
            x = int(temp[0])
            y = int(temp[1])
            print(self.shipMap[y][x])
            if self.shipMap[y][x] != '-':
                print('hit')
                hitmiss.append(True)
                self.hitCell(x, y)
            else:
                hitmiss.append(False)
        self.log.info("Set hits if there were any.")
        return hitmiss