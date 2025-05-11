import pygame as pg
import os

from consts import FLOOR_TILE_DIMENSIONS, FLOOR_BLOCK, FLOOR_BLOCK_SPRITE_PATH, PEACH_SPRITE_PATH

class Map:
    """ The Map class is responsible for creating the game map and drawing it on the screen.

        This is implemented as a singleton to ensure only one instance exists, during the game.

        Attributes:
            - instance (Map): The instance of the Map class
            - tile_set (Surface): The tile set of the game map
            - tile_per_row (int): The number of tiles per row
            - tile_per_col (int): The number of tiles per column
            - map (list of lists): The game map
            - floor_blocks_colliders (list): The list of floor block colliders
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """ The __new__ method is responsible for creating a new instance of the Map class if it does not exist.
            In this method we ensure that only one instance of the Map class exists during the game, to adopt the singleton design pattern.
            This method is called before the __init__ method (constructor of the class)

            Args:
                - cls (Map): The class of the instance
                - *args: The arguments
                - **kwargs: The keyword arguments

            Returns:
                - Map: The instance of the Map class
        """

        if cls._instance is None:
            cls._instance = super(Map, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self) -> None:
        """ Initializes a new instance of the Map class and sets up the game map attributes
            If the instance of the Map class exists, this method does not create a new instance (singleton design pattern)  
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.floor_block_sprite = pg.image.load(os.path.join(os.path.dirname(__file__), FLOOR_BLOCK_SPRITE_PATH)).convert_alpha()
        self.peach = pg.image.load(os.path.join(os.path.dirname(__file__), PEACH_SPRITE_PATH)).convert_alpha()

        self.map = [[],
                    [],
                    [],
                    [],
                    [],
                    [None] * 60 + [FLOOR_BLOCK] * 10,
                    [],
                    [], 
                    [None] * 47 + [FLOOR_BLOCK] * 10 + [None] * 16 + [FLOOR_BLOCK] * 10,
                    [], 
                    [],
                    [None] * 34 + [FLOOR_BLOCK] * 10 + [None] * 16 + [FLOOR_BLOCK] * 10, 
                    [],
                    [None] * 90,
                    [FLOOR_BLOCK] * 31 + [None] * 56 + [FLOOR_BLOCK] * 5,
        ]

        self.floor_blocks_colliders = []
        self.peach_collider = None
        self._initialized = True

    def draw(self, window, camera):
        """ The draw method is responsible for drawing the game map on the screen.
            It iterates over the map list and draws the tiles in their positions (FLOOR_BLOCK) on the screen.
            The list with the floor block colliders is also updated in this method.

            Args:
                - window (Surface): The game window
                - camera (Camera): The camera object
        """
        for row_index, row in enumerate(self.map):
            for column_index, floor_block__index in enumerate(row):

                if floor_block__index is FLOOR_BLOCK:  
                    x, y = column_index * FLOOR_TILE_DIMENSIONS["WIDTH"], row_index * FLOOR_TILE_DIMENSIONS["HEIGHT"]

                    floor_block_collider = pg.Rect(x, y, FLOOR_TILE_DIMENSIONS["WIDTH"], FLOOR_TILE_DIMENSIONS["HEIGHT"])

                    self.floor_blocks_colliders.append(floor_block_collider)

                    window.blit(self.floor_block_sprite, camera.apply(floor_block_collider))


    def get_peach_position(self):
        """ The get_peach_position method is responsible for finding the position of the peach sprite in the map.
            It iterates over the map list and returns the position of the peach sprite.

            Returns:
                - tuple: The position of the peach sprite (x, y)
        """
        for row_index, row in enumerate(self.map):
            for column_index, floor_block__index in enumerate(row):
                if floor_block__index is PEACH_SPRITE_PATH:
                    x, y = column_index * FLOOR_TILE_DIMENSIONS["WIDTH"], row_index * FLOOR_TILE_DIMENSIONS["HEIGHT"]
                    return (x, y)
        return None