import pygame
# This is the food class
class Food:
    def __init__(self,pos):
        self.pos = pos

    def get_position(self):
        return self.pos
    
    def draw(self,display,SCALE):
        pygame.draw.rect(display, "green", (SCALE * self.pos[0], SCALE * self.pos[1], SCALE, SCALE))