from tkinter import *
from src.Game import Game

#create game window
window = Tk()
#set title
window.title("BATTLESHIP: PI EDITION")
#shotFrame = ShotFrame(window)
#shipFrame = ShipFrame(window)
#window.mainloop()

# Start game
Game(window)