import random as rand
import math as m

# The Entity class is the parent class of the Snake class
class Entity:
    # The constructor of the class initializes
    def __init__(self,vital_space,spawn_treshold):
        self.vital_space = vital_space
        self.spawn_threshold = spawn_treshold
        self.other_entities =  []

    # The spawn metohd spawns the entities
    def spawn(self):
        entity_pos = rand.randrange(self.vital_space[0]), rand.randrange(self.vital_space[1])

        if not self.check_other_spawns(entity_pos):
            self.spawn()
            return
        
        return entity_pos
          
    # The check_other_spawns method checks for other entities spawns
    def check_other_spawns(self,entity_pos):
        x,y = entity_pos

        for other_entity in self.other_entities:
            if (x,y) in other_entity:
                return False
            
            if m.dist(entity_pos,other_entity) < self.spaw_threshold:
                return False
            
        return True

    # The draw method draws the entities in the pygame window
    def draw(self):
        pass