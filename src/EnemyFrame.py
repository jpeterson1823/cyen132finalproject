from tkinter import *

# Shows all shots taken by the player and if they were a hit or miss
class EnemyFrame(Frame):
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