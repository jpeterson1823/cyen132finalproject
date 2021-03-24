from tkinter import *
from random import randint
import time

global STARTB, RESETB
STARTB = 20
RESETB = 21

class WelcomeFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg="blue", width=1000, height=500)
        parent.attributes('-fullscreen', False)
        self.setup()

    def setup(self):
        titleText = open("titleText.txt", 'r').read()
        self.title = Label(self, text=titleText, anchor=CENTER, 
                            bg='blue', height=2, font=('Arial', 12), foreground='white')
        self.title.grid(row=0,column=0, sticky=N+E+S+W)
        self.pack()
    

# Shows all shots taken by the player and if they were a hit or miss
class ShotFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg="green", width=500, height=500)
        parent.attributes('-fullscreen', False)
        self.setup()
       
    def setup(self):
        # Load and resize all images to 50x50 pixels
        RESCALE_MODIFIER = 10
        
        # Load Tile Images
        self.TILE_IMG = PhotoImage(file="sprites/enemy_tile.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.HIT_IMG = PhotoImage(file="sprites/hit2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)
        self.MISS_IMG = PhotoImage(file="sprites/miss2.png").subsample(RESCALE_MODIFIER, RESCALE_MODIFIER)

        # initalize grid full of buttons
        self.shotGridButtons = [[Button(self, image=self.TILE_IMG, borderwidth=0, highlightthickness=0,
                                    command=lambda x=col, y=row:self.process(x,y)) for row in range(10)] for col in range(10)]

        # initalize grid full of buttons' states
        # 'U' means unknown, 'M' means miss, and 'H' means hit
        self.shotGridStates = [['U' for x in range(10)] for y in range(10)]

        # Add buttons to frame
        for i in range(10):
            for j in range(10):
                self.shotGridButtons[i][j].grid(row=i, column=j, sticky=N+E+S+W)

        # pack the frame
        self.pack(side=LEFT, fill=X, expand=1, anchor=N)

    
    def process(self, x, y):
        img = self.MISS_IMG if randint(0,1) == 1 else self.HIT_IMG
        self.shotGridButtons[x][y].configure(image=img)

        
# Shows all friendly ships and if/where they have been hit
class ShipFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg="blue", width=500, height=500)
        parent.attributes("-fullscreen", False)
        self.shipMap = self.getFormattedMap()
        self.setup()
        self.current_ship = "Carrier"
        self.preGame = True
    
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
            for j in range(10):
                self.shipGridButtons[i][j].grid(row=i, column=j, sticky=N+E+S+W)

        # create map for placing ships
        shipMap = self.placeShips()

        # Pack frame
        self.pack(side=RIGHT, fill=X, expand=1, anchor=E)
        return shipMap
    
    
    def getFormattedMap(self):
        rawMap = open("testmaps/a.map").readlines()
        formattedMap = []
        for line in rawMap:
            row = []
            for cell in line:
                row.append(cell)
            formattedMap.append(row)
        return formattedMap

    
    def placeShips(self):
        for row in range(len(self.shipMap)):
            for cell in range(len(self.shipMap)):
                if self.shipMap[row][cell] == 'o':
                    self.shipGridButtons[row][cell].configure(image=self.determineCellSprite(row, cell))

    

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

        
    def checkCellAbove(self, row, cell):
        if row != 0:
            # If ship cell has another ship cell above
            if self.shipMap[row-1][cell] == 'o':
                return True
        return False
    
    def checkCellBelow(self, row, cell):
        if row != 9:
            if self.shipMap[row+1][cell] == 'o':
                return True
        return False
    
    def checkCellRight(self, row, cell):
        if cell != 9:
            if self.shipMap[row][cell+1] == 'o':
                return True
        return False
    
    def checkCellLeft(self, row, cell):
        if cell != 0:
            if self.shipMap[row][cell-1] == 'o':
                return True
        return False
    

    def process(self, x, y):
        print(f"ShipFrame: ({x},{y})")


class Game():
    def __init__(self, window):
        # Start intro
        welcome = WelcomeFrame(window)
        window.update_idletasks()
        window.update()
        time.sleep(5)
        welcome.destroy()
        window.update_idletasks()
        window.update()

        # Start rest of game
        self.shotFrame = ShotFrame(window)
        self.shipFrame = ShipFrame(window)
        self.window = window
        self.startGameLoop()
        
    
    def reset(self):
        self.shotFrame.destroy()
        self.shotFrame = ShotFrame(self.window)
        self.shipFrame.destroy()
        self.shipFrame = ShipFrame(self.window)
    
    def startGameLoop(self):
        while True:
            try:
                self.window.update_idletasks()
                self.window.update()
            except:
                print("Window Manually Closed.")
                exit()


def main():
    Game(Tk())

if __name__ == "__main__":
    main()