import pygame as pg

# The width and height of the game window
WIDTH, HEIGHT = 80, 40

# The size of the snake and food cubes
SCALE = 10

# The custom event type
GAME_EVENT = pg.event.custom_type()

# The directions the snake can move
RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, -1)
DOWN = (0, 1)

ARROW_KEYS = [pg.K_UP,pg.K_DOWN,pg.K_LEFT,pg.K_RIGHT]

WASD_KEYS = [pg.K_w,pg.K_s,pg.K_a,pg.K_d]