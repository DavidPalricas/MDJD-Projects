import pygame as pg

"""
    Class that defines the commands that can be executed by the player.
    Each command has an execute method that takes the player as an argument.
"""
class Command:
    def execute(self, player):
        pass

class MoveRightCommand(Command):
    """ The MoveRightCommand class is responsible for moving the player to the right."""
    def execute(self, player):
        player.move_right()

class MoveLeftCommand(Command):
    """ The MoveLeftCommand class is responsible for moving the player to the left."""
    def execute(self, player):
        player.move_left()

class JumpCommand(Command):
    """ The JumpCommand class is responsible for making the player jump."""
    def execute(self, player):
        player.initiate_jump()

class QuitGameCommand(Command):
    """ The QuitGameCommand class is responsible for quitting the game."""
    def execute(self, player):
        player.quit_game()

class InputHandler:
    """ The InputHandler class is responsible for handling the player input and executing the corresponding commands."""
    def __init__(self):
        self.commands = {
            pg.K_UP: JumpCommand(),
            pg.K_LEFT: MoveLeftCommand(),
            pg.K_RIGHT: MoveRightCommand(),
            pg.K_w: JumpCommand(),
            pg.K_a: MoveLeftCommand(),
            pg.K_d: MoveRightCommand(),
            pg.K_SPACE: JumpCommand(),
            pg.K_ESCAPE: QuitGameCommand()
        }

    def set_command(self, key, command):
        self.commands[key] = command

    def handle_input(self, key, player):
        command = self.commands.get(key, None)
        if command and player is not None:
            command.execute(player)