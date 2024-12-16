import pygame as pg
import finite_state_machine as fsm
from game_map import Map
from player import Player
from kirby import Kirby
from observer import Observer
from sound_player import SoundPlayer
from camera import Camera
from consts import SCREEN_DIMENSIONS, FPS, TIME, GAME_EVENTS, FONT_PATH, FONT_SIZE, COLORS, KIRBIES_SPAWN_POSITIONS, MENUS_TEXT_FILE_PATHS
from game_ui import UI
from command import InputHandler
from peach import Peach
import os
import json

class Game:
    """ This class represents the game and manages the game states,and its atributtes.

        Attributes:
            - window: The game window.
            - clock: The game clock.
            - map: The game map.
            - fsm: The game finite state machine.
            - player: The game player.
            - ui: The game user interface.
            - audio_players: The game audio players.
            - camera: The game camera.
            - delta_time: The game delta time.
            - all_sprites: The game sprites.
            - _instance: The game instance.
            - start_menu_text: The game start menu text.
            - end_game_text: The game end game text.
    """
    _instance = None

    def __new__(cls):
        """
        Creates a new instance of the game if it does not exist.
        
        Returns:
            The game instance.
            
        """
        
        if cls._instance is None:
            cls._instance = super(Game, cls).__new__(cls)
            cls._instance.__initialized = False

        return cls._instance
    
    def __init__(self) -> None:
        """
        Initializes a new instance of the game, and setups the window, cllock, fsm, atributtes.
        """
        if not self.__initialized:
            self.window = self.setup_pygame()
            self.clock = None
            self.map = None
            self.fsm = fsm.FSM(self.set_states(), self.set_transitions())
            self.__initialized = True
            self.player = None
            self.ui = None
            self.audio_players = None
            self.camera = None
            self.delta_time = 0
            self.all_sprites = None
            self.menu_text = None
            self.final_score_text = None
            self.player_won = False

    def setup_pygame(self):
        """
        The setup_pygame method initializes the pygame and its windows with the screen dimensions and title.
        """
        pg.init()
        window = pg.display.set_mode((SCREEN_DIMENSIONS["WIDTH"], SCREEN_DIMENSIONS["HEIGHT"]))
        pg.display.set_caption("Super Bowser")
    
        return window
    
    def set_states(self):
        """
        The set_states method is responsible for setting the states of the game e.g. (start_menu, playing, game_over).

        Returns:
          - states (list): The list of the game's states.
        """
        self.start_menu = fsm.StartMenu()
        self.playing = fsm.Playing()
        self.game_over = fsm.GameOver()

        return [self.start_menu, self.playing, self.game_over]
    
    def set_transitions(self):
        """
        Manages the transitions based on the states created before.
        """
        return {
            "start_game": fsm.Transition(self.start_menu, self.playing),
            "game_over": fsm.Transition(self.playing, self.game_over),
            "restart_game": fsm.Transition(self.game_over, self.playing)
        }

    def reset_game(self):
        """
        The reset_game method is responsible for resetting the game by initializing the map and updating the FSM state.
        """
        self.map = Map()
        self.fsm.update("start_game", self)
   
    def play_level(self):    
        """
        The play_level method is responsible for updating the game level by updating the sprites, camera, and UI.

        An observer is used to observe the game , and if a event is triggered, the observer will notify the game.
        """
        self.all_sprites.update()
        self.camera.update(self.player)
        self.delta_time += self.clock.tick(FPS)
        self.observer.observe(self.all_sprites)
     
        if self.delta_time >= TIME["ONE_SECOND"]:
            self.ui.update_timer()
            game_time = self.ui.time
            self.observer.observe_time_envents(game_time)
            self.delta_time -= TIME["ONE_SECOND"]

    def setup_sprites(self):
        """
        The setup_sprites method is responsible for adding the sprites of the player and the enemies (kirbies).

        Returns:
            - all_sprites (pygame.sprite.Group): The group of all game sprites.
        """
        all_sprites = pg.sprite.Group()
    
        player = Player()
        all_sprites.add(player)


        peach = Peach()
        all_sprites.add(peach)
       
        first_kirby = None

        for kirby_position in KIRBIES_SPAWN_POSITIONS:
            if KIRBIES_SPAWN_POSITIONS.index(kirby_position) == 0:
                first_kirby = Kirby(kirby_position)
                all_sprites.add(first_kirby)
            else:
                kirby = first_kirby.clone()
                kirby.rect.topleft = kirby_position
                all_sprites.add(kirby)

        return all_sprites       
     
    def setup_game_level(self):
        """
        The setup_game_level method is responsible for setting up the game level by initializing the map, sprites, player, camera, observer, and audio players.
        """
        self.map = Map()
        self.all_sprites = self.setup_sprites()  
        self.player = next(sprite for sprite in self.all_sprites if isinstance(sprite, Player)) 
        self.camera = Camera(SCREEN_DIMENSIONS["WIDTH"], SCREEN_DIMENSIONS["HEIGHT"])
        self.observer = Observer()
        self.audio_players = get_audio_players()
        self.delta_time = 0
        self.ui = UI()
        self.clock = pg.time.Clock()
 
    def display_start_menu(self):
        """
        The display_start_menu method is responsible for displaying the start menu screen with the game title and instructions.
        """

        self.window.fill(COLORS["BLACK"])
    
        if self.menu_text is None:
            self.load_menu_text_file(MENUS_TEXT_FILE_PATHS["START_MENU"])

        self.write_menu_text()

    def write_menu_text(self):
        """ The write_menu_text method is responsible for writing the menu text on the screen.


        """

        y_offset = SCREEN_DIMENSIONS["HEIGHT"] // 2 - 100
        
        title_font = pg.font.Font(os.path.join(os.path.dirname(__file__), FONT_PATH),FONT_SIZE)
        title_font.bold = True
       
        text_font = pg.font.Font(os.path.join(os.path.dirname(__file__), FONT_PATH), FONT_SIZE - 1)

        for line in self.menu_text:
            if title_font is not None:
                line_text = title_font.render(line.strip(), True, COLORS["WHITE"])
                title_font = None
            else:
                line_text = text_font.render(line.strip(), True, COLORS["WHITE"])

            self.window.blit(line_text, (SCREEN_DIMENSIONS["WIDTH"] // 2 - line_text.get_width() // 2, y_offset))
            y_offset += FONT_SIZE + 5
        
        if self.final_score_text is not None:     
            score_lines = self.final_score_text.split("\n")

            for line in score_lines:
                score_label = text_font.render(line.strip(), True, COLORS["WHITE"])
                self.window.blit(score_label, (SCREEN_DIMENSIONS["WIDTH"] // 2 - score_label.get_width() // 2, y_offset))
                y_offset += FONT_SIZE + 5

    def load_menu_text_file(self,file_path):
        """
        The load_menu_text_file method is responsible for loading  a menu text file.

        Args:
            - file_path (str): The path to the menu text file.
        """
        
        full_path = os.path.join(os.path.dirname(__file__), file_path)

        try:
            with open(full_path, "r") as file:    
                self.menu_text = file.readlines()
                
        except FileNotFoundError:
            print("Menu text file not found")

    def display_end_game(self):
        """
        Displays the end game screen with the game over message and score.
        """

        self.window.fill(COLORS["BLACK"])
    
        if self.final_score_text is None and self.player_won:
            self.load_score_text()

        self.clear_level()

        if self.menu_text is None:
            text_path = MENUS_TEXT_FILE_PATHS["END_GAME_MENU"] if self.player_won else MENUS_TEXT_FILE_PATHS["GAME_OVER_MENU"]
            self.load_menu_text_file(text_path)

        self.write_menu_text()
    
    def load_score_text(self):
        """
        The load_score_text method is responsible for loading the score text.
        If the player has a new high score, it will return a new high score message, otherwise it will return the player's score and its high score.

        Returns:
            - score_text (pygame.Surface): The score text.
        """

        final_score = self.ui.score + self.ui.time
        
        high_score_file_path = os.path.join(os.path.dirname(__file__), MENUS_TEXT_FILE_PATHS["HIGH_SCORE"])
        
        new_high_score = False
        previous_high_score = None

        try:
            with open (high_score_file_path, "r+") as file:
                json_file = json.load(file)
                previous_high_score = json_file.get("high_score")

                if final_score > previous_high_score:
                    new_high_score = True
                    json_file["high_score"] = final_score
                    file.seek(0)
                    json.dump(json_file, file)
                    file.truncate()

        except FileNotFoundError:
            print("High score file not found")

        self.final_score_text =  f"New High Score: {final_score}." if new_high_score else f"Score: {final_score}\nYour High Score : {previous_high_score}."

        self.final_score_text += "\n\nPress Enter to Play Again or Escape to exit the game."
       
    def clear_level(self):
        """
        Clears the current game level by resetting the map, sprites, player, camera, observer, and audio players.
        """
        self.map = None
        self.all_sprites.empty()
        self.player = None
        self.camera = None
        self.observer = None
        self.delta_time = None
        self.game_over_text = None
        self.clock = None
  
      

def update_display(game):
    """
    Updates the game display based on the current FSM state.
    """
    if game.fsm.current == game.playing:
        game.window.fill(COLORS["BACKGROUND"])
        game.map.draw(game.window, game.camera)

        for sprite in game.all_sprites:
            game.window.blit(sprite.image, game.camera.apply(sprite))
        game.ui.draw_labels(game.window)

    pg.display.flip()

def event_handler(running, game):
    """
    Handles game events such as key presses and custom game events.
    """
    input_handler = InputHandler()
    for event in pg.event.get(): 
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:
            input_handler.handle_input(event.key, game.player)
            
            if event.key == pg.K_RETURN and game.fsm.current == game.game_over:
                game.ui.reset_labels_values()
                game.final_score_text = None
                game.setup_game_level()
                game.fsm.update("restart_game", game)

            elif event.key == pg.K_RETURN and game.fsm.current == game.start_menu:
                game.setup_game_level()
                game.fsm.update("start_game", game)

            elif event.key == pg.K_ESCAPE:
                running = False

        elif event.type == GAME_EVENTS["QUIT_GAME_EVENT"]:
            print("Quit game event triggered")
            running = False

        elif event.type == GAME_EVENTS["PLAYER_DEATH_EVENT"]: 
            game.audio_players[1].play("bowser_death")
            player = next(sprite for sprite in game.all_sprites if isinstance(sprite, Player))
            player.respawn()
            game.ui.update_score(-50)

        elif event.type == GAME_EVENTS["TIMEOUT_EVENT"]:
            game.clear_level()
            game.fsm.update("game_over", game)
            game.menu_text = None

            game.audio_players[0].stop()
            game.audio_players[1].play("game_over")

        elif event.type == GAME_EVENTS["TIME_ALERT_EVENT"]:
            game.ui.change_timer_text_color()

            game.audio_players[1].play("time_warning")

        elif event.type == GAME_EVENTS["PLAYER_JUMP_EVENT"]:
            game.audio_players[1].play("jump")

        elif event.type == GAME_EVENTS["END_GAME_EVENT"]:
            game.fsm.update("game_over", game)
            game.player_won = True
            game.menu_text = None

            game.audio_players[0].stop()

            game.audio_players[1].play("end_game")
    
        elif event.type == GAME_EVENTS["ENEMY_KILLED_EVENT"]:
            game.audio_players[1].play("enemy_killed")

            for sprite in game.all_sprites:
                if isinstance(sprite, Kirby) and sprite.dead: 
                    game.all_sprites.remove(sprite)

            game.ui.update_score(100)

    return running

def get_audio_players():
    """
    Initializes and returns the audio players for music and sound effects.
    """
    music_player = SoundPlayer(["overworld_theme"], True)
    music_player.play("overworld_theme")
    sound_effecter = SoundPlayer(["jump","bowser_death","time_warning", "enemy_killed", "end_game","game_over"], False)
    return [music_player, sound_effecter]

def game_loop(game):
    """
    Main game loop that handles the game states and updates the display.
    """
    running = True

    while running:
        if game.fsm.current == game.start_menu:
              game.display_start_menu()

        elif game.fsm.current == game.playing:
            game.play_level()

        elif game.fsm.current == game.game_over:
            game.display_end_game()

        running = event_handler(running, game)
        update_display(game)
        
    pg.quit()

def main():
    """
    Entry point for the game. Initializes the game and starts the game loop.
    """
    game = Game()
    game_loop(game)

if __name__ == "__main__":
    main()