import pygame

# The width and height of the game window
WIDTH, HEIGHT = 80, 40

# The size of the snake and food cubes
SCALE = 10

# The custom event type
GAME_EVENT = pygame.event.custom_type()

# The directions the snake can move
RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, -1)
DOWN = (0, 1)