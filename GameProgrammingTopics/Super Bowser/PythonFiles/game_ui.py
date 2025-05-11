from consts import TIME, FONT_PATH, FONT_SIZE, COLORS
import pygame as pg
import os

class UI:
    """ The UI class is responsible for managing the user interface of the game.
        This is implemented as a singleton to ensure only one instance exists, during the game.

        Attributes:
            - _instance (UI): The instance of the UI class
            - score (int): The score of the player
            - time (int): The time remaining in the game
            - font (Font): The font used for the text
            - score_text_color (tuple): The color of the score text
            - timer_text_color (tuple): The color of the timer text
    """

    _instance = None

    def __new__(cls, *args, **kwargs):  
        """ The __new__ method is responsible for creating a new instance of the UI class if it does not exist.
            In this method we ensure that only one instance of the UI class exists during the game, to adopt the singleton design pattern.
            This method is called before the __init__ method (constructor of the class)

            Args:
                - cls (UI): The class of the instance
                - *args: The arguments
                - **kwargs: The keyword arguments

            Returns:
                - UI: The instance of the UI class
        """

        if cls._instance is None:
            cls._instance = super(UI, cls).__new__(cls, *args, **kwargs)

        return cls._instance
    
    def __init__(self) -> None:
        """ Initializes a new instance of the UI class and sets up the user interface attributes
            If the instance of the UI class exists, this method does not create a new instance (singleton design pattern)  
        """

        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self.score = 0
        self.time = TIME["GAME_TIME"]
        self.font  = pg.font.Font(os.path.join(os.path.dirname(__file__), FONT_PATH ), FONT_SIZE)
        self.score_text_color =  COLORS["WHITE"]
        self.timer_text_color =  COLORS["WHITE"]


    def change_timer_text_color(self):
        """ The change_timer_text_color function is responsible for changing the color of the timer text to red when the time is running out.
            It raises a ValueError if the timer text color is already red.
        """
        if self.timer_text_color == COLORS["RED"]:
            raise ValueError("The timer text color is already red")
        
        if self.timer_text_color == COLORS["WHITE"]:
            self.timer_text_color = COLORS["RED"]


    def update_score(self,points):
        """ The update_score function is responsible for updating the score of the player.
             If the score is less than 0, it sets the score to 0.

            Args:
                - points (int): The points to be added to the player's score.
        """

        self.score  = self.score + points if self.score + points > 0 else 0

    def reset_labels_values(self):
        self.time = TIME["GAME_TIME"]
        self.timer_text_color = COLORS["WHITE"]
        self.score = 0


    def update_timer(self):
        """ The update_timer function is responsible for updating the time remaining in the game.
            It decrements the time by the delta time.

            Args:
                - delta_time (int): The time elapsed since the last frame.
        """

        self.time = self.time - 1 if self.time - 1 > 0 else 0

    def draw_timer_label(self,window):
        """ The draw_timer_label function is responsible for drawing the timer label on the screen after 1 second has passed.
            It also changes the color of the timer label when the time is running out, and plays a warning sound effect and the version of the music speed up.
            It stops the music player and decremeting the time when the time is up.

            Args:
                - window (Surface): The game window object.
                - delta_time (int): The time elapsed since the last frame.
        """

        time_label = self.font.render(f"TIME", True, self.timer_text_color)
        timer_label = self.font.render(f"{self.time:03}", True, self.timer_text_color)
            
        window.blit(time_label, (700, 10))
        window.blit(timer_label, (705, 25))


    def draw_score_label(self,window):
        """ The draw_score_label function is responsible for drawing the score label on the screen.

            Args:
                - window (Surface): The game window object.
        """

        player_text = self.font.render("Bowser", True, self.score_text_color)
        score_label = self.font.render(f"{self.score:07}", True, self.score_text_color)

        window.blit(player_text, (10, 10))
        window.blit(score_label, (10, 25))

    def draw_labels(self,window):
        """ The draw_ui_labels function is responsible for calling the methods to draw the score and timer labels on the screen.

            Args:
                - window (Surface): The game window object.
                - delta_time (int): The time elapsed since the last frame.
        """
        self.draw_score_label(window)
        self.draw_timer_label(window)

