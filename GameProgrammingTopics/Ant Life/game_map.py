import pygame as pg
import random
from consts import WINDOW_WIDTH, WINDOW_HEIGHT
class GameMap():

    def __init__(self) -> None:
        self.map = self.create_map()

        self.map_width = self.map.get_width()
        self.map_height = self.map.get_height()

        self.environment_elements = []

        self.sugar_number = 20

        self.water_number = 10

        self.poison_number = 15

    def create_map(self):
        """ The create_map function creates the game map.

            Returns:
            - map: The game map.
        """
        map = pg.Surface((800, 600))
        map.fill((155, 118, 83))

        return map
    
    def draw(self,window):
        window.blit(self.map,(0,0))
        
        if self.environment_elements == []:
            self.draw_ants_home(window)
            self.draw_environment_elements(window)
        else:
            for element in self.environment_elements:
                pg.draw.rect(window,element[2],element[0])

            
    def draw_ants_home(self,window):
        home = pg.Rect(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,100,100)
        pg.draw.rect(window,(101, 67, 33),home)
        self.environment_elements.append((home,"home",(101, 67, 33)))

    def draw_environment_elements(self,window):

        for i in range (self.sugar_number):

            if i <= self.water_number:
                self.create_environment_element(window,(15,15),(0,0,255),"water")

            if i <= self.poison_number:
                self.create_environment_element(window,(15,15),(160,32,240),"poison")

            self.create_environment_element(window,(15,15),(255,255,255),"sugar")
    
    def create_environment_element(self,window,object_size,color,element_name):

        element = pg.Rect(random.randint(0, self.map_width), random.randint(0, self.map_height), object_size[0], object_size[1])
       
        for obj in self.environment_elements:
            if element.colliderect(obj[0]):
                self.create_environment_element(window,object_size,color,element_name)  
                return
            

        pg.draw.rect(window, color, element)
        self.environment_elements.append((element,element_name,color))

      


        


