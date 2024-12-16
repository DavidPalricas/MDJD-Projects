import os
import copy
import pygame as pg
import finite_state_machine as fsm
from sprite  import Sprite
from consts import KIRBY_COLLIDER, KIRBY_PATHS, KIRBY_MOVEMENT

class Kirby(Sprite):
    def __init__(self, position): 
        """
        Initializes a new instance of the Kirby class, calling the Entity and Prototype constructors.
        """
        sprite_path = os.path.join(os.path.dirname(__file__), KIRBY_PATHS["IDLE"])

        super().__init__(sprite_path, position, KIRBY_COLLIDER)

        # Set up Kirby's attributes
        self.walked_distance = 0
        self.speed = KIRBY_MOVEMENT["SPEED"]
        self.turned_right = True
        self.name = "Kirby"
        self.dead = False

        # Initialize FSM and states
        self.fsm = fsm.FSM(self.set_states(), self.set_transitions())

    def clone(self):
        """
        Creates a deep copy of the current instance.
        Returns:
            A new instance that is a clone of the current object.
        """
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        """
        Custom deepcopy method to handle pygame.Surface objects.
        """
        # Create a new instance of Kirby
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # Copy attributes
        for k, v in self.__dict__.items():
            if k == 'image':
                # Manually copy the pygame.Surface object
                result.__dict__[k] = self.image.copy()
            else:
                result.__dict__[k] = copy.deepcopy(v, memo)
        
        return result
    
    def set_states(self):
        """Sets Kirby's FSM states."""
        self.idle = fsm.Idle()
        self.walk = fsm.Walk()
        return [self.idle, self.walk]
    
    def set_transitions(self):
        """Sets Kirby's FSM transitions."""
        return {
            "walk": fsm.Transition(self.idle, self.walk),
            "idle": fsm.Transition(self.walk, self.idle)
        }
    
    def update(self):
        """Updates Kirby's FSM and handles animations."""
        self.patrol()
        self.animator.play_animation(self.fsm.current.name, self)
    
    def patrol(self):
        """Handles Kirby's patrol behavior."""
        if self.turned_right:
            if self.fsm.current == self.idle:
                self.fsm.update("walk", self)
            self.walked_distance += self.speed
            self.rect.x += self.speed
        else:
            if self.fsm.current == self.idle:
                self.fsm.update("walk", self)
            self.walked_distance += self.speed
            self.rect.x -= self.speed

        if self.walked_distance >= KIRBY_MOVEMENT["PATROL_MAX_DISTANCE"]:
            self.turned_right = not self.turned_right
            self.walked_distance = 0
            self.image = pg.transform.flip(self.image, not self.turned_right, False)
            self.fsm.update("idle", self)