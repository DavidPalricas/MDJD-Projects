import pygame as pg
from consts import TIME, GAME_EVENTS, SCREEN_DIMENSIONS,PLAYER_MOVEMENT
from player import Player
from kirby import Kirby
from peach import Peach
from game_map import Map

class Observer:
 """The Score class acts as game observer, because to update the score it needs to listen to the game events.
    This class is also responsible for drawing the score and timer labels on the screen.

      Attributes:
         - player (Player): The player object.
         - game_map (GameMap): The game map object.
         - enemies (list): The list of enemy sprites.
 """

 def __init__(self) -> None:
    """ Initializes a new instance of the Observer class and sets up the attributes of the class.
    """
    self.player = None  
    self.game_map = Map()
    self.enemies = None

 def observe(self, all_sprites):	
   """ The check_collision function checks if the player has collided with any of the blocks in the game map.

      For now this method only checks if the player has collided with the brick blocks and question blocks in the game map, when the player is below the block.
      If the player has collided with a brick block, it breaks the block and adds 50 points to the player's score.
      If the player has collided with a question block, it replaces the block with a used question block.


      Args:
         - all_sprites (Group): The group of all the sprites in the game.
   """

   if self.player is None:
      self.player = next(sprite for sprite in all_sprites if isinstance(sprite, Player))

   enemies = [sprite for sprite in all_sprites if isinstance(sprite, Kirby)]

   peach = next(sprite for sprite in all_sprites if isinstance(sprite, Peach))

   self.observe_player_jumped()

   self.observe_player_in_void()

   self.check_endgame(peach)

   self.observe_floor_collisions()

   if len(enemies) > 0:
      self.observe_enemy_collision(enemies)

 def observe_player_jumped(self):
   """ The observe_player_jumped method checks if the player has jumped in the game, if it has, it posts an event of player jump.""" 
   # Check if the player has jumped
   if self.player.velocity_y == -PLAYER_MOVEMENT["JUMP_SPEED"] :
      pg.event.post(pg.event.Event(GAME_EVENTS["PLAYER_JUMP_EVENT"]))
    
 def observe_player_in_void(self):
   """ The observe_player_in_void method checks if the player has fallen into the void in the game map, if it has, it posts an event of player death.""" 

   if self.player.rect.y > SCREEN_DIMENSIONS["HEIGHT"]:
      pg.event.post(pg.event.Event(GAME_EVENTS["PLAYER_DEATH_EVENT"]))


 def observe_time_envents(self, game_time):  
   """ The observe_time method checks if the game time is equal to the alert time or the timeout time, and posts the corresponding event.
   
      Args:
         - game_time (int): The current game time.
         
   """   

   if game_time == TIME["ALERT_TIME"]:
      pg.event.post(pg.event.Event(GAME_EVENTS["TIME_ALERT_EVENT"]))
     
   if game_time <= TIME["TIMEOUT"]:
      pg.event.post(pg.event.Event(GAME_EVENTS["TIMEOUT_EVENT"]))
  

 def check_endgame(self, peach):
    """ The check_endgame method checks if the player has collided with the peach sprite in the game map, if it has, it posts an event to end the game."""

    if self.player.rect.colliderect(peach.rect): 
      pg.event.post(pg.event.Event(GAME_EVENTS["END_GAME_EVENT"]))
   

 def observe_floor_collisions(self):
    """ The observe_floor_collisions method checks if the player has collided with any of the floor blocks in the game map.
         If the player has collided with a floor block, it sets the player's velocity_y to 0 and sets the player's is_on_ground attribute to True.
         Otherwise, it sets the player's is_on_ground attribute to False (the player is in the air).
    """

    floor_block_index = self.player.rect.collidelist(self.game_map.floor_blocks_colliders)

    if floor_block_index != -1:
      block = self.game_map.floor_blocks_colliders[floor_block_index]
      
      # Check if the player is above the block
      if self.player.velocity_y > 0  and self.player.rect.bottom > block.top and self.player.rect.top < block.top:
         self.player.rect.bottom = block.top 

         self.player.on_block = None
   
         self.player.velocity_y = 0
      
         self.player.is_on_ground = True
    else:
         self.player.is_on_ground = False
  
 def observe_enemy_collision(self, enemies):
      """ The observe_enemy_collision method checks if the player has collided with any of the enemies in the game.
            If the player has collided with an enemy, it checks if the player is above the enemy.
            If the player is above the enemy, it posts an event to kill the enemy otherwise the player dies and posts and event of player death.

         Args:
            - enemies (list): The list of enemy sprites.
      """

      enemies_colliders = [enemy.rect for enemy in enemies]
      enemy_collider_index = self.player.rect.collidelist(enemies_colliders)

      if enemy_collider_index != -1:
         enemy = enemies[enemy_collider_index]

         kirby_collider = enemies_colliders[enemy_collider_index]

         if self.player.rect.bottom >= kirby_collider.top and  not self.player.is_on_ground:
            pg.event.post(pg.event.Event(GAME_EVENTS["ENEMY_KILLED_EVENT"]))
            enemy.dead = True
         else:
            pg.event.post(pg.event.Event(GAME_EVENTS["PLAYER_DEATH_EVENT"]))
    
