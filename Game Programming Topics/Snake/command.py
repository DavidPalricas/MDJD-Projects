from consts import RIGHT,LEFT,UP,DOWN
class Command:
    def execute():
        raise NotImplemented
       

class Up(Command):
    @classmethod
    def execute(self,player):
        player.change_direction(UP)

class Down(Command):
    @classmethod
    def execute(self,player):
        player.change_direction(DOWN)

class Left(Command):
    @classmethod
    def execute(self,player):
        player.change_direction(LEFT)

class Right(Command):
    @classmethod
    def execute(self,player):
        player.change_direction(RIGHT)
