class State:
    """The State class is responsible for managing the states of the entity
    
       The class has the following attributes:
            - name: The name of the state
    """

    def __init__(self, name) -> None:
        """
            Initializes a new instance of the State class
        """
        self.name = name

    def enter(self):
        """The enter method is responsible for entering the state"""
        print(f"Entering {self.name}")

    def update(self, object):
        """The update method is responsible for updating the state of the entity

            Args:
                - object (Entity): The entity that the state belongs to
        """
        pass

    def exit(self):
     """The exit method is responsible for exiting the state"""
     pass

class Transition:
    """The Transition class is responsible for managing the transitions between the entity's states
    
       The class has the following attributes:
            - _from: The state from which the transition occurs
            - _to: The state to which the transition occurs
    """

    def __init__(self, _from, _to) -> None:
        """
           Initializes a new instance of the Transition class
        """
        self._from = _from
        self._to = _to

class Forage(State):
    """The Idle class is responsible for managing the idle state of the entity
    """

    def __init__(self) -> None:
        """
            Initializes a new instance of the Idle class, and calls the constructor of the State class (the parent class)
        """

        super().__init__(self.__class__.__name__)

    def update(self, object):
        """The update method is responsible for updating the idle state of the entity

            Args:
                - object (Entity): The entity that the state belongs to

            Returns:
                - bool: A flag indicating to update the entity state
        """

        print("Finding food")
        return super().update(object)

class GoHome(State):
    """The Walk class is responsible for managing the walk state of the entity
    """

    def __init__(self) -> None:
        """ 
            Initializes a new instance of the Walk class, and calls the constructor of the State class (the parent class)
        """

        super().__init__(self.__class__.__name__)

    def update(self, object):
        """The update method is responsible for updating the walk state of the entity

            Args:
                - object (Entity): The entity that the state belongs to

            Returns:
                - bool: A flag indicating to update the entity state
        """

        print("Food found, going home")
        return super().update(object)
    
class Dead(State):
    """The Jump class is responsible for managing the jump state of the entity
    """

    def __init__(self) -> None:
        """ 
            Initializes a new instance of the Jump class, and calls the constructor of the State class (the parent class)
        """

        super().__init__(self.__class__.__name__)

    def update(self, object):
        """The update method is responsible for updating the jump state of the entity

            Args:
                - object (Entity): The entity that the state belongs to

            Returns:
                - bool: A flag indicating to update the entity state
        """

        print("RIP")
        return super().update(object)
    
class Thirsty(State):
    """The Jump class is responsible for managing the jump state of the entity
    """

    def __init__(self) -> None:
        """ 
            Initializes a new instance of the Jump class, and calls the constructor of the State class (the parent class)
        """

        super().__init__(self.__class__.__name__)

    def update(self, object):
        """The update method is responsible for updating the jump state of the entity

            Args:
                - object (Entity): The entity that the state belongs to

            Returns:
                - bool: A flag indicating to update the entity state
        """

        print("Home found, finding water")
        return super().update(object)

class FSM:
    """The FSM class is responsible for managing the finite state machine of the entity

       The class has the following attributes:
            - states: The states of the entity (e.g. idle, walk, jump)
            - transitions: The transitions between the entity's states
            - current: The current state of the entity
            - end: The end state of the entity
    """
    def __init__(self, states: list[State], transitions: dict[Transition]) -> None:
        """
            Initializes a new instance of the FSM class
            
            Args:
                - states (list): A list of the states of the entity
                - transitions (dict): A dictionary of the transitions between the entity's states
        """

        self._states = states
        self._transitions = transitions
        self.current: State = self._states[0]
        self.end: State = self._states[-1]

    def update(self, event, object):
        """
            The update method is responsible for updating the state of the entity based on the event

            Args:
                - event (str): The event that triggers the state transition
                - object (Entity): The entity that the state belongs to

            Returns:
                - bool: A flag indicating whether the entity has reached the end state
        """

        if event:

            if event == "found_poison":
                trans = self._transitions.get(event)
                self.current.exit()
                self.current = trans._to
                self.current.enter()

            else:
                trans = self._transitions.get(event)
                if trans and trans._from == self.current:
                    self.current.exit()
                    self.current = trans._to
                    self.current.enter()
        self.current.update(object)

        if self.current == self.end:
            self.current.exit()
            return False
        return True
    