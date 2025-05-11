import pygame as pg

# The width and height of the game window
WIDTH, HEIGHT = 80, 40

# The size of the snakes and apples
SCALE = 10

# The custom event type
GAME_EVENT = pg.event.custom_type()

NUMBER_OF_PLAYERS = 2

# The directions the snake can move
RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, -1)
DOWN = (0, 1)