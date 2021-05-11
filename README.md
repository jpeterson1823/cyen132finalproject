# **BATTLESHIP [ RPi Edition ]**
A CYEN/CSC 132 RPi Project

Created by:
* Lucas Duran
* Galen Turner IV
* John Peterson

## Controls:
* Touchscreen
  - Used to select which cells to fire at.
* Buttons
  - SHOOT   (RED)
  - START   (GREEN)
  - RESET   (YELLOW)
  - FORFEIT (BLUE)

## Gameplay
The game loop consists of 2 phases:
* Selection Phase
* Fire Phase

In the selection phase, each player is prompted by the LCD display to choose three enemy cells they wish to fire at. 
Once three cells have been chosen, the player is then prompted to press the SHOOT button. Once both players have pressed
the SHOOT button, the game will continue to the Fire Phase.

In the fire phase, both devices will show whether the player's selected cells were hits or misses. Players are to take this
in to account when chosing their next cells as targets.

The game then loops back to the selection phase. This pattern continues until one of two things happens:
* All of one player's ships are destroied.
* One of the players hits the FORFEIT button, forfeitting the match.

### How To Play
Objective: Destroy all enemy ships or make them forfeit.

When prompted by the LCD, choose three cells as targets. Once a cell has been chosen, a corresponding LED will be illuminated over the SHOOT button.
Once you have selected your three targets, press the SHOOT button when prompted by the LCD.

A red pin on the cell you selected means you have hit a part of a ship.
A white pin on the cell you selected means you have missed a ship entirely.

To forfeit a match, simply press the FORFEIT button on the BATTLESHIP unit.

## Hardware Needed (Per Device)
Electronic Components:
* Raspberry Pi 4
* Raspberry Pi 4 Touchscreen capable display
* Large breadboard
* Raspberry Pi breadboard pinout attachment and ribbon cable
* A router with built-in access point (no modem is needed)
* I2C capable LCD display
* 5 common annode or cathode 4-pin RGB LEDs
* 4 nice-looking, different colored buttons (preferably ones that have pre-soldered wires attached)

Wires:
* Male to Male breadboard jumper wires
* Female to Female breadboard jumper wires
* Male to Female breadboard jumper wires
* Wire crimps that will fit your jumper wires and button wires

Tools:
* Wire crimper
* Wire stripper
* Neddle-nose pliers
