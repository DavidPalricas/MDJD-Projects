import pygame
import random

# The snake and food classes
import snake as s
import food as f

# The game constants
from consts import *

# This variable is used to control the game loop
running = True

# The pygame display
display = pygame.display.set_mode((SCALE * WIDTH, SCALE * HEIGHT))

# The pygame clock
clock = pygame.time.Clock()

# The snake and food objects
snake = s.Snake()
food = f.Food((random.randrange(WIDTH), random.randrange(HEIGHT)))

# The update_window function updates the game window
def update_window():
    pygame.display.flip()
    clock.tick(15)

# The quit_game function quits the game
def quit_game():
    global running
    running = False

# The check_snake_colisions function checks for snake collisions (wall,self and food collisions)
def check_snake_colisions():
    global food
    snake_body = snake.get_body()
    for x, y in snake_body:
        snake.draw(display,(x,y))
        
        food_pos = food.get_position()

        if food_pos == (x, y):
            snake.increase_length()
            ev = pygame.event.Event(GAME_EVENT, {'txt': "mmmnhami"})
            pygame.event.post(ev)
            print("Sent")
            ev = pygame.event.Event(GAME_EVENT, {'txt': "dammmm"})
            pygame.event.post(ev)
            food = f.Food((random.randrange(WIDTH), random.randrange(HEIGHT)))

        if x not in range(WIDTH) or y not in range(HEIGHT):
            print("Snake crashed against the wall")
            quit_game()

        if snake_body.count((x, y)) > 1:
            print("Snake eats self")
            quit_game()    

# The update_map function updates the game window by filling it with a black color and drawing the food
def update_map():
     display.fill("black")
     food.draw(display)

# The event_listener function listens for events (keyboard and quit events) and acts accordingly
def event_listener():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.change_direction(UP)

            elif event.key == pygame.K_DOWN:
                snake.change_direction(DOWN)

            elif event.key == pygame.K_LEFT:
                snake.change_direction((LEFT))

            elif event.key == pygame.K_RIGHT:
                snake.change_direction((RIGHT))

        elif event.type == GAME_EVENT:
            print(event.txt)

# The main function of the game
# This function is responsible for running the game loop
# It listens for events, updates the game state, checks for collisions and updates the game window
def main():
    while running:
        event_listener()

        update_map()

        check_snake_colisions()
 
        snake.move()

        update_window()
      
    pygame.quit()

# The following line of code is the entry point of the game
if __name__ == "__main__":
    main()
