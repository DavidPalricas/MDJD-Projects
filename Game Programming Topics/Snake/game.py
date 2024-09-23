import pygame
import random
import snake as s
import food as f

WIDTH, HEIGHT = 80, 40
SCALE = 10
GAME_EVENT = pygame.event.custom_type()

running = True

display = pygame.display.set_mode((SCALE * WIDTH, SCALE * HEIGHT))
clock = pygame.time.Clock()

snake = s.Snake()
food = f.Food((random.randrange(WIDTH), random.randrange(HEIGHT)))

def update_window():
    pygame.display.flip()
    clock.tick(15)

def quit_game():
    global running
    running = False

def check_snake_colisions():
    global food
    snake_body = snake.get_body()
    for x, y in snake_body:
        snake.draw(display,SCALE,(x,y))
        
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

def update_map():
     display.fill("white")
     food.draw(display,SCALE)

def event_listener():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.change_direction((0, -1))

            elif event.key == pygame.K_DOWN:
                snake.change_direction((0, 1))

            elif event.key == pygame.K_LEFT:
                snake.change_direction((-1, 0))

            elif event.key == pygame.K_RIGHT:
                snake.change_direction((1, 0))

        elif event.type == GAME_EVENT:
            print(event.txt)

def main():
    while running:
        event_listener()

        update_map()

        check_snake_colisions()
 
        snake.move()

        update_window()
      
    pygame.quit()

if __name__ == "__main__":
    main()
