import pygame as pg

# The snake and food classes
import snake as s
import food as f

# The game constants
from consts import SCALE,WIDTH,HEIGHT,GAME_EVENT,WASD_KEYS,ARROW_KEYS

# This variable is used to control the game loop
running = True

# The pygame display
display = pg.display.set_mode((SCALE * WIDTH, SCALE * HEIGHT))

# The pygame clock
clock = pg.time.Clock()

# The update_window function updates the game window
def update_window():
    pg.display.flip()
    clock.tick(15)

# The quit_game function quits the game
def quit_game():
    global running
    running = False

# The check_snake_colisions function checks for snake collisions (wall,self and food collisions)
def check_snake_colisions(snakes,food):
    for snake in snakes:
        snake_body = snake.get_body()
        for x, y in snake_body:
            snake.draw(display,(x,y))    
            food_pos = food.get_position()

            if food_pos == (x, y):
                snake.increase_length()
                ev = pg.event.Event(GAME_EVENT, {'txt': "mmmnhami"})
                pg.event.post(ev)
                print("Sent")
                ev = pg.event.Event(GAME_EVENT, {'txt': "dammmm"})
                pg.event.post(ev)
                food.update_pos()

            if x not in range(WIDTH) or y not in range(HEIGHT):
                print("Snake crashed against the wall")
                quit_game()

            if snake_body.count((x, y)) > 1:
                print("Snake eats self")
                quit_game()    

# The update_map function updates the game window by filling it with a black color and drawing the food
def update_map(food):
     display.fill("black")
     food.draw(display)

# The event_listener function listens for events (keyboard and quit events) and acts accordingly
def event_listener(snakes): 
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit_game()
        elif event.type == pg.KEYDOWN:
            for i in range(0,len(snakes)):
                if i % 2 == 0 and event.key in WASD_KEYS:
                    snakes[i].change_direction(event.key)

                elif i %2 != 0 and event.key in ARROW_KEYS:
                    snakes[i].change_direction(event.key)
               

        elif event.type == GAME_EVENT:
            print(event.txt)

# The main function of the game
# This function is responsible for running the game loop
# It listens for events, updates the game state, checks for collisions and updates the game window
def main():

    # The snake and food objects

    snakes = []

    for  i in range(0,2):
        snakes.append(s.Snake())
    
    food = f.Food()

    while running:
        event_listener(snakes)

        update_map(food)

        check_snake_colisions(snakes,food)
 
        for snake in snakes:
            snake.move()

        update_window()
      
    pg.quit()

# The following line of code is the entry point of the game
if __name__ == "__main__":
    main()
