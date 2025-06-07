import logging
import random
import math

from consts import Direction, Tiles, VITAL_SPACE, NEST_SIZE

logger = logging.getLogger("Map")
logger.setLevel(logging.DEBUG)

class Map:
    def __init__(
        self,
        level=1,
        size=(VITAL_SPACE + 10, VITAL_SPACE + 10),
        mapa=None,
    ):
        assert size[0] > VITAL_SPACE + 9
        assert size[1] > VITAL_SPACE + 9

        self._level = level
        self._size = size
        self._stones = []
        self._food = []
        self._snake_nests = []

        if not mapa:
            logger.info("Generating a MAP")
            self.map = [[Tiles.PASSAGE] * self.ver_tiles for _ in range(self.hor_tiles)]

            # add stones
            for _ in range(10):
                x, y = random.randint(0, self.hor_tiles - 1), random.randint(
                    0, self.ver_tiles - 1
                )
                wall_length = 5
                for yy in range(
                    y, (y + random.choice([-wall_length, wall_length])) % self.ver_tiles
                )[:wall_length]:
                    self.map[x][yy] = Tiles.STONE
                    self._stones.append((x, yy))
                for xx in range(
                    x, (x + random.choice([-wall_length, wall_length])) % self.hor_tiles
                )[:wall_length]:
                    self.map[xx][y] = Tiles.STONE
                    self._stones.append((xx, y))

        else:
            logger.info("Loading MAP")
            self.map = mapa

    @property
    def food(self):
        return [(x, y, self.map[x][y].name) for x, y in self._food]

    def spawn_snake(self):
        x = random.randint(0, self.hor_tiles - 1)
        y = random.randint(0, self.ver_tiles - 1)
        while any((x, y) in nest for nest in self._snake_nests):
            x = random.randint(0, self.hor_tiles - 1)
            y = random.randint(0, self.ver_tiles - 1)
        self._snake_nests.append([(a, b) for a in range(x - NEST_SIZE, x + NEST_SIZE) for b in range(y - NEST_SIZE, y + NEST_SIZE)])
        return x, y

    def spawn_food(self, food_type=Tiles.FOOD):
        x = random.randint(0, self.hor_tiles - 1)
        y = random.randint(0, self.ver_tiles - 1)
        while (x, y) in self._food or (x, y) in self._stones:
            x = random.randint(0, self.hor_tiles - 1)
            y = random.randint(0, self.ver_tiles - 1)
        self.map[x][y] = food_type
        self._food.append((x, y))
        logger.debug("Food spawned at %s", self._food[-1])

    def eat_food(self, pos):
        x, y = pos
        old = self.map[x][y]
        self.map[x][y] = Tiles.PASSAGE
        self._food.remove((x, y))
        return old

    @property
    def hor_tiles(self):
        return self.size[0]

    @property
    def ver_tiles(self):
        return self.size[1]

    def __getstate__(self):
        return self.map

    def __setstate__(self, state):
        self.map = state

    @property
    def size(self):
        return self._size

    @property
    def level(self):
        return self._level

    @property
    def digdug_spawn(self):
        return self._digdug_spawn

    def get_tile(self, pos: tuple[int, int]):
        x, y = pos
        return self.map[x][y]

    def get_zone(self, pos: tuple[int, int], size: int):
        zone: dict[int, dict[int, Tiles]] = {}
        x, y = pos
        for i in range(x - size, x + size + 1):
            for j in range(y - size, y + size + 1):
                if math.dist((x, y), (i, j)) <= size:
                    ii = i % self.hor_tiles
                    jj = j % self.ver_tiles
                    if ii not in zone:
                        zone[ii] = {}
                    zone[ii][jj] = self.map[ii][jj]

        return zone

    def is_blocked(self, pos, traverse):
        x, y = pos
        if not traverse and (
            x not in range(self.hor_tiles) or y not in range(self.ver_tiles)
        ):
            logger.debug("Crash against map edge(%s, %s)", x, y)
            return True
        if self.map[x][y] == Tiles.PASSAGE:
            return False
        if self.map[x][y] == Tiles.STONE:
            if traverse:
                return False
            else:
                logger.debug("Crash against Stone(%s, %s)", x, y)
                return True
        if self.map[x][y] in [Tiles.FOOD, Tiles.SUPER]:
            return False

        assert False, "Unknown tile type"

    def calc_pos(self, cur, direction: Direction, traverse=False):
        cx, cy = cur
        npos = cur
        if direction == Direction.NORTH:
            if traverse and cy - 1 < 0:  # wrap around
                npos = cx, self.ver_tiles - 1
            else:
                npos = cx, cy - 1
        if direction == Direction.WEST:
            if traverse and cx - 1 < 0:  # wrap around
                npos = self.hor_tiles - 1, cy
            else:
                npos = cx - 1, cy
        if direction == Direction.SOUTH:
            if traverse and cy + 1 >= self.ver_tiles:  # wrap around
                npos = cx, 0
            else:
                npos = cx, cy + 1
        if direction == Direction.EAST:
            if traverse and cx + 1 >= self.hor_tiles:  # wrap around
                npos = 0, cy
            else:
                npos = cx + 1, cy

        # test blocked
        if self.is_blocked(npos, traverse):
            logger.debug("%s is blocked", npos)
            return cur

        return npos
