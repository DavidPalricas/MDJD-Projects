from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import pygame

EVENT_FOOD_EATEN = "event_food_eaten"

GAME_EVENT = pygame.event.custom_type()


class Directions(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class Food:
    pos: tuple
    is_super: bool


@dataclass
class Stone:
    pos: tuple


@dataclass
class Snake:
    body: list
    direction: Directions
    score: int
    name: str
    traverse: bool


@dataclass
class ScoreBoard:
    highscores: list[tuple[str, int]]


def get_direction(x, y, prev_x, prev_y, HEIGHT, WIDTH):
    """given 2 coordinates returns direction taken.
    HEIGHT and WIDTH are the dimensions of the board and enable proper handling of the edges when the snake wraps around.
    """
    dir = None
    if x - prev_x == WIDTH - 1:
        dir = Directions.LEFT
    elif x - prev_x == -(WIDTH - 1):
        dir = Directions.RIGHT
    elif y - prev_y == HEIGHT - 1:
        dir = Directions.UP
    elif y - prev_y == -(HEIGHT - 1):
        dir = Directions.DOWN
    elif x - prev_x > 0:
        dir = Directions.RIGHT
    elif x - prev_x < 0:
        dir = Directions.LEFT
    elif y - prev_y > 0:
        dir = Directions.DOWN
    elif y - prev_y < 0:
        dir = Directions.UP
    return dir
