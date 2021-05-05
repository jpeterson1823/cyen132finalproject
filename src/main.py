from tkinter import *
from Game import Game
import logging

logging.getLogger().setLevel(logging.INFO)
logging.info("Starting main script...")

#create game window
window = Tk()
# Set full screen
window.attributes('-fullscreen', True)
#set title
window.title("BATTLESHIP: PI EDITION")

# Create game object
game = Game(window)

try:
    # Start main loop
    window.mainloop()
except KeyboardInterrupt:
    game.exitFlag = True
    game.nethandler.exitFlag = True
    game.gpioHandler.exitFlag = True
    game.nethandler.isock.close()
    game.nethandler.osock.close()
    if game.nethandler.machineType == 'host':
        game.nethandler.oconnection.close()
        game.nethandler.iconnection.close()
