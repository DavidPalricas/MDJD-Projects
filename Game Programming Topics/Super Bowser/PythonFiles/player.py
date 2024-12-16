import pygame as pg
from sprite import Sprite
import finite_state_machine as fsm
import os
from command import InputHandler
from consts import GRAVITY, PLAYER_SPAWN_POSITION , PLAYER_COLLIDER, PLAYER_MOVEMENT, PLAYER_PATHS


class Player(Sprite):
    """
        The Player class is responsible for managing the player entity in the game world
       
        The class has the following attributes:
            - jump_speed: The speed of the player's jump
            - sound_player: The sound player of the player
            - last_key_pressed: The last key pressed by the player
    """

    def __init__(self): 
        """
            Initializes a new instance of the Player class, and calls the constructor of the Entity class (the parent class)
            Loads the sprite image for the player
            Sets up the player's attributes and the attributes inherited from the Entity class including the FSM and its states

            Args:
                - collider (tuple): The collider of the player
        """

        if not hasattr(self, 'initialized'):
            sprite_path = os.path.join(os.path.dirname(__file__), PLAYER_PATHS["IDLE"])
            super().__init__(sprite_path,PLAYER_SPAWN_POSITION, PLAYER_COLLIDER)
            
            self.is_on_ground = True
            self.turned_right = True
            self.name = "Bowser"
            self.velocity_x = 0
            self.velocity_y = 0

            # Initialize FSM and states
            self.fsm = fsm.FSM(self.set_states(), self.set_transitions())

            self.input_handler = InputHandler()


    def set_states(self):
        """ The set_states method is responsible for setting the states of the player e.g. (idle, walk, jump)
            Returns:
                - states (list): A list of the player's states
        """
        self.idle = fsm.Idle()
        self.walk = fsm.Walk()
        self.jump = fsm.Jump()

        return [self.idle, self.walk, self.jump]
    
    def set_transitions(self):
        """ The set_transitions method is responsible for setting the transitions between the player's states

            Returns:
                - transitions (dict): A dictionary of the player's transitions
        """
        return {
            "walk": fsm.Transition(self.idle, self.walk),
            "jump": fsm.Transition(self.idle, self.jump),
            "idle": fsm.Transition(self.walk, self.idle),
            "fall": fsm.Transition(self.jump, self.idle)
        }
                
    def update(self):
        """ The update method is responsible for move the player based on pressed keys, applying gravity, and playing animations
           Calling respectively this methods: move, apply_gravity, play_animation (from the animator attribute)
        """
        pressed_keys = pg.key.get_pressed()
    
        if not self.is_on_ground:
            self.apply_gravity()
      

        self.move(pressed_keys)
        
        self.animator.play_animation(self.fsm.current.name, self )

    def move(self, keys):
        """ The move method is responsible for moving the player based on the pressed keys and sets the player idle if no movement key is pressed.
            If the player presses the space key, W key, or UP key, the initiate_jump method is called to make the player jump.
            If the player presses the D key or RIGHT key, the move_right method is called to move the player to the right.
            If the player presses the A key or LEFT key, the move_left method is called to move the player to the left.

            Args:
                - keys (list): A list of the pressed keys
        """
        handled_movement = False

        for key, command in self.input_handler.commands.items():
            if keys[key]:
                command.execute(self)
                handled_movement = True

        # Transition to idle state if no movement key is pressed
        if not handled_movement:
            self.velocity_x *= PLAYER_MOVEMENT["FRICTION"]
            self.fsm.update("idle", self)


        self.rect.x += self.velocity_x  if self.rect.x + self.velocity_x > 0 else 0

        self.rect.y += self.velocity_y

    def move_right(self):
        """ The move_right method is responsible for moving the player to the right  and sprite flip.
            It also updates the player's state to walk if it's not already in that state.
        """
        if self.fsm.current != self.walk:
            self.fsm.update("walk", self)

        self.velocity_x = PLAYER_MOVEMENT["SPEED"]

        if not self.turned_right:
            self.image = pg.transform.flip(self.image, True, False)
            self.turned_right = True

    def move_left(self):
        """ The move_left method is responsible for moving the player to the left  and sprite flip.
            It also updates the player's state to walk if it's not already in that state.
        """
        if self.fsm.current != self.walk:
            self.fsm.update("walk", self)
            
        self.velocity_x = -PLAYER_MOVEMENT["SPEED"]

        if self.turned_right:
            self.image = pg.transform.flip(self.image, True, False)
            self.turned_right = False

    def initiate_jump(self):
        """ The initiate_jump method is responsible for making the player jump if it is on the ground.
            It also updates the player's state to jump and plays the jump sound effect.
        """

        if self.is_on_ground:
            self.fsm.update("jump", self)
            self.velocity_y = -PLAYER_MOVEMENT["JUMP_SPEED"]

    def apply_gravity(self):
        """ The apply_gravity method is responsible for applying gravity to the player, making it fall to the ground"""

        self.velocity_y += GRAVITY  
         
        if self.velocity_y > 0:    
            self.fsm.update("fall", self)

    def respawn(self):
        """ The respawn method is responsible for respawning the player at the starting position"""
        self.rect.x = PLAYER_SPAWN_POSITION[0]
        self.rect.y = PLAYER_SPAWN_POSITION[1]

    def quit_game(self):
        """ The quit_game method is responsible for quitting the game"""
        pg.quit()