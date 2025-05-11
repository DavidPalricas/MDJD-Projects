import pygame as pg

#The score class is responsible for keeping track of the player's score
class Score:
    # The constructor of the class initializes
    def __init__(self):
        pg.font.init()
        self.value = 0
        self.font = pg.font.Font("assets/font/snake.ttf", 30)
    
    # The increase method increases the player's score
    def increase(self):
        self.value += 1
    
    # The update method updates the player's score
    def update(self,display):
        score_label = self.font.render(f"Score {self.value}", True, (255,255,255))
        display.blit(score_label, (10,10))


