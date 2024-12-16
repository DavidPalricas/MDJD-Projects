import pygame as pg
import pygame.sprite as pgs
from animator import Animator
class Sprite:
    """ The Sprite class is responsible for managing the sprites in the game world

        The class has the following attributes:
            - image: The image of the sprite
            - dimensions: The dimensions of the sprite
            - rect: The rectangle of the sprite
            - add_internal: The add_internal method of the sprite group
            - remove_internal: The remove_internal method of the sprite group
            - is_on_ground: A boolean that indicates whether the sprite is on the ground
            - speed: The speed of the sprite
            - states: The states of the sprite
            - transitions: The transitions between the sprite's states
            - fsm: The finite state machine of the sprite
            - name: The name of the sprite
            - animator: The animator of the sprite
    """

    def __init__(self,sprite_path, position, collider): 
        """ 
            Initializes a new instance of the Sprite class, loads the sprite image file , sets the dimensions of the sprite, and creates a rectangle for the sprite

            Args:
                - sprite_path (str): The path to the sprite image file
                - position (tuple): The position of the sprite
                - collider (tuple): The collider of the sprite
        """   

        self.image = pg.image.load(sprite_path).convert_alpha()
        self.dimensions = (self.image.get_width(), self.image.get_height())

        self.rect = pgs.Rect(position, collider)
        
        # The add_internal and remove_internal methods are implemented to be possible for add and remove instance of the Sprite class from the sprite group define in the game.py
        self.add_internal = pgs.Group.add
        self.remove_internal = pgs.Group.remove

        self.is_on_ground = True
        self.speed = None
        self.states = None
        self.transitions = None
        self.fsm = None
        self.name = None
        self.animator = Animator()

    def update(self):
        """ The update method is responsible for updating the sprite
            This method must be implemented even if it does nothing, for  instance of the Sprite class could be updated by  the sprite group define in the game.py
        """
        pass  

    def set_states(self) :
        """
            The set_states method is responsible for setting the states of the entity
            The method should be overridden by the derived classes
        """

        raise NotImplementedError
    
    def set_transitions(self):
        """
            The set_transitions method is responsible for setting the transitions between the entity's states
            The method should be overridden by the derived classes
        """
        
        raise NotImplementedError
 