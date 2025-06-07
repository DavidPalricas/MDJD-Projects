import asyncio
import logging
import random
from collections import deque

from consts import KILL_SNAKE_POINTS, TIMEOUT, Direction, HISTORY_LEN, Tiles, SuperFood
from mapa import Map

logger = logging.getLogger("Game")
logger.setLevel(logging.DEBUG)

INITIAL_SCORE = 0
GAME_SPEED = 10
MAP_SIZE = (48, 24)
FOOD_IN_MAP = 4

class Snake:
    def __init__(self, player_name, x=1, y=1):
        self._name = player_name
        self._body = [(x, y)]
        self._spawn_pos = (x, y)
        self._direction: Direction = Direction.EAST
        self._history = deque(maxlen=HISTORY_LEN)
        self._score = 0
        self._traverse = True  # if True, the snake can traverse stones
        self._alive = True
        self.lastkey = ""
        self.to_grow = 1
        self.range = 3

    def sight(self, mapa, snakes):
        in_range = mapa.get_zone(self.head, self.range)

        for snake in snakes:  # mark all snakes in the map
            if not snake.alive:
                continue  # ignore dead snakes
            for x, y in snake.body:
                if x in in_range and y in in_range[x]:
                    in_range[x][y] = Tiles.SNAKE

        return in_range

    def grow(self, amount=1):
        self.to_grow += amount
        self.to_grow = max(-len(self._body) + 1, self.to_grow)

    @property
    def head(self):
        return self._body[-1]

    @property
    def tail(self):
        return self._body[:-1]

    @property
    def body(self):
        return self._body

    @property
    def alive(self):
        return self._alive

    def kill(self):
        self._alive = False

    @property
    def name(self):
        return self._name

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @property
    def history(self):
        return str(list(self._history))

    @property
    def direction(self):
        return self._direction

    @property
    def x(self):
        return self._pos[0]

    @property
    def y(self):
        return self._pos[1]

    @property
    def __str__(self) -> str:
        return f"{self.name}({self._pos})"

    def move(self, mapa, direction: Direction):
        if direction is None:
            return

        new_pos = mapa.calc_pos(self.head, direction, traverse=self._traverse)

        if new_pos == self.head or new_pos in self._body:
            # if we can't move to the new position, we crashed against a wall
            # or we are crashing against ourselves
            logger.debug(
                "Head %s can't move to %s with direction %s",
                self.head,
                new_pos,
                direction,
            )
            self.kill()
            return

        self._body.append(new_pos)
        if self.to_grow > 0:  # if we are growing
            self.to_grow -= 1
        elif self.to_grow < 0 and len(self._body) > 3:  # if we are shrinking
            self.to_grow += 1
            self._body.pop(0)
            self._body.pop(0)
        else:  # if we are simply moving
            self._body.pop(0)

        self._direction = direction
        self._history.append(new_pos)

    def collision(self, pos):
        return pos in self._body

    def _calc_dir(self, old_pos, new_pos):
        if old_pos[0] < new_pos[0]:
            return Direction.EAST
        elif old_pos[0] > new_pos[0]:
            return Direction.WEST
        elif old_pos[1] < new_pos[1]:
            return Direction.SOUTH
        elif old_pos[1] > new_pos[1]:
            return Direction.NORTH
        logger.error(
            "Can't calculate direction from %s to %s, please report as this is a bug",
            old_pos,
            new_pos,
        )
        return None


def key2direction(key):
    if key == "w":
        return Direction.NORTH
    elif key == "a":
        return Direction.WEST
    elif key == "s":
        return Direction.SOUTH
    elif key == "d":
        return Direction.EAST
    return None


class Game:
    def __init__(self, level=1, timeout=TIMEOUT, size=MAP_SIZE, game_speed=GAME_SPEED):
        logger.info(f"Game(level={level})")
        self.initial_level = level
        self._game_speed = game_speed
        self._running = False
        self._timeout = timeout
        self._step = 0
        self._state = {}
        self._snakes = {}
        self.map = Map(size=size)

    @property
    def snakes(self):
        return self._snakes

    @property
    def level(self):
        return self.map.level

    @property
    def running(self):
        return self._running

    @property
    def total_steps(self):
        return self._total_steps

    def start(self, players_names):
        logger.debug("Reset world")
        self._running = True
        self._snakes = {
            player_name: Snake(player_name, *self.map.spawn_snake())
            for player_name in players_names
        }
        for _ in range(FOOD_IN_MAP):
            self.map.spawn_food()

    def stop(self):
        logger.info("GAME OVER")
        self._running = False

    def quit(self):
        logger.debug("Quit")
        self._running = False

    def keypress(self, player_name, key):
        self._snakes[player_name].lastkey = key

    def update_snake(self, name):
        try:
            snake = self._snakes[name]
            if not snake.alive:
                return  # if snake is dead, we don't need to update it  
            lastkey = snake.lastkey

            assert lastkey in "wasd" or lastkey == ""
        except AssertionError:
            logger.error("Invalid key <%s> pressed. Valid keys: w,a,s,d", lastkey)
            snake.move(self.map, snake.direction)
            return False

        # Update position
        snake.move(
            self.map,
            key2direction(snake.lastkey)
            if snake.lastkey in "wasd" and snake.lastkey != ""
            else snake.direction,
        )

        return True

    def kill_snake(self, name):
        logger.info("[step=%s] Snake <%s> has died", self._step, name)
        self._snakes[name].kill()

        if all([not snake.alive for snake in self._snakes.values()]):
            # if all snakes are dead, we stop the game
            self.stop()

    def collision(self):
        if (
            not self._running
        ):  # if game is not running, we don't need to check collisions
            return

        for name1, snake1 in self._snakes.items():
            if not snake1.alive:
                continue
            # check collisions between snakes
            for name2, snake2 in self._snakes.items():
                if not snake2.alive:
                    continue
                if name1 != name2 and snake2.collision(snake1.head):
                    self.kill_snake(name1)
                    snake2.score += KILL_SNAKE_POINTS

            # check collisions with the map
            if self.map.is_blocked(snake1.head, traverse=snake1._traverse):
                logger.info(
                    "Snake <%s> has crashed against a wall/rock at %s",
                    name1,
                    snake1.head,
                )
                self.kill_snake(name1)

            # check collisions with the food
            if self.map.get_tile(snake1.head) in [Tiles.FOOD, Tiles.SUPER]:
                what_i_ate = self.map.eat_food(snake1.head)
                if what_i_ate == Tiles.FOOD:
                    logger.debug("Snake <%s> ate food", name1)
                    snake1.score += 1
                    snake1.grow()
                    self.map.spawn_food()
                elif what_i_ate == Tiles.SUPER:
                    kind = random.choice(
                        [
                            SuperFood.POINTS,
                            SuperFood.LENGTH,
                            SuperFood.RANGE,
                            SuperFood.TRAVERSE,
                        ]
                    )
                    logger.debug("Snake <%s> ate <%s> at position (%s)", name1, kind.name, snake1.head)

                    if kind == SuperFood.POINTS:
                        points = random.randint(-5, 10)
                        snake1.score += points 
                        logger.debug("Snake ate superfood and scored: %s", points)
                    elif kind == SuperFood.LENGTH:
                        extra = random.randint(-2, 2)
                        snake1.grow(extra)
                        logger.debug("Snake ate superfood and grew: %s", extra)
                    elif kind == SuperFood.RANGE:
                        snake1.range += random.randint(-2, 2)
                        snake1.range = min(max(snake1.range, 2), 6) # range between 2 and 6
                        logger.debug("Snake ate superfood and range changed to: %s", snake1.range)
                    elif kind == SuperFood.TRAVERSE:
                        snake1._traverse = not snake1._traverse
                        logger.debug("Snake ate superfood and traverse is: %s", snake1._traverse)

    async def next_frame(self):
        await asyncio.sleep(1.0 / self._game_speed)

        if not self._running:
            logger.info("Waiting for player 1")
            return

        self._step += 1
        if self._step == self._timeout:
            self.stop()

        if self._step % 100 == 0:
            self.map.spawn_food(Tiles.SUPER)

            for name, snake in self._snakes.items():
                logger.debug(f"[{self._step}] SCORE {name}: {snake.score}")

        for name, snake in self._snakes.items():
            if not snake.alive:
                continue
            self.update_snake(name)

        self.collision()

        self._state = {
            "food": self.map.food,
            "players": [snake for snake in self._snakes],
            "step": self._step,
            "timeout": self._timeout,
            "snakes": [
                {
                    "name": name,
                    "body": snake.body[::-1],
                    "sight": snake.sight(self.map, self._snakes.values()),
                    "score": snake.score,
                    "range": snake.range,
                    "traverse": snake._traverse,
                }
                for name, snake in self._snakes.items()
                if snake.alive
            ],
        }

        if all([not snake.alive for snake in self._snakes.values()]):
            self.stop()

        return self._state

    def info(self):
        return {
            "size": self.map.size,
            "map": self.map.map,
            "fps": self._game_speed,
            "timeout": self._timeout,
            "level": self.map.level,
        }
