import pygame
from collections import deque

from .spritesheet import SpriteSheet, CELL_SIZE
from .common import Directions, Snake, Food, Stone, ScoreBoard, get_direction

from dataclasses import dataclass

@dataclass
class Info:
    text: str

class GameInfoSprite(pygame.sprite.Sprite):
    def __init__(self, info: Info, column: int, line: int, WIDTH, SCALE):
        self.font = pygame.font.Font(None, int(SCALE))
        super().__init__()

        self.info = info
        self.line = line
        self.column = column
        self.image = pygame.Surface([WIDTH * SCALE, (self.line + 1) * SCALE])
        print(self.image.get_size())
        self.image.set_colorkey("white")
        self.rect = self.image.get_rect()
        self.SCALE = SCALE

    def update(self):
        self.image.fill("white")
        self.image.set_colorkey("white")

        self.image.blit(
            self.font.render(
                self.info.text,
                True,
                "purple",
                "white",
            ),
            (self.column * self.SCALE, self.line * self.SCALE),
        )

class GameStateSprite(pygame.sprite.Sprite):
    def __init__(self, player: Snake, pos: int, WIDTH, HEIGHT, SCALE):
        self.font = pygame.font.Font(None, int(SCALE))
        super().__init__()

        self.player = player
        self.pos = pos
        self.image = pygame.Surface([WIDTH * SCALE, (self.pos + 1) * SCALE])
        self.image.set_colorkey("white")
        self.rect = self.image.get_rect()
        self.SCALE = SCALE

    def update(self):
        self.image.fill("white")
        self.image.set_colorkey("white")

        traverse = "[T]" if self.player.traverse else ""

        self.image.blit(
            self.font.render(
                f"{self.player.name} {traverse}: {self.player.score}",
                True,
                "purple",
                "white",
            ),
            (0, self.pos * self.SCALE),
        )


class ScoreBoardSprite(pygame.sprite.Sprite):
    def __init__(self, scoreboard, WIDTH, HEIGHT, SCALE):
        self.font = pygame.font.Font(None, int(SCALE))
        super().__init__()

        self.highscores = sorted(
            scoreboard.highscores, key=lambda s: s[1], reverse=True
        )

        self.image = pygame.Surface([WIDTH * SCALE, HEIGHT * SCALE])
        self.rect = self.image.get_rect()
        self.SCALE = SCALE

    def update(self):
        self.image.fill("white")
        self.image.set_colorkey("white")

        scale = lambda t: (int(t[0] * self.SCALE), int(t[1] * self.SCALE))

        table_surface = pygame.Surface(scale((15, 16)))
        table_surface.fill((70, 70, 70))

        table_surface.blit(
            self.font.render("THE 10 BEST PLAYERS", True, "white"), scale((3, 1))
        )

        table_surface.blit(self.font.render("RANK", True, "orange"), scale((1, 3)))
        table_surface.blit(self.font.render("SCORE", True, "orange"), scale((5, 3)))
        table_surface.blit(self.font.render("NAME", True, "orange"), scale((9, 3)))

        colors = deque(
            [
                (255, 99, 71),  # Tomato
                (135, 206, 235),  # Sky Blue
                (50, 205, 50),  # Lime Green
                (255, 165, 0),  # Orange
                (147, 112, 219), # Medium Purple
            ]  
        )

        RANKS = [
            "1ST",
            "2ND",
            "3RD",
            "4TH",
            "5TH",
            "6TH",
            "7TH",
            "8TH",
            "9TH",
            "10TH",
        ]

        for i, highscore in enumerate(self.highscores):
            colors.rotate(1)
            table_surface.blit(
                self.font.render(RANKS[i], True, colors[0]),
                scale((1, i + 5)),
            )
            table_surface.blit(
                self.font.render(str(highscore[1]), True, colors[0]),
                scale((5, i + 5)),
            )
            table_surface.blit(
                self.font.render(highscore[0], True, colors[0]),
                scale((9, i + 5)),
            )

        # center in screen
        self.image.blit(
            table_surface,
            (
                (self.image.get_width() - table_surface.get_width()) / 2,
                (self.image.get_height() - table_surface.get_height()) / 2,
            ),
        )


class StoneSprite(pygame.sprite.Sprite):
    def __init__(self, stone: Stone, WIDTH, HEIGHT, SCALE):
        super().__init__()

        self.stone = stone
        self.SCALE = SCALE

        rect = pygame.Rect((0, 3 * SCALE, SCALE, SCALE))
        self.stone_image = pygame.Surface(rect.size)

        self.stone_image.fill("black")

        self.image = pygame.Surface([WIDTH * SCALE, HEIGHT * SCALE])
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        self.image.fill("white")
        self.image.set_colorkey("white")

        # Render Stone
        self.image.blit(
            self.stone_image,
            (self.SCALE * self.stone.pos[0], self.SCALE * self.stone.pos[1]),
        )


class FoodSprite(pygame.sprite.Sprite):
    def __init__(self, food: Food, WIDTH, HEIGHT, SCALE):
        super().__init__()

        if food.is_super:
            FOOD_SPRITESHEET = SpriteSheet("data/snake-graphics-bw.png")
        else:
            FOOD_SPRITESHEET = SpriteSheet("data/snake-graphics.png")

        self.food = food
        self.SCALE = SCALE

        food_image_rect = (0, 3 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.food_image = FOOD_SPRITESHEET.image_at(food_image_rect, -1)
        self.food_image = pygame.transform.scale(self.food_image, (SCALE, SCALE))

        self.image = pygame.Surface([WIDTH * SCALE, HEIGHT * SCALE])
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        self.image.fill("white")
        self.image.set_colorkey("white")

        # Render Food
        self.image.blit(
            self.food_image,
            (self.SCALE * self.food.pos[0], self.SCALE * self.food.pos[1]),
        )


class SnakeSprite(pygame.sprite.Sprite):
    def __init__(self, snake: Snake, WIDTH, HEIGHT, SCALE):
        super().__init__()

        SNAKE_SPRITESHEET = SpriteSheet("data/snake-graphics.png")

        self.snake = snake
        self.HEIGHT = HEIGHT
        self.WIDTH = WIDTH
        self.SCALE = SCALE

        snake_map = {
            ("head", Directions.UP): (3, 0),
            ("head", Directions.RIGHT): (4, 0),
            ("head", Directions.LEFT): (3, 1),
            ("head", Directions.DOWN): (4, 1),
            (Directions.UP, Directions.RIGHT): (0, 0),
            (Directions.LEFT, Directions.DOWN): (0, 0),
            (Directions.DOWN, Directions.RIGHT): (0, 1),
            (Directions.LEFT, Directions.UP): (0, 1),
            (Directions.LEFT, Directions.LEFT): (1, 0),
            (Directions.RIGHT, Directions.RIGHT): (1, 0),
            (Directions.RIGHT, Directions.DOWN): (2, 0),
            (Directions.UP, Directions.LEFT): (2, 0),
            (Directions.UP, Directions.UP): (2, 1),
            (Directions.DOWN, Directions.DOWN): (2, 1),
            (Directions.RIGHT, Directions.UP): (2, 2),
            (Directions.DOWN, Directions.LEFT): (2, 2),
            ("tail", Directions.UP): (4, 3),
            ("tail", Directions.DOWN): (3, 2),
            ("tail", Directions.RIGHT): (3, 3),
            ("tail", Directions.LEFT): (4, 2),
        }

        # Load and resize images to SCALE
        self.snake_images = {
            name: pygame.transform.scale(
                SNAKE_SPRITESHEET.image_at(
                    (a * CELL_SIZE, b * CELL_SIZE, CELL_SIZE, CELL_SIZE), -1
                ),
                (SCALE, SCALE),
            )
            for (name, (a, b)) in snake_map.items()
        }

        self.image = pygame.Surface([WIDTH * SCALE, HEIGHT * SCALE])
        self.update()
        self.rect = self.image.get_rect()

    def update(self):
        self.image.fill("white")
        self.image.set_colorkey("white")

        # Get Head
        prev_x, prev_y = self.snake.body[0]
        prev_dir = None

        # Walk from 1st body position towards tail
        for x, y in self.snake.body[1:]:
            dir = get_direction(x, y, prev_x, prev_y, self.HEIGHT, self.WIDTH)
            if prev_dir is None:
                image = ("head", self.snake.direction)
            else:
                image = (prev_dir, dir)

            # blit previous body part now that we now directions taken
            if image in self.snake_images:  # TODO remove this check
                self.image.blit(
                    self.snake_images[image], (self.SCALE * prev_x, self.SCALE * prev_y)
                )

            prev_x, prev_y = x, y
            prev_dir = dir

        # Finally blit tail
        self.image.blit(
            self.snake_images[("tail", prev_dir)],
            (self.SCALE * prev_x, self.SCALE * prev_y),
        )
