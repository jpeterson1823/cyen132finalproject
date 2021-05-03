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

# Start main loop

try:
    while True:
        if game.exitFlag == True:
            logging.info("Joining gameLoopThread with main...")
            game.gameLoopThread.join()
            logging.info("Joining listenThread with main...")
            game.nethandler.listenThread.join()
            logging.info("Joining buttonThread with main...")
            game.gpioHandler.buttonThread.join()

            logging.info("Creating new game instance...")
            game = Game(window)

        window.update_idletasks()
        window.update()
except KeyboardInterrupt:
    print('exiting')
    exit(1)