import pygame as pg
import os
from consts import PLAYER_PATHS, KIRBY_PATHS

class Animator:
    """The Animator class is responsible for playing animations for the entities. It uses the Flyweight pattern to store shared instances of animations.

       The class has the following attributes:
         - _animations: A dictionary that stores the shared instances of animations (Flyweight storage)
         - current_animation: The current animation that is being played
         - animation_index: The index of the current frame in the animation
         - animation_delay: The delay between each frame in milliseconds
         - animations_frames: The frames of the current animation
         - last_update: The time of the last update in milliseconds 
    """

    _animations = {}

    def __init__(self) -> None:
        """ 
           Initializes a new instance of the Animator class    
        """
        
        self.current_animation = "idle"
        self.animation_index = 0
        self.animation_delay = 100
        self.animations_frames = None
        self.last_update = 0
               
    def play_animation(self,state,entity):
     """The play_animation method is responsible for playing the animation for the given state
        
        Args:
            - state (str): The state of the entity (e.g. idle, walk, jump)
            - entity (Entity): The entity that the animation belongs to
    """
     
     # Check if the current animation is different from the new animation
     if self.current_animation != state:
        self.current_animation = state

         # Reset the animation
        self.animation_index = 0 
        self.last_update = 0

        # Load the animation frames for the new state
        self.animations_frames = self.load_animation_frames(entity, state) 
     
     # Get the current time in milliseconds since Pygame was initialized
     now = pg.time.get_ticks()
    
    # Check if the time elapsed since the last update is greater than the animation delay
     if now - self.last_update > self.animation_delay:
     
        self.last_update = now
        
        # Increment the animation index and wrap it around using modulo to stay within the valid range
        self.animation_index = (self.animation_index + 1) % len(self.animations_frames)
        
        entity.image = self.animations_frames[self.animation_index]

        if not entity.turned_right:
            entity.image = pg.transform.flip(entity.image, True, False)
    
    def load_animation_frames(self, entity, state):
        """The load_animation_frames method is responsible for loading the animation frames for the given state

           It first checks if the frames are already stored in the animations_storage dictionary. If not, it loads the frames from the sprite sheet and saves them in the dictionary for future use.

            Args:
                - entity (Entity): The entity that the animation belongs to
                - state (str): The state of the entity (e.g. idle, walk, jump)

            Returns:
                - frames (list): A list of the animation frames     
        """

        key = f"{entity.name}_{state}"  

        if key in self._animations:
            return self._animations[key] 
        
        if entity.name == "Bowser":
            image_path = os.path.join(os.path.dirname(__file__),  f"{PLAYER_PATHS["ANIMATOR_BASE"]}/{state}/{entity.name}_{state}.png")
        else:
            image_path = os.path.join(os.path.dirname(__file__), f"{KIRBY_PATHS["ANIMATOR_BASE"]}/{state}/{entity.name}_{state}.png")

        new_image = pg.image.load(image_path).convert_alpha()

        # Check if the image is a tileset (based on the width of the original sprite) or if it's a single frame

        frames = self.split_tileset(new_image, entity.dimensions[0]) if new_image.get_width() > entity.dimensions[0] else [pg.transform.scale(new_image, (entity.dimensions[0], new_image.get_height()))]

        # Save the frames in the animations_storage dictionary
        self._animations[key] = frames
        
        return frames

    def split_tileset(self, tile_set, sprite_width,):
        """The split_tileset method is responsible for splitting the tileset into individual frames

            Args:
                - tile_set (Surface): The tileset image
                - sprite_width (int): The width of the original sprite

            Returns:
                - frames (list): A list of the individual frames
        """

        frames = []
        total_width = tile_set.get_width()
        total_height = tile_set.get_height()

        num_frames = total_width // sprite_width
        remainder = total_width % sprite_width

        for i in range(num_frames):
            frame = tile_set.subsurface((i * sprite_width, 0, sprite_width, total_height))
            frame = pg.transform.scale(frame, (sprite_width, total_height))
            frames.append(frame)

        # Add the remianing frame to animation
        if remainder > 0:
            frame = tile_set.subsurface((num_frames * sprite_width, 0, remainder, total_height))
            frame = pg.transform.scale(frame, (sprite_width, total_height))
            frames.append(frame)

        return frames