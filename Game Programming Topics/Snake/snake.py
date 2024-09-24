import pygame

# The size of the snake and food cubes
from consts import SCALE 

# This is the snake class 
class Snake:
    #The constructor of the class initializes the snake with its body, direction and length
    def __init__(self) :
        # The snake body is 3 red cubes
        self.snake_body = [(40, 20), (39, 20), (38, 20)]

        # The snake direction is initially to the right
        self.snake_direction = (1, 0)
        self.snake_length = 3

    # The change_direction method changes the snake's direction
    def change_direction(self,coordinates):
        self.snake_direction = coordinates
    
    # The increase_length method increases the snake's length
    def increase_length(self):
        self.snake_length += 1
    
    # The get_body method returns the snake's body
    def get_body(self):
        return self.snake_body
    
    # The move method moves the snake
    def move(self):
        #Inserts a new head position to the snake body effectively moving the snake in the direction specified
        self.snake_body[0:0] = [
        (self.snake_body[0][0] + self.snake_direction[0], self.snake_body[0][1] + self.snake_direction[1])
        ]

        while len(self.snake_body) > self.snake_length:
            self.snake_body.pop()
    
    # The draw method draws the snake in the pygame window
    def draw(self,display,position):
        x = position[0]
        y = position[1]

        pygame.draw.rect(display, "green", (SCALE * x, SCALE * y, SCALE, SCALE))
        

        
   