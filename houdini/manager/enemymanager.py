import asyncio
from dataclasses import dataclass

import numpy as np

from houdini.constants import EnemySly, EnemyScrap, EnemyTank, UnoccupiedEnemySpawnTile
from houdini.constants import FireNinja, WaterNinja, SnowNinja
from houdini.constants import MapConstants, EnemyObject, HPObject


class EnemyManager:

    def __init__(self, room):
        self.room = room

        self.current_enemies = []
        self.default_enemies = [EnemySly, EnemyScrap, EnemyTank]

    def generate_enemies(self):
        self.room.object_manager.generate_enemies()

        for enemy in self.room.object_manager.enemies:
            self.current_enemies.append(Enemy(id=enemy.id, hitpoints=enemy.occupant.Hitpoints.value, \
                                                curr_object=enemy, parent=enemy.occupant))
    
    async def do_enemy_turn(self):
        for enemy in self.current_enemies:
            players = self.get_nearby_players(enemy.curr_object.x, enemy.curr_object.y)
            if len(players) == 0: # No surronding users, let's move
                distances = [np.linalg.norm( \
                            np.array([player.snow_ninja.current_object.x, player.snow_ninja.current_object.y]) \
                            - np.array([enemy.curr_object.x, enemy.curr_object.y])) for player in self.room.penguins]
                player = self.room.penguins[distances.index(min(distances))] # Determine which player to follow
                nonoverlap_coordinate = self.room.object_manager.find_open_coordinate(player.snow_ninja.current_object.x, \
                                        player.snow_ninja.current_object.x + 1, player.snow_ninja.current_object.y, \
                                        player.snow_ninja.current_object.y + 1)

                new_x, new_y = self.do_astar_algorithm((enemy.curr_object.x, enemy.curr_object.y), \
                                                (nonoverlap_coordinate[0], nonoverlap_coordinate[1]), \
                                                tile_range = enemy.parent.Range.value)[1]
                
                await self.move_enemy(enemy, new_x, new_y)

                await asyncio.sleep(3)
            else: # Attack nearby user
                print('Incomplete implementation')

    async def move_enemy(self, enemy, x, y):
        enemy_hp_bar = self.room.object_manager.enemy_hpbars[self.room.object_manager.enemies.index(enemy.curr_object)]

        old_x, old_y = enemy.curr_object.x, enemy.curr_object.y
        enemy.curr_object.x = x
        enemy.curr_object.y = y

        enemy_hp_bar.x = x
        enemy_hp_bar.y = y

        adjusted_x = round(x + EnemyObject.XCoordinateOffset.value, EnemyObject.XCoordinateDecimals.value)
        adjusted_y = round(y + EnemyObject.YCoordinateOffset.value, EnemyObject.YCoordinateDecimals.value)

        await self.room.send_tag('O_SLIDE', enemy.curr_object.id, adjusted_x, adjusted_y, \
                                    128, enemy.parent.MoveAnimationDuration.value)

        await self.room.animation_manager.play_animation(enemy.curr_object, \
                                    enemy.parent.MoveAnimation.value, 'play_once', \
                                    enemy.parent.MoveAnimationDuration.value)
        await self.room.animation_manager.play_animation(enemy.curr_object, \
                                    enemy.parent.IdleAnimation.value, 'loop', \
                                    enemy.parent.IdleAnimationDuration.value)

        await self.room.sound_manager.play_sound(enemy.parent.MoveAnimationSound.value)

        adjusted_x = round(x + HPObject.XCoordinateOffset.value, HPObject.XCoordinateDecimals.value)
        adjusted_y = round(y + HPObject.YCoordinateOffset.value, HPObject.YCoordinateDecimals.value)
        await self.room.send_tag('O_SLIDE', enemy_hp_bar.id, adjusted_x, adjusted_y, \
                                    128, enemy.parent.MoveAnimationDuration.value)
        
        self.room.object_manager.map[x][y].occupant = enemy.parent
        self.room.object_manager.map[old_x][old_y].occupant = None
        await self.room.send_tag('P_TILECHANGE', old_x, old_y, UnoccupiedEnemySpawnTile.TileUrl.value)

    def get_nearby_players(self, x, y, tile_range=1):
        occupants = []
        for x_i in range(x - tile_range, x + tile_range + 1):
            if x_i < 0 or x_i >= MapConstants.BoardWidth.value:
                continue

            for y_i in range(y - tile_range, y + tile_range + 1):
                if y_i < 0 or y_i >= MapConstants.BoardHeight.value or (x_i == x and y_i == y):
                    continue
                
                if self.room.object_manager.map[x_i][y_i].occupant in [FireNinja, WaterNinja, SnowNinja]:
                    occupants.append(self.room.object_manager.map[x_i][y_i].occupant)
        
        return occupants
    
    def do_astar_algorithm(self, start, end, tile_range=1):
        start_node = Node(parent=None, position=start, g=0, h=0, f=0)
        end_node = Node(parent=None, position=end, g=0, h=0, f=0)

        open_list, closed_list = [], []
        open_list.append(start_node)

        outer_iterations, max_iterations = 0, (len(self.room.object_manager.map) // 2) ** 2

        while len(open_list) > 0:
            outer_iterations += 1

            curr_node, curr_i = open_list[0], 0
            for i, node in enumerate(open_list):
                if node.f < curr_node.f:
                    curr_node = node
                    curr_i = i
            if outer_iterations > max_iterations:
                path = []
                head = curr_node

                while head is not None:
                    path.append(head.position)
                    head = head.parent
                
                return path[::-1]

            open_list.pop(curr_i)
            closed_list.append(curr_node)

            if curr_node.position == end_node.position:
                path = []
                head = curr_node

                while head is not None:
                    path.append(head.position)
                    head = head.parent
                
                return path[::-1]
            
            children = []
            for position in self.get_neighbor_list(tile_range):
                new_pos = curr_node.position[0] + position[0], curr_node.position[1] + position[1]
                if new_pos[0] > (len(self.room.object_manager.map) - 1) or new_pos[0] < 0 or new_pos[1] > (len(self.room.object_manager.map[len(self.room.object_manager.map)-1]) -1) or new_pos[1] < 0:
                    continue

                if self.room.object_manager.map[new_pos[0]][new_pos[1]].occupant is not None:
                    continue
                
                children.append(Node(parent=curr_node, position=new_pos, f=0, g=0, h=0))
        
            for child in children:
                if len([closed_child for closed_child in closed_list if closed_child.position == child.position]) > 0:
                    continue
        
                child.g = curr_node.g + 1
                child.h = np.linalg.norm(np.array(child.position) - np.array(end_node.position))
                child.f = child.g + child.h

                if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                    continue
                
                open_list.append(child)

    def get_neighbor_list(self, tile_range):
        neighbors = []
        i, delta = -1, 1
        for x in range(-tile_range, tile_range + 1):
            i += delta
            if i == tile_range:
                delta = -1

            for y in range(-i, i + 1):
                neighbors.append((x, y))

        return neighbors

@dataclass
class Enemy():
    id: int 
    hitpoints: int

    curr_object: 'typing.Any'
    parent: 'typing.Any'

@dataclass
class Node():
    parent: 'typing.Any'
    position: 'typing.Any'

    g: int
    h: int
    f: int