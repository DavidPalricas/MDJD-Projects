import pygame as pg

import entity as ent

# SCALE : Size of the snakes and apples
# WIDTH, HEIGHT : Width and Height of the game window
from consts import SCALE,WIDTH,HEIGHT

# This is the food class
class Apple(ent.Entity):
    vital_space=(WIDTH- WIDTH/2+1,HEIGHT-HEIGHT/2+1)
    spawn_threshold = 2

    # The constructor of the class initializes the food with its position
    def __init__(self):
        # The super() function is used to call the parent class (Entity Class) constructor
        super().__init__(Apple.vital_space,Apple.spawn_threshold)
        
        self.pos = self.spawn()
    
    # The get_position method returns the food's position
    def get_position(self):
        return self.pos
    
    # The update_pos updates the food position
    # Creating an ilusion thar the food was eaten and disapeared
    def update_pos(self):
        self.pos = self.spawn()
    
    # The draw method draws the food in the pygame window
    def draw(self,display):
        pg.draw.rect(display, "red", (SCALE * self.pos[0], SCALE * self.pos[1], SCALE, SCALE))