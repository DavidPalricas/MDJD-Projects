from enum import IntEnum

HISTORY_LEN = 10

KILL_SNAKE_POINTS = 100

MAX_LEN_ROPE = 3
MIN_ENEMIES = 3

VITAL_SPACE = 3
NEST_SIZE = 3

TIMEOUT = 3000


class Tiles(IntEnum):
    PASSAGE = 0
    STONE = 1
    FOOD = 2
    SUPER = 3
    SNAKE = 4


class SuperFood(IntEnum):
    POINTS = 1
    LENGTH = 2
    RANGE = 3
    TRAVERSE = 4


class Speed(IntEnum):
    SLOWEST = (1,)
    SLOW = (2,)
    NORMAL = (3,)
    FAST = 4


class Direction(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
