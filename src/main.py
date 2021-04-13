from tkinter import *
from Game import Game
import logging

logging.getLogger().setLevel(logging.INFO)

#create game window
window = Tk()
#set title
window.title("BATTLESHIP: PI EDITION")

# Start game
Game(window)

window.mainloop()