from tkinter import *
from Game import Game
import logging

#create game window
window = Tk()
# Set full screen
window.attributes('-fullscreen', True)
#set title
window.title("BATTLESHIP: PI EDITION")

# Start game
Game(window)

window.mainloop()
