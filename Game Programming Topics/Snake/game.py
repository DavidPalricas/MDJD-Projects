import pygame as pg

# The snake and food classes
import snake as s
import apple as f
import score as sc

# The game constants
# SCALE : Size of the snakes and apples
# WIDTH, HEIGHT : Width and Height of the game window
# GAME_EVENT : Custom event type
# ARROW_KEYS : The keys the snake can use to move (Arrow keys)
# WASD_KEYS : The keys the snake can use to move (WASD keys)
# NUMBER_OF_PLAYERS : Number of players
from consts import SCALE,WIDTH,HEIGHT,GAME_EVENT,NUMBER_OF_PLAYERS,WASD_KEYS,ARROW_KEYS

# This variable is used to control the game loop
running = True

# The update_window function updates the game window
def update_window(clock):
    pg.display.flip()
    clock.tick(15)

# The quit_game function quits the game
def quit_game():
    global running
    running = False

# The check_snake_colisions function checks for snake collisions (wall,self and food collisions)
def check_snake_colisions(snakes,apples,score,display):
    for snake in snakes:
        snake_body = snake.get_body()

        for x, y in snake_body:
            snake.draw(display,(x,y))

            for apple in apples:    
                apple_pos = apple.get_position()

                if apple_pos == (x, y):
                    score.increase()
                    snake.increase_length()
                    ev = pg.event.Event(GAME_EVENT, {'txt': "mmmnhami"})
                    pg.event.post(ev)
                    print("Sent")
                    ev = pg.event.Event(GAME_EVENT, {'txt': "dammmm"})
                    pg.event.post(ev)
                    apple.update_pos()
                    
                if x not in range(WIDTH) or y not in range(HEIGHT):
                    print("Snake crashed against the wall")
                    quit_game()

                if snake_body.count((x, y)) > 1:
                    print("Snake eats self")
                    quit_game()    

# The update_map function updates the game window by filling it with a black color and drawing the food
def update_map(foods,display,score):
     display.fill("black")
     score.update(display)
     for food in foods:
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
    # The pygame display
    display = pg.display.set_mode((SCALE * WIDTH, SCALE * HEIGHT))

    # The pygame clock
    clock = pg.time.Clock()

    snakes = []
    apples = []

    score = sc.Score()

    for  _ in range(0,NUMBER_OF_PLAYERS):
        snakes.append(s.Snake())
        apples.append(f.Apple())

    while running:
        event_listener(snakes)

        update_map(apples,display,score)

        check_snake_colisions(snakes,apples,score,display)
 
        for snake in snakes:
            snake.move()

        update_window(clock)
      
    pg.quit()

# The following line of code is the entry point of the game
if __name__ == "__main__":
    main()
