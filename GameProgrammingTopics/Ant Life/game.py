import pygame as pg
from game_map import GameMap
from ant import Ant
from consts import WINDOW_WIDTH, WINDOW_HEIGHT

def update_display(window, clock,game_map,ants):
    """ The update_display function updates the display of the game.

        Args:
        - window: The window of the game.
        - clock: The clock of the game.
    """

    window.fill((0, 0, 0))
    game_map.draw(window)

    for ant in ants:
        ant.draw(window)

    pg.display.update()
    clock.tick(60)

def event_handler():
    """ The event_handler function is responsible for handling the events in the game, such as quitting the game.

        Returns:
        - running: A flag indicating whether the game is running or not.
    """

    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
    return True


def move_ants(ants,game_map):
    """ The move_ants function is responsible for moving the ants in the game.

        Args:
        - ants: The list of ants in the game.
        - game_map: The game map.
    """

    for ant in ants:
        ant.move(game_map)
        if ant.reproduce:
            ants.append(Ant())
            ant.reproduce = False

        if ant.fsm.current == ant.dead:
            ants.remove(ant)
            del ant

def game_loop(window, clock):

    running = True
    
    game_map = GameMap()
    game_map.draw(window)
    
    ants = []
    ant = Ant()
    ant.draw(window)
    ants.append(ant)

    while running:
        running = event_handler()

        move_ants(ants,game_map)
   
        if len(ants) == 0:
            running = False
            
        update_display(window,clock,game_map,ants)
            

    pg.quit()


def setup_pygame():
    """ The setup_sprites function creates the games sprites and adds it to the all_sprites group.
          
        Returns:
            - all_sprites: The group of all the sprites in the game.
    """
    pg.init()
    window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pg.display.set_caption("Ant Life")
    clock = pg.time.Clock()

    return window, clock


def main():

    window,clock = setup_pygame()

    game_loop(window, clock)


if __name__ == "__main__":
    main()