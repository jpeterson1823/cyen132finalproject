from StartFrame import StartFrame
from tkinter import *

window = Tk()
window.attributes('-fullscreen', True)

start = StartFrame(window)

while True:
    start.animate()
    window.update()
    window.update_idletasks()
