import pygame as pg
import random as rand

# The size of the snake and food cubes
from consts import SCALE,WIDTH,HEIGHT

# This is the food class
class Food:
    # The constructor of the class initializes the food with its position
    def __init__(self):
        self.pos = rand.randrange(WIDTH), rand.randrange(HEIGHT)
    
    # The get_position method returns the food's position
    def get_position(self):
        return self.pos
    
    # The update_pos updates the food position
    # Creating an ilusion thar the food was eaten and disapeared
    def update_pos(self):
        self.pos = rand.randrange(WIDTH), rand.randrange(HEIGHT)

    
    # The draw method draws the food in the pygame window
    def draw(self,display):
        pg.draw.rect(display, "red", (SCALE * self.pos[0], SCALE * self.pos[1], SCALE, SCALE))