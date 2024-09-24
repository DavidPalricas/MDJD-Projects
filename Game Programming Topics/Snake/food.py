import pygame

# The size of the snake and food cubes
from consts import SCALE

# This is the food class
class Food:
    # The constructor of the class initializes the food with its position
    def __init__(self,pos):
        self.pos = pos
    
    # The get_position method returns the food's position
    def get_position(self):
        return self.pos
    
    # The draw method draws the food in the pygame window
    def draw(self,display):
        pygame.draw.rect(display, "red", (SCALE * self.pos[0], SCALE * self.pos[1], SCALE, SCALE))