import pygame as pg
import random as rand
import math as m

# The size of the snake and food cubes
from consts import SCALE,WIDTH,HEIGHT,RIGHT,LEFT,UP,DOWN

# This is the snake class 
class Snake():
    #The constructor of the class initializes the snake with its body, direction and length
    vital_space = (WIDTH- WIDTH/2,HEIGHT-HEIGHT/2)
    snakes_heads_pos = []
    def __init__(self) :
        # The snake body is 3 red cubes
        self.snake_body = self.spawn_snake()

        # The snake direction is initially to the right
        self.snake_direction = (1, 0)
        self.snake_length = 3


    # The change_direction method changes the snake's direction
    def change_direction(self,key):   
        coordinates = ()
        match key:
            case pg.K_UP | pg.K_w:
                coordinates = UP

            case pg.K_DOWN | pg.K_s:
                coordinates= DOWN

            case pg.K_LEFT | pg.K_a:
                pg.K_a
                coordinates = LEFT

            case _:
                coordinates = RIGHT

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

        pg.draw.rect(display, "green", (SCALE * x, SCALE * y, SCALE, SCALE))

    
    def spawn_snake(self):
        snake_body = []
        #[(40, 20), (39, 20), (38, 20)]
        snake_head = (rand.randrange(Snake.vital_space[0]),rand.randrange(Snake.vital_space[1]))

        if (not self.check_snake_pos(snake_head)):
            self.spawn_snake()
            return
             
        snake_body.append(snake_head)

        for i in range (1,3):
            snake_body.append((snake_head[0]- i,snake_head[1]))

        return snake_body
    
    def check_snake_pos(self,snake_head):
        x = snake_head[0]
        y = snake_head[1]

        for other_snake_head in Snake.snakes_heads_pos:
            if x or x -1 or x -2 or y in other_snake_head:
                return False
            
            if m.dist(snake_head,other_snake_head) < 10:
                return False
                      
        return True

        

        
   