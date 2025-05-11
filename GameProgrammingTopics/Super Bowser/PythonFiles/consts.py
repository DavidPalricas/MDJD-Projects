import pygame as pg

# Game Event Constants
GAME_EVENTS = {"QUIT_GAME_EVENT": pg.USEREVENT + 1, 
               "PLAYER_DEATH_EVENT": pg.USEREVENT + 2, 
               "TIMEOUT_EVENT": pg.USEREVENT + 3, 
               "TIME_ALERT_EVENT": pg.USEREVENT + 4, 
               "PLAYER_JUMP_EVENT": pg.USEREVENT + 5, 
               "END_GAME_EVENT": pg.USEREVENT + 6, 
               "ENEMY_KILLED_EVENT": pg.USEREVENT + 7 
               }

# Screen Dimensions Constants
SCREEN_DIMENSIONS = {"WIDTH": 800, 
                     "HEIGHT": 277}

# Map Constants flor block constants and peach sprite path
FLOOR_TILE_DIMENSIONS = {"WIDTH": 16, "HEIGHT": 19}
FLOOR_BLOCK = 0
FLOOR_BLOCK_SPRITE_PATH = "../Assets/SpriteSheets/Map/floor_block.png"

# Peach Constants
PEACH_COLLIDER = (16, 16)
PEACH_SPAWN_POSITION = (1445, 240)
PEACH_SPRITE_PATH = "../Assets/SpriteSheets/Peach/peach.png"

# Time Constants
TIME = {"GAME_TIME": 20, 
        "ALERT_TIME": 10,
          "TIMEOUT": 0, 
          "ONE_SECOND": 1000
        }

# Game Constants
FPS = 60
GRAVITY = 0.8

# Player Constants
PLAYER_MOVEMENT = {"SPEED": 1.8, 
                  "JUMP_SPEED": 10, 
                  "FRICTION": 0.8, 
                  } 
PLAYER_PATHS = {"IDLE": "../Assets/SpriteSheets/Bowser/idle/bowser_idle.png",
                "ANIMATOR_BASE": "../Assets/SpriteSheets/Bowser/",
               }
PLAYER_COLLIDER = (25, 31)
PLAYER_SPAWN_POSITION = (0, 235)

# Kirby Constants
KIRBY_PATHS = {"IDLE": "../Assets/SpriteSheets/Kirby/idle/kirby_idle.png",
                "ANIMATOR_BASE": "../Assets/SpriteSheets/Kirby/",
               }
KIRBY_MOVEMENT = {"SPEED": 1.2,
                  "PATROL_MAX_DISTANCE": 100
                }
KIRBY_COLLIDER = (18, 20)
KIRBIES_SPAWN_POSITIONS = [(150, 252), (350, 252), (570, 195),(770, 138), (1000, 195)]


# UI Constants
FONT_PATH = "../Assets/Font/mario_nes.ttf"
FONT_SIZE = 12
COLORS = {"WHITE": (255, 255, 255), 
          "RED": (255, 0, 0), 
          "BLACK": (0, 0, 0), 
          "BACKGROUND": (107, 136, 255)
          }

# Menus Constants
MENUS_TEXT_FILE_PATHS = {"START_MENU": "../Assets/MenusText/start_menu.txt",
                         "GAME_OVER_MENU": "../Assets/MenusText/game_over_menu.txt",
                          "END_GAME_MENU": "../Assets/MenusText/end_game_menu.txt",
                          "HIGH_SCORE" : "../Assets/MenusText/high_score.json"
                        }