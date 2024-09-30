import pygame
import random

# The size of the snake and food cubes
from consts import SCALE,WIDTH,HEIGHT

# This is the food class
class Food:
    # The constructor of the class initializes the food with its position
    def __init__(self):
        self.pos = random.randrange(WIDTH), random.randrange(HEIGHT)
    
    # The get_position method returns the food's position
    def get_position(self):
        return self.pos
    
    def new_food(self):
        self.pos = random.randrange(WIDTH), random.randrange(HEIGHT)

    
    # The draw method draws the food in the pygame window
    def draw(self,display):
        pygame.draw.rect(display, "red", (SCALE * self.pos[0], SCALE * self.pos[1], SCALE, SCALE))