from houdini.constants import MapConstants, MovementTile, EnemyObject, \
                                    PenguinObject, HPObject, ObstacleObject, EnemyTarget, SelectedEnemyTarget
from houdini.constants import FireNinja, WaterNinja, SnowNinja
from houdini.constants import EnemySly, EnemyTank, EnemyScrap
from houdini.constants import OccupiedPenguinSpawnTile

from dataclasses import dataclass

import asyncio
import random

class ObjectManager:

    def __init__(self, room):
        self.room = room

        self.map = []
        self.enemies = []
        self.players = []
        self.obstacles = []

        self.player_hpbars = []
        self.enemy_hpbars = []

        self.temp_objects = []
    
        self.object_id = 14
        self.moveset_id = None

        self.create_game_room()

        self.object_id = 75
    
    def create_game_room(self):
        self.generate_map()
        self.generate_obstacles()
        self.generate_players()

    def generate_map(self):
        for column in range(MapConstants.BoardWidth.value):
            self.map.append([])
            
            for row in range(MapConstants.BoardHeight.value):
                tile_object = self.generate_object(MovementTile.ArtIndex.value, MovementTile.TemplateId.value, \
                                                    column, row, parent=MovementTile)

                self.map[column].append(tile_object)
    
    def generate_obstacles(self):
        for x, y in ObstacleObject.DefaultLocations.value:
            self.generate_obstacle_object(x, y)

    def generate_players(self):
        ninjas = [FireNinja, WaterNinja, SnowNinja]
        random.shuffle(ninjas)

        for i, ninja in enumerate(ninjas):
            y_coordinate = 2 * i
            self.generate_player_object(MapConstants.PlayerObjectIds.value[i], ninja, 0, y_coordinate)
            self.generate_player_hp_object(0, y_coordinate, ninjaType=ninja)

            print('\n\n', self.players, '\n\n', self.player_hpbars, '\n\n')
        
    def generate_enemies(self):
        count = random.randint(1, 3) if self.room.round_manager.round <= 2 else 4
        random.shuffle(self.room.enemy_manager.default_enemies)

        for i in range(count):
            x, y = self.find_open_coordinate(7, 8, 0, 4)
            self.generate_enemy_object(self.room.enemy_manager.default_enemies[0], x, y)
            self.generate_enemy_hp_object(x, y, enemyType=self.room.enemy_manager.default_enemies[0])
            
            random.shuffle(self.room.enemy_manager.default_enemies)
            
    def generate_enemy_object(self, enemyType, x, y):
        enemy_object = self.generate_object(EnemyObject.ArtIndex.value, EnemyObject.TemplateId.value, \
                                                x, y, parent=EnemyObject, occupant=enemyType)

        self.map[x][y].occupant = enemy_object
        self.enemies.append(enemy_object)

    def generate_enemy_hp_object(self, x, y, enemyType=None):
        enemy_hp_object = self.generate_object(HPObject.ArtIndex.value, HPObject.TemplateId.value, \
                                                x, y, parent=HPObject, occupant=enemyType)

        self.enemy_hpbars.append(enemy_hp_object)

    def generate_obstacle_object(self, x, y):
        obstacle_object = self.generate_object(ObstacleObject.ArtIndex.value, ObstacleObject.TemplateId.value, \
                                                x, y, parent=ObstacleObject)

        self.map[x][y].occupant = obstacle_object
        self.obstacles.append(obstacle_object)
    
    def generate_player_object(self, id, ninja, x, y):
        player_object = Object(id = id, name = f'Actor{id}', art_index = '0:1', template_id = '0:1', \
                        x = x, y = y, parent = PenguinObject, occupant = ninja)

        self.map[x][y].occupant = player_object
        self.players.append(player_object)
    
    def generate_player_hp_object(self, x, y, ninjaType=None):
        player_hp_object = self.generate_object(HPObject.ArtIndex.value, HPObject.TemplateId.value, \
                                                x, y, parent=HPObject, occupant=ninjaType)

        self.player_hpbars.append(player_hp_object)

    def generate_player_ghost(self, ninjaType, x, y):
        ghost_object = self.generate_object('0:1', '0:30017', \
                                                x, y, parent=ninjaType)

        self.temp_objects.append(ghost_object)
        return ghost_object

    def generate_object(self, art_index, template_id, x, y, name=None, parent=None, occupant=None):
        if name is None:
            name = f'Actor{self.object_id}'
        
        obj = Object(id = self.object_id, name = name, art_index = art_index, template_id = template_id, \
                        x = x, y = y, parent = parent, occupant = occupant)
        self.object_id += 1

        return obj
    
    def get_tiles_from_range(self, x, y, tile_range=1):
        tiles = []
        i, delta = -1, 1
        min_xrange, max_xrange = -tile_range + x, tile_range + x + 1
        for x_i in range(min_xrange, max_xrange):
            i += delta
            if i == tile_range:
                delta = -1

            if x_i < 0 or x_i >= MapConstants.BoardWidth.value:
                continue
            
            min_yrange, max_yrange = -i + y, i + y + 1
            for y_i in range(min_yrange, max_yrange):
                if y_i < 0 or y_i >= MapConstants.BoardHeight.value:
                    continue
                
                tiles.append(self.map[x_i][y_i])
        
        return tiles

    async def show_moveable_tiles(self):
        edited_sprite_count = []

        for player in self.room.penguins:

            await self.show_targets(player, player.snow_ninja.current_object.x, player.snow_ninja.current_object.y)

            player.snow_ninja.modified_object = []

            potential_tiles = self.get_tiles_from_range(player.snow_ninja.current_object.x, player.snow_ninja.current_object.y, \
                                                        tile_range=player.ninja.Move.value)
            for tile in potential_tiles:
                await player.send_tag('O_SPRITE', tile.id, \
                                    '0:100063' if tile.occupant is None else '0:100270', '1')
                player.snow_ninja.modified_object.append(tile.id)
            
            edited_sprite_count.append(len(player.snow_ninja.modified_object))

        self.moveset_id = max(edited_sprite_count) + self.object_id 
        self.object_id = self.moveset_id + 1
        await self.room.send_tag('O_HERE', self.moveset_id, '0:100300', 0, 0, 0, 1, 0, 0, 0, \
                                f'Actor{self.moveset_id}', '0:30038', 0, 0, 0)
    
    async def remove_movement_plans(self):
        await self.remove_available_tiles()
        await self.room.send_tag('O_GONE', self.moveset_id)

        for player in self.room.penguins:
            if player.snow_ninja.last_object is not None:
                for potential_player in list(self.temp_objects):
                    if potential_player.parent == player.ninja:
                        await self.room.send_tag('O_GONE', potential_player.id)
                        self.temp_objects.remove(potential_player)
                        break
        
    async def remove_available_tiles(self):
        for player in self.room.penguins:
            for tile_id in player.snow_ninja.modified_object:
                await player.send_tag('O_SPRITE', tile_id, '0:1', 1)

            for old_obj in player.snow_ninja.target_objects:
                await player.send_tag('O_GONE', old_obj.id)

    def update_player_coordinates(self, player):
        for player_object in self.players:
            if player_object.occupant == player.ninja:
                player.snow_ninja.current_object = player_object

                break
    
    async def plan_movement(self, p, tile):
        ghost_object = self.generate_player_ghost(p.ninja, tile.x, tile.y)
        adjusted_x = round(ghost_object.x + PenguinObject.XCoordinateOffset.value, PenguinObject.XCoordinateDecimals.value)
        adjusted_y = round(ghost_object.y + PenguinObject.YCoordinateOffset.value, PenguinObject.YCoordinateDecimals.value)

        await p.room.send_tag('O_HERE', ghost_object.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0, \
                                f'Actor{ghost_object.id}', '0:30017', 0, 1, 0)
        await p.room.send_tag('O_SPRITE', ghost_object.id, p.ninja.SelectedTileAnimation.value, 1, '')
        await p.room.sound_manager.play_sound('0:1840040')

        if p.snow_ninja.last_object is not None:
            for potential_player in list(self.temp_objects):
                if potential_player.parent == p.ninja:
                    await p.room.send_tag('O_GONE', potential_player.id)
                    self.temp_objects.remove(potential_player)
                    break
    
        p.snow_ninja.last_object = tile

        ## TODO: show nearby enemy targets
        await self.show_targets(p, tile.x, tile.y)

    async def show_targets(self, p, x, y):
        if len(p.snow_ninja.target_objects) > 0:
            for old_obj in p.snow_ninja.target_objects:
                await p.send_tag('O_GONE', old_obj.id)
        
        p.snow_ninja.target_objects = []
        potential_tiles = self.get_tiles_from_range(x, y, tile_range=p.ninja.Range.value)
        for tile in potential_tiles:
            if p.ninja == SnowNinja and tile.occupant in [FireNinja, WaterNinja, SnowNinja]: # Healing Target
                print('Unimplemeted')
            
            if tile.occupant in [EnemySly, EnemyTank, EnemyScrap]:
                target_obj = self.generate_object(EnemyTarget.ArtIndex.value, EnemyTarget.TemplateId.value, \
                                                        tile.x, tile.y, parent=EnemyTarget)

                adjusted_x = round(tile.x + EnemyTarget.XCoordinateOffset.value, EnemyTarget.XCoordinateDecimals.value)
                adjusted_y = round(tile.y + EnemyTarget.YCoordinateOffset.value, EnemyTarget.YCoordinateDecimals.value)

                await p.send_tag('O_HERE', target_obj.id, target_obj.art_index, adjusted_x, adjusted_y, \
                                    0, 1, 0, 0, 0, target_obj.name, target_obj.template_id, 0, 0, 0)
                asyncio.create_task(self.room.animation_manager.display_target(p, target_obj))
                await p.room.sound_manager.play_individual_sound(p, target_obj.parent.Sound.value)
            
                p.snow_ninja.target_objects.append(target_obj)

    async def select_enemy(self, p, enemy_id):
        enemy = [e for e in self.enemies if e.id == enemy_id][0]
        p.snow_ninja.curr_target = enemy
        for target_obj in p.snow_ninja.target_objects:
            if target_obj.x == enemy.x and target_obj.y == enemy.y:
                target_obj.parent = SelectedEnemyTarget
                asyncio.create_task(self.room.animation_manager.green_target(p, target_obj))
            else:
                target_obj.parent = EnemyTarget
                asyncio.create_task(self.room.animation_manager.display_target(p, target_obj))

    async def do_move_action(self):
        for i, penguin in enumerate(self.room.penguins):
            if penguin.snow_ninja.last_object is not None:
                await self.room.animation_manager.play_animation(penguin.snow_ninja.current_object, \
                                            penguin.ninja.MoveAnimation.value, 'play_once', \
                                            penguin.ninja.MoveAnimationDuration.value)
                await self.room.animation_manager.play_animation(penguin.snow_ninja.current_object, \
                                            penguin.ninja.IdleAnimation.value, 'loop', \
                                            penguin.ninja.IdleAnimationDuration.value)

                self.map[penguin.snow_ninja.current_object.x][penguin.snow_ninja.current_object.y].occupant = None
                new_tile = penguin.snow_ninja.last_object
                new_tile.occupant = penguin.ninja
                #penguin.snow_ninja.current_object = new_tile

                penguin.snow_ninja.current_object.x = new_tile.x
                penguin.snow_ninja.current_object.y = new_tile.y

                self.player_hpbars[i].x = new_tile.x
                self.player_hpbars[i].y = new_tile.y

                adjusted_x = round(new_tile.x + PenguinObject.XCoordinateOffset.value, PenguinObject.XCoordinateDecimals.value)
                adjusted_y = round(new_tile.y + PenguinObject.YCoordinateOffset.value, PenguinObject.YCoordinateDecimals.value)

                await self.room.send_tag('O_SLIDE', penguin.snow_ninja.current_object.id, adjusted_x, adjusted_y, \
                                            128, penguin.ninja.MoveAnimationDuration.value)
                
                await self.room.sound_manager.play_sound(penguin.ninja.MoveAnimationSound.value)

                adjusted_x = round(self.player_hpbars[i].x + HPObject.XCoordinateOffset.value, HPObject.XCoordinateDecimals.value)
                adjusted_y = round(self.player_hpbars[i].y + HPObject.YCoordinateOffset.value, HPObject.YCoordinateDecimals.value)

                await self.room.send_tag('O_SLIDE', self.player_hpbars[i].id, adjusted_x, adjusted_y, \
                                            128, penguin.ninja.MoveAnimationDuration.value)
                
                penguin.snow_ninja.last_object = None

    def find_open_coordinate(self, x_min, x_max, y_min, y_max):
        if x_min < 0:
            x_min = 0
        if x_max >= MapConstants.BoardWidth.value:
            x_max = MapConstants.BoardWidth.value - 1
        if y_min < 0:
            y_min = 0
        if y_max >= MapConstants.BoardHeight.value:
            y_max = MapConstants.BoardHeight.value - 1
        
        x, y = random.randint(x_min, x_max), random.randint(y_min, y_max)
        while self.map[x][y].occupant is not None:
            x, y = random.randint(x_min, x_max), random.randint(y_min, y_max)
        
        return x, y
    
    def get_enemy_by_id(self, enemy_id):
        for enemy in self.enemies:
            if enemy.id == enemy_id:
                return enemy
        
        return None
    
    def get_tile_by_id(self, tile_id):
        adjusted_object_id = tile_id - 14
        x, y = adjusted_object_id // MapConstants.BoardHeight.value, adjusted_object_id % MapConstants.BoardHeight.value
        try:
            return self.map[x][y]
        except:
            return None
        
    async def send_map(self, p):
        for column in self.map:
            for tile in column:
                adjusted_x = round(tile.x + tile.parent.XCoordinateOffset.value, tile.parent.XCoordinateDecimals.value)
                adjusted_y = round(tile.y + tile.parent.YCoordinateOffset.value, tile.parent.YCoordinateDecimals.value)

                await p.send_tag('O_HERE', tile.id, tile.art_index, adjusted_x, adjusted_y, 0, 1, 0, 0, 0, \
                                    tile.name, tile.template_id, 0, 1, 0)
        
        for obj in self.obstacles:
            adjusted_x = round(obj.x + obj.parent.XCoordinateOffset.value, obj.parent.XCoordinateDecimals.value)
            adjusted_y = round(obj.y + obj.parent.YCoordinateOffset.value, obj.parent.YCoordinateDecimals.value)

            await p.send_tag('O_HERE', obj.id, obj.art_index, adjusted_x, adjusted_y, 0, 1, 0, 0, 0, \
                                obj.name, obj.template_id, 0, 1, 0)
            await p.send_tag('O_SPRITE', obj.id, obj.art_index, 0, '')
        
        for i, player_obj in enumerate(self.players):
            player_hp_obj = self.player_hpbars[i]

            adjusted_x = round(player_obj.x + player_obj.parent.XCoordinateOffset.value, player_obj.parent.XCoordinateDecimals.value)
            adjusted_y = round(player_obj.y + player_obj.parent.YCoordinateOffset.value, player_obj.parent.YCoordinateDecimals.value)

            await p.send_tag('O_MOVE', player_obj.id, adjusted_x, adjusted_y, 128)
            await p.send_tag('P_TILECHANGE', player_obj.x, player_obj.y, OccupiedPenguinSpawnTile.TileUrl.value)
            await p.send_tag('O_ANIM', player_obj.id, player_obj.occupant.IdleAnimation.value, 'loop', \
                                player_obj.occupant.IdleAnimationDuration.value, 1, 0, player_obj.id, i + 1, 0, 0)

            adjusted_x = round(player_hp_obj.x + player_hp_obj.parent.XCoordinateOffset.value, \
                                 player_hp_obj.parent.XCoordinateDecimals.value)
            adjusted_y = round(player_hp_obj.y + player_hp_obj.parent.YCoordinateOffset.value, \
                                 player_hp_obj.parent.YCoordinateDecimals.value)

            await p.send_tag('O_HERE', player_hp_obj.id, player_hp_obj.art_index, adjusted_x, adjusted_y, \
                                0, 1, 0, 0, 0, player_hp_obj.name, player_hp_obj.template_id, 0, 1, 0)
            await p.send_tag('O_SPRITEANIM', player_hp_obj.id, 1, 1, 0, 'play_once', 0)
            await p.send_tag('O_SPRITE', player_hp_obj.id, '0:100395', 1, '')

@dataclass
class Object():
    id: int 
    name: str

    art_index: str
    template_id: str

    x: float
    y: float

    parent: 'typing.Any'
    occupant: 'typing.Any'