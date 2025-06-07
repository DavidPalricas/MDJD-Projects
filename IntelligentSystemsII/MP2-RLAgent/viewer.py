import argparse
import asyncio
import json
import logging
import os
import sys
import pprint

from consts import Tiles
import pygame
import websockets

logging.basicConfig(level=logging.DEBUG)
logger_websockets = logging.getLogger("websockets")
logger_websockets.setLevel(logging.WARN)

logger = logging.getLogger("Viewer")
logger.setLevel(logging.DEBUG)

from viewer.common import Directions, Food, Snake, Stone, ScoreBoard, get_direction
from viewer.sprites import (
    Info,
    GameStateSprite,
    GameInfoSprite,
    SnakeSprite,
    FoodSprite,
    StoneSprite,
    ScoreBoardSprite,
)


async def main_loop(q, SCALE):
    while True:
        await main(SCALE)


def should_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit


async def main(SCALE):
    logging.info("Waiting for map information from server")
    while True:
        try:
            should_quit()
            state = q.get_nowait()  # first state message includes map information
            break
        except asyncio.queues.QueueEmpty:
            await asyncio.sleep(0.1)

    logging.debug("Initial game status: %s", state)
    newgame_json = json.loads(state)

    new_game = True
    GAME_SPEED = newgame_json["fps"]
    WIDTH, HEIGHT = newgame_json["size"]
    MAP = newgame_json["map"]

    display = pygame.display.set_mode((SCALE * WIDTH, SCALE * HEIGHT))

    all_sprites = pygame.sprite.Group()
    snake_sprites = pygame.sprite.Group()
    food_sprites = pygame.sprite.Group()
    stone_sprites = pygame.sprite.Group()
    prev_foods = None

    step_info = Info(text="0")

    while True:
        should_quit()

        try:
            state = json.loads(q.get_nowait())
            pprint.pprint(state)

            if "snakes" in state and "food" in state:
                snakes_update = state["snakes"]
                foods_update = state["food"]
                foods_update = state["food"]
                step_info.text = f"Step: {state['step']}"
            elif "highscores" in state:
                all_sprites.add(
                    ScoreBoardSprite(
                        ScoreBoard(
                            highscores=[(p[0], p[1]) for p in state["highscores"]]
                        ),
                        WIDTH,
                        HEIGHT,
                        SCALE,
                    )
                )
            else:
                new_game = True

        except asyncio.queues.QueueEmpty:
            await asyncio.sleep(0.1 / GAME_SPEED)
            continue

        # Update Foods
        if new_game or prev_foods != foods_update:
            food_sprites.empty()

            foods = {
                f"{food}": Food(pos=(food[0], food[1]), is_super=food[2] == "SUPER")
                for food in foods_update
            }
            food_sprites.add(
                [FoodSprite(food, WIDTH, HEIGHT, SCALE) for food in foods.values()]
            )
            prev_foods = foods_update

        # Update Stones
        if new_game:
            for x, col in enumerate(MAP):
                for y, pos in enumerate(col):
                    if pos == Tiles.STONE:
                        stone_sprites.add(
                            StoneSprite(Stone(pos=(x, y)), WIDTH, HEIGHT, SCALE)
                        )

        # Update Snakes
        if new_game or not all(
            [
                snake["name"] in [s.name for s in snakes.values()]
                for snake in snakes_update
            ]
        ):
            all_sprites.empty()
            snake_sprites.empty()

            snakes = {
                snake["name"]: Snake(
                    body=snake["body"],
                    direction=Directions.RIGHT,
                    score=snake["score"],
                    name=snake["name"],
                    traverse=snake["traverse"],
                )
                for snake in snakes_update
            }

            all_sprites.add(GameInfoSprite(step_info, WIDTH-len(step_info.text), 0, WIDTH, SCALE))

            all_sprites.add(
                [
                    GameStateSprite(snake, i, WIDTH, HEIGHT, SCALE)
                    for i, snake in enumerate(snakes.values())
                ]
            )

            snake_sprites.add(
                [SnakeSprite(snake, WIDTH, HEIGHT, SCALE) for snake in snakes.values()]
            )

        else:
            for snake in snakes_update:
                snakes[snake["name"]].body = snake["body"]
                head = snake["body"][0]
                neck = snake["body"][1]
                snakes[snake["name"]].direction = get_direction(
                    head[0], head[1], neck[0], neck[1], HEIGHT=HEIGHT, WIDTH=WIDTH
                )
                snakes[snake["name"]].score = snake["score"]
                snakes[snake["name"]].traverse = snake["traverse"]

            # Remove dead snakes
            for snake in snakes.values():
                if snake.name not in [s["name"] for s in snakes_update]:
                    snake_sprites.remove(
                        [s for s in snake_sprites if s.snake.name == snake.name]
                    )

        new_game = False

        # Render Window
        display.fill("white")

        try:
            all_sprites.update()
            snake_sprites.update()
            food_sprites.update()
            stone_sprites.update()
        except Exception as e:
            logging.error(e)
        stone_sprites.draw(display)
        food_sprites.draw(display)
        all_sprites.draw(display)
        snake_sprites.draw(display)

        # update window
        pygame.display.flip()


async def messages_handler(ws_path, queue):
    async with websockets.connect(ws_path) as websocket:
        await websocket.send(json.dumps({"cmd": "join"}))

        while True:
            r = await websocket.recv()
            queue.put_nowait(r)


if __name__ == "__main__":
    SERVER = os.environ.get("SERVER", "localhost")
    PORT = os.environ.get("PORT", "8000")

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="IP address of the server", default=SERVER)
    parser.add_argument(
        "--scale", help="reduce size of window by x times", type=int, default=1
    )
    parser.add_argument("--port", help="TCP port", type=int, default=PORT)
    args = parser.parse_args()
    SCALE = 32 * (1 / args.scale)

    LOOP = asyncio.get_event_loop()
    pygame.init()
    pygame.font.init()
    q: asyncio.Queue = asyncio.Queue()

    ws_path = f"ws://{args.server}:{args.port}/viewer"

    try:
        LOOP.run_until_complete(
            asyncio.gather(messages_handler(ws_path, q), main_loop(q, SCALE=SCALE))
        )
    finally:
        LOOP.stop()
