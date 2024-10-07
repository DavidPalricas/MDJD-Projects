import pygame as pg
import entity as ent

# SCALE : Size of the snakes and apples
# WIDTH, HEIGHT : Width and Height of the game window
# RIGHT,LEFT,UP,DOWN : The directions the snake can move
from consts import SCALE,WIDTH,HEIGHT,RIGHT,LEFT,UP,DOWN

# This is the snake class 
class Snake(ent.Entity):
    # The vital_space variable stores the vital space for the snake to spawn
    vital_space = (WIDTH- WIDTH/2-1,HEIGHT-HEIGHT/2-1)
    
    # The spawn_threshold variable stores the spawn threshold for the snakes
    spawn_threshold = 10

     #The constructor of the class initializes the snake with its body, direction and length
    def __init__(self) :

        # The super() function is used to call the parent class (Entity Class) constructor
        super().__init__(Snake.vital_space,Snake.spawn_threshold)

        # The snake body is 3 red cubes
        self.snake_body = self.spawn()

        # The snake direction is initially to the right
        self.snake_direction = RIGHT

        self.snake_length = 3
    

    def change_direction(self,new_direction):
        self.snake_direction = new_direction

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
    
    # The spawn method spawns the snake
    # This metod uses the parent class spawn method to get the snake head
    # And then creates the snake body
    def spawn(self):    
        snake_head = super().spawn()
   
        snake_body = []
             
        snake_body.append(snake_head)

        for i in range (1,3):
            # Checks if the snake's body is spawning in the same position as another snake
            if (self.check_other_spawns((snake_head[0]-i,snake_head[1]))):
                snake_body.append((snake_head[0]- i,snake_head[1]))
            else:
                self.spawn()
                return
            
        # Parent class atributte
        self.other_entities.append(snake_body)

        return snake_body
    
    # The draw method draws the snake in the pygame window
    def draw(self,display,position):
        x,y = position

        pg.draw.rect(display, "green", (SCALE * x, SCALE * y, SCALE, SCALE))
    



        

        
   