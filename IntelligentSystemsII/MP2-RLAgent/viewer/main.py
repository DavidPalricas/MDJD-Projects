import json
import logging
import sys
import pygame
import os
import argparse
import asyncio
import websockets

from common import Directions, Food, Snake, ScoreBoard, get_direction

from sprites import SnakeSprite, FoodSprite, ScoreBoardSprite


async def main_loop(q):
    while True:
        await main()


async def main(SCALE=32):
    logging.info("Waiting for map information from server")
    state = await q.get()  # first state message includes map information
    logging.debug("Initial game status: %s", state)
    newgame_json = json.loads(state)

    new_game = True
    GAME_SPEED = newgame_json["fps"]
    WIDTH, HEIGHT = newgame_json["size"]

    display = pygame.display.set_mode((SCALE * WIDTH, SCALE * HEIGHT))

    all_sprites = pygame.sprite.Group()
    food_sprites = pygame.sprite.Group()
    prev_foods = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit(0)

        # Render Window
        display.fill("white")

        try:
            all_sprites.update()
            food_sprites.update()
        except Exception as e:
            logging.error(e)
        food_sprites.draw(display)
        all_sprites.draw(display)

        # update window
        pygame.display.flip()

        try:
            state = json.loads(q.get_nowait())
            import pprint

            pprint.pprint(state)

            if "snakes" in state and "food" in state:
                snakes_update = state["snakes"]
                if new_game:
                    foods_update = state["food"]
                prev_foods = foods_update
                foods_update = state["food"]
            else:
                print("Show SCOREBOARD")

        except asyncio.queues.QueueEmpty:
            await asyncio.sleep(1.0 / GAME_SPEED)
            continue

        if new_game:
            snakes = {
                snake["name"]: Snake(body=snake["body"], direction=Directions.RIGHT)
                for snake in snakes_update
            }

            all_sprites.add(
                [SnakeSprite(snake, WIDTH, HEIGHT, SCALE) for snake in snakes.values()]
            )
            new_game = False
        else:
            for snake in snakes_update:
                snakes[snake["name"]].body = snake["body"]
                head = snake["body"][0]
                neck = snake["body"][1]
                snakes[snake["name"]].direction = get_direction(
                    head[0], head[1], neck[0], neck[1], HEIGHT=HEIGHT, WIDTH=WIDTH
                )

        if prev_foods != foods_update:
            print("FOODS UPDATE")
            food_sprites.empty()
            foods = {f"{food}": Food(pos=(food[0], food[1])) for food in foods_update}
            food_sprites.add(
                [FoodSprite(food, WIDTH, HEIGHT, SCALE) for food in foods.values()]
            )


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
    SCALE = args.scale

    LOOP = asyncio.get_event_loop()
    pygame.init()
    pygame.font.init()
    q: asyncio.Queue = asyncio.Queue()

    ws_path = f"ws://{args.server}:{args.port}/viewer"

    try:
        LOOP.run_until_complete(
            asyncio.gather(messages_handler(ws_path, q), main_loop(q))
        )
    finally:
        LOOP.stop()
