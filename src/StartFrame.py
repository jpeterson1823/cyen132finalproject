from tkinter import *
from PIL import Image
from PIL import ImageTk
from time import sleep
from threading import Thread
import logging

# The frame that is shown on startup
class StartFrame(Canvas):
    def __init__(self, parent):
        self.parent = parent
        # Create class logger
        self.log = logging.getLogger("StartFrame")
        logging.getLogger().setLevel(logging.INFO)

        # Create parent member variable
        self.parent = parent

        # Initialize frame
        Canvas.__init__(self, parent, bg='black', width=800, height=480)

        # Create animation thread exit flag
        self.__stopAnim = False

        # Start frame setup
        self.__setup(parent)
    
    # Sets up the start frame
    def __setup(self, parent):
        self.configure(highlightthickness=0)

        # Load background
        img = Image.open("../sprites/start.png")
        self.tkimg = ImageTk.PhotoImage(img)
        # Add background image to frame
        self.create_image(400,240, image=self.tkimg)

        # Load start frames
        self.__loadStartFrames()

        self.reverse = False
        self.frame = 0
        
        self.pack()
        
        self.animate()

    # Loads start frames into memory
    def __loadStartFrames(self):
        self.frames = []
        # Start Button Base loaded first
        img = Image.open("../sprites/pstartflat.png")
        tkimg = ImageTk.PhotoImage(img)
        self.create_image(400, 350, image=tkimg, tags='start')

        self.frames.append(tkimg)
        
        # Load inbetween frames then add them to canvas with id
        for i in range(5, 100, 5):
            # Create path string
            path = f"../sprites/pstartib{i}.png"
            # Load image and add to startFrames
            img = Image.open(path)
            tkimg = ImageTk.PhotoImage(img)
            self.frames.append(tkimg)

        # Start Button with max glow loaded last
        img = Image.open("../sprites/pstartbright.png")
        tkimg = ImageTk.PhotoImage(img)
        self.frames.append(tkimg)
        self.lastFrame = len(self.frames) - 1
    
    # Animates the start button
    def animate(self):
        # Check if at last frame and update reverse accordingly
        if self.frame == self.lastFrame:
            self.reverse = True
        # Check if at first frame and update reverse accordingly
        if self.frame == 0:
            self.reverse = False
        
        # Go back a frame
        if self.reverse:
            self.frame -= 1
        # Go forward a frame
        else:
            self.frame += 1

        self.itemconfigure('start', image=self.frames[self.frame])

        # Sleep to show animation
        sleep(0.025)
        print("Updated Frame")
        #self.after(50, self.__animate)
