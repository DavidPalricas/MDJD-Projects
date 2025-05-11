from command import *
import pygame as pg
class InputHandler:

    def __init__(self):
        self.command = None
  

    def set_command(self,snake_number):
        if snake_number % 2 == 0:
            self.command = {
                pg.K_w: Up,
                pg.K_s: Down,
                pg.K_a: Left,
                pg.K_d: Right,
            }
        else:
            self.command = {
                pg.K_UP: Up,
                pg.K_DOWN : Down,
                pg.K_LEFT: Left,
                pg.K_RIGHT: Right
            }


    def handle_input(self,key):
        
        if key not in self.command:
            return None
        
        return self.command[key]


