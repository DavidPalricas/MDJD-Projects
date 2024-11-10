import pygame as pg
import random
import finite_state_machine as fsm

class Ant():
    """ The Ant class is responsible for managing the ant in the game.

        Attributes:
        - ant: The ant sprite.
        - fsm: The finite state machine of the ant.
        - reproduce: A flag indicating whether the ant can reproduce or not.
    """
    def __init__(self)-> None:
        """ Initializes a new instance of the Ant class.
            In the constructor, the ant sprite is created, the finite state machine is initialized, and the reproduce flag is set to False.
        """

        self.ant = pg.Rect(0, 0, 10, 10)

        self.fsm = fsm.FSM(self.set_states(),self.set_transitions())

        self.reproduce = False


    def set_states(self):
       """ 
            The set_states method initializes the states of the ant.~

            The ant has four states: forage, go_home, dead, and thirsty.
            The forage state is the initial state of the ant and is responsible for finding food in the game map.
            The go_home state is responsible for the ant returning home after finding food.
            The thirsty state is responsible for the ant finding water after returning home.
            The dead state is responsible for transitioning the ant to the dead state.
         
              Returns:
              - list: The list of states of the ant.
       """
       
       self.forage = fsm.Forage()
       self.go_home = fsm.GoHome()
       self.thirsty = fsm.Thirsty()
       self.dead   = fsm.Dead()

       return [self.forage, self.go_home, self.thirsty, self.dead]

    def set_transitions(self):
        """
            The set_transitions method initializes the transitions between the states of the ant.
            
            Returns:
            - dict: The dictionary of transitions between the states of the ant.
            
        """
        return { "found_food": fsm.Transition(self.forage, self.go_home),
                  "found_home" : fsm.Transition(self.go_home,self.thirsty),
                  "found_water" : fsm.Transition(self.thirsty,self.forage),
                  "found_poison" : fsm.Transition(any, self.dead)
        }
  
    def draw(self, window):
        """ The draw method is responsible for drawing the ant on the game window.
            It draws the ant as a rectangle with a size of 10x10 pixels.
            
            Args:
            - window: The game window.
        """
        pg.draw.rect(window, (30, 30, 30), self.ant)


    def move(self,game_map):
        """ The move method is responsible for moving the ant randomly in the game map.
            It checks if the ant next move does not go out of the game map horizontally or vertically, by calling the cannot_move_horizontal and cannot_move_vertical methods.
            It also checks the current state of the ant by calling the check_ant_state method.
            And if the ant has found poison, it transitions to the dead state.
        """

        move_horizontal = 5 if random.randint(0,1) == 1 else -5
        move_vertical = 5 if random.randint(0,1) == 1 else -5
        
        if  self.cannot_move_horizontally(self.ant.x + move_horizontal, game_map):
            move_horizontal = 0
        
        if self.cannot_move_vertically(self.ant.y + move_vertical, game_map):
            move_vertical = 0

        self.ant.x += move_horizontal
        self.ant.y += move_vertical


        self.check_ant_state(game_map)

        if (self.found_element(game_map,"poison")):
            self.fsm.update("found_poison",self)
   
    def cannot_move_horizontally(self,x,game_map):

        """ The cannot_move_horizontal method checks if the ant next move does not go out of the game map horizontally.
            
            Args:
                - x: The x-coordinate of the ant.
                - game_map: The game map.
            
            Returns:
                - bool: A flag indicating whether the ant cannot move horizontally.
        """
        return x <= 0 or x >= game_map.map_width 
  
    
    def cannot_move_vertically(self,y,game_map):
        """ The cannot_move_vertical method checks if the ant next move does not go out of the game map vertically.
            
            Args:
                - y: The y-coordinate of the ant.
                - game_map: The game map.
            
            Returns:
                - bool: A flag indicating whether the ant cannot move vertically.
        """

        return y <= 0 or y >= game_map.map_height
    
    def check_ant_state(self,game_map):
        """ The check_ant_state method checks the current state of the ant and updates it based on the rules of the game.
            If the ant is in the forage state and finds sugar, the ant transitions to the go_home state.
            If the ant is in the go_home state and finds the home, the ant transitions to the thirsty state and its reproduction flag is set to True.
            If the ant is in the thirsty state and finds water, the ant transitions to the forage state.

            Args:
            - game_map: The game map.
        """

        match self.fsm.current:
            case self.forage:
                if  self.found_element(game_map,"sugar"):
                    self.fsm.update("found_food",self)

            case self.go_home:
                if self.found_element(game_map,"home"):
                    self.fsm.update("found_home",self)
                    self.reproduce = True

            case self.thirsty:
                if  self.found_element(game_map,"water"):
                    self.fsm.update("found_water",self)

    
    
    def found_element(self,game_map,element_name):
        """ The found_element method checks if the ant has found an element in the game map.
            If the ant has found the element, the method removes the element from the game map, except for its home.
        
            Args:
            - game_map: The game map.
            - element_name: The name of the element that the ant is looking for.

            Returns:
            - bool: A flag indicating whether the ant has found the element.
        """

        sugar = [element for element in game_map.environment_elements if element[1] == element_name]

        for element in sugar:
            if self.ant.colliderect(element[0]):

                if element_name != "home":
                    game_map.environment_elements.remove(element)

                return True
            
        return False
    