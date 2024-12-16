from sprite import Sprite
from consts import PEACH_SPRITE_PATH, PEACH_SPAWN_POSITION, PEACH_COLLIDER

class Peach(Sprite):
    """
        The Peach class is responsible for managing the peach entity in the game world
       
        The class has the following attributes:
           
    """

    def __init__(self):
        """ Initializes a new instance of the Peach class"""
        super().__init__(PEACH_SPRITE_PATH, PEACH_SPAWN_POSITION, PEACH_COLLIDER)


