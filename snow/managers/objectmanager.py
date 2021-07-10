import asyncio
import random
import typing
from dataclasses import dataclass

from snow.constants import FireNinja, WaterNinja, SnowNinja
from snow.constants import MapConstants, MovementTile, EnemyObject, \
    PenguinObject, HPObject, ObstacleObject, EnemyTarget, SelectedEnemyTarget, SelectedPenguinTarget, PenguinTarget
from snow.constants import OccupiedPenguinSpawnTile
from loguru import logger

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
        self.check_marks = []

        self.object_id = 14
        self.moveset_id = None

        self.create_game_room()

        self.object_id = 75

    def create_game_room(self):
        self.generate_map()
        self.generate_obstacles()
        self.generate_players()

    def generate_map(self):
        for column in range(MapConstants.board_width.value):
            self.map.append([])

            for row in range(MapConstants.board_height.value):
                tile_object = self.generate_object(MovementTile.art_index.value, MovementTile.template_id.value,
                                                   column, row, parent=MovementTile)

                self.map[column].append(tile_object)

    def generate_obstacles(self):
        for x, y in ObstacleObject.default_locations.value:
            self.generate_obstacle_object(x, y)

    def get_alive_ninjas(self):
        return [p for p in self.room.penguins if p.is_alive]

    def generate_players(self):
        ninjas = [FireNinja, WaterNinja, SnowNinja]
        random.shuffle(ninjas)

        for i, ninja in enumerate(ninjas):
            y_coordinate = 2 * i
            self.generate_player_object(MapConstants.player_object_ids.value[i], ninja, 0, y_coordinate)
            self.generate_player_hp_object(0, y_coordinate, ninja_type=ninja)

            print('\n\n', self.players, '\n\n', self.player_hpbars, '\n\n')

    def generate_enemies(self):
        count = random.randint(1, 3) if self.room.round_manager.round <= 2 else 4
        random.shuffle(self.room.enemy_manager.default_enemies)

        for i in range(count):
            x, y = self.find_open_coordinate(7, 8, 0, 4)
            self.generate_enemy_object(self.room.enemy_manager.default_enemies[0], x, y)
            self.generate_enemy_hp_object(x, y, enemy_type=self.room.enemy_manager.default_enemies[0])

            random.shuffle(self.room.enemy_manager.default_enemies)

    def generate_check_mark(self, ninja_type, x, y):
        check_mark = self.generate_object('0:1', '0:30049',
                                          x, y, parent=ninja_type)

        self.check_marks.append(check_mark)
        return check_mark

    def generate_damage_particle(self, ninja_type, x, y):
        damage_number = self.generate_object('0:1', '0:30059',
                                             x, y, parent=ninja_type)
        tile_particle = self.generate_object('0:1', '0:30059',
                                             x, y, parent=ninja_type)

        self.temp_objects.append(damage_number)
        self.temp_objects.append(tile_particle)
        return damage_number, tile_particle

    def get_healthbar(self, ninja_type):
        for hpbar in self.player_hpbars:
            if hpbar.owner == ninja_type:
                return hpbar

    def generate_enemy_object(self, enemy_type, x, y):
        enemy_object = self.generate_object(EnemyObject.art_index.value, EnemyObject.template_id.value,
                                            x, y, parent=EnemyObject, owner=enemy_type)

        self.map[x][y].owner = enemy_object
        self.enemies.append(enemy_object)

    def generate_enemy_hp_object(self, x, y, enemy_type=None):
        enemy_hp_object = self.generate_object(HPObject.art_index.value, HPObject.template_id.value,
                                               x, y, parent=HPObject, owner=enemy_type)

        self.enemy_hpbars.append(enemy_hp_object)

    def generate_obstacle_object(self, x, y):
        obstacle_object = self.generate_object(ObstacleObject.art_index.value, ObstacleObject.template_id.value,
                                               x, y, parent=ObstacleObject)

        self.map[x][y].owner = obstacle_object
        self.obstacles.append(obstacle_object)

    def generate_player_object(self, obj_id, ninja, x, y):
        player_object = Object(id=obj_id, name=f'Actor{obj_id}', art_index='0:1', template_id='0:1',
                               x=x, y=y, parent=PenguinObject, owner=ninja)

        self.map[x][y].owner = player_object
        self.players.append(player_object)

    def generate_player_hp_object(self, x, y, ninja_type=None):
        player_hp_object = self.generate_object(HPObject.art_index.value, HPObject.template_id.value,
                                                x, y, parent=HPObject, owner=ninja_type)

        self.player_hpbars.append(player_hp_object)

    def generate_player_ghost(self, ninja_type, x, y):
        ghost_object = self.generate_object('0:1', '0:30017',
                                            x, y, parent=ninja_type)

        self.temp_objects.append(ghost_object)
        return ghost_object

    def generate_object(self, art_index, template_id, x, y, name=None, parent=None, owner=None):
        if name is None:
            name = f'Actor{self.object_id}'

        obj = Object(id=self.object_id, name=name, art_index=art_index, template_id=template_id,
                     x=x, y=y, parent=parent, owner=owner)
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

            if x_i < 0 or x_i >= MapConstants.board_width.value:
                continue

            min_yrange, max_yrange = -i + y, i + y + 1
            for y_i in range(min_yrange, max_yrange):
                if y_i < 0 or y_i >= MapConstants.board_height.value:
                    continue

                tiles.append(self.map[x_i][y_i])

        return tiles

    async def show_moveable_tiles(self):
        edited_sprite_count = []

        for player in self.get_alive_ninjas():
            await self.show_targets(player, player.tile.x, player.tile.y)

            player.edited_objects = []

            potential_tiles = self.get_tiles_from_range(player.tile.x,
                                                        player.tile.y,
                                                        tile_range=player.ninja.move.value)
            for tile in potential_tiles:
                await player.send_tag('O_SPRITE', tile.id,
                                      '0:100063' if tile.owner is None else '0:100270', '1')
                player.edited_objects.append(tile.id)

            edited_sprite_count.append(len(player.edited_objects))

        self.moveset_id = max(edited_sprite_count) + self.object_id
        self.object_id = self.moveset_id + 1
        await self.room.send_tag('O_HERE', self.moveset_id, '0:100300', 0, 0, 0, 1, 0, 0, 0,
                                 f'Actor{self.moveset_id}', '0:30038', 0, 0, 0, f=self.is_player_dead())

    async def remove_movement_plans(self):
        await self.remove_available_tiles()
        await self.room.send_tag('O_GONE', self.moveset_id)

        for player in self.get_alive_ninjas():
            if player.last_object is not None:
                for potential_player in list(self.temp_objects):
                    if potential_player.parent == player.ninja:
                        await self.room.send_tag('O_GONE', potential_player.id)
                        self.temp_objects.remove(potential_player)

        for check_mark in self.check_marks:
            await self.room.send_tag('O_GONE', check_mark.id)
            self.check_marks.remove(check_mark)

    async def remove_available_tiles(self):
        for player in self.get_alive_ninjas():
            for tile_id in player.edited_objects:
                await player.send_tag('O_SPRITE', tile_id, '0:1', 1)

            for old_obj in player.target_objects:
                await player.send_tag('O_GONE', old_obj.id)
            for old_obj in player.heal_target_objects:
                await player.send_tag('O_GONE', old_obj.id)

    def update_player_coordinates(self, player):
        for player_object in self.players:
            if player_object.owner == player.ninja:
                player.tile = player_object

    async def check_mark(self, p):
        x, y = p.tile.x, p.tile.y
        check_object = self.generate_check_mark(p.ninja, x, y)
        adjusted_x = round(check_object.x + PenguinObject.x_coordinate_offset.value,
                           PenguinObject.x_coordinate_decimals.value)
        adjusted_y = round(check_object.y + PenguinObject.y_coordinate_offset.value,
                           PenguinObject.y_coordinate_decimals.value)
        await p.room.send_tag('O_HERE', check_object.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                              f'Actor{check_object.id}', '0:30049', 0, 0, 0)
        await p.room.send_tag('O_SPRITE', check_object.id, '0:100195', 0)
        await p.room.sound_manager.play_sound('0:1840040')
        p.confirm = True
        if all(map(lambda ninja: ninja.confirm, self.get_alive_ninjas())):
            self.room.round_manager.callback.cancel()
            await self.room.round_manager.expire_timer()

    async def plan_movement(self, p, tile):
        if p.last_object is not None:
            for potential_player in list(self.temp_objects):
                if potential_player.parent == p.ninja:
                    await p.room.send_tag('O_GONE', potential_player.id)
                    self.temp_objects.remove(potential_player)

        ghost_object = self.generate_player_ghost(p.ninja, tile.x, tile.y)
        adjusted_x = round(ghost_object.x + PenguinObject.x_coordinate_offset.value,
                           PenguinObject.x_coordinate_decimals.value)
        adjusted_y = round(ghost_object.y + PenguinObject.y_coordinate_offset.value,
                           PenguinObject.y_coordinate_decimals.value)

        await p.room.send_tag('O_HERE', ghost_object.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                              f'Actor{ghost_object.id}', '0:30017', 0, 1, 0)
        await p.room.send_tag('O_SPRITE', ghost_object.id, p.ninja.selected_tile_animation.value, 1, '')
        await p.room.sound_manager.play_sound('0:1840040')

        p.last_object = tile

        # TODO: show nearby enemy targets
        await self.show_targets(p, tile.x, tile.y)

    async def show_targets(self, p, x, y):
        if len(p.target_objects) > 0:
            for old_obj in p.target_objects:
                await p.send_tag('O_GONE', old_obj.id)
        if len(p.heal_target_objects) > 0:
            for old_obj in p.heal_target_objects:
                await p.send_tag('O_GONE', old_obj.id)

        p.target_objects = []
        p.heal_target_objects = []
        potential_tiles = self.get_tiles_from_range(x, y, tile_range=p.ninja.range.value)
        for tile in potential_tiles:
            await self.generate_heal_tiles(p, tile)
            if tile.owner in self.room.enemy_manager.default_enemies:
                target_obj = self.generate_object(EnemyTarget.art_index.value, EnemyTarget.template_id.value,
                                                  tile.x, tile.y, parent=EnemyTarget)

                adjusted_x = round(tile.x + EnemyTarget.x_coordinate_offset.value,
                                   EnemyTarget.x_coordinate_decimals.value)
                adjusted_y = round(tile.y + EnemyTarget.y_coordinate_offset.value,
                                   EnemyTarget.y_coordinate_decimals.value)

                await p.send_tag('O_HERE', target_obj.id, target_obj.art_index, adjusted_x, adjusted_y,
                                 0, 1, 0, 0, 0, target_obj.name, target_obj.template_id, 0, 0, 0)
                asyncio.create_task(self.room.animation_manager.display_target(p, target_obj))
                await p.room.sound_manager.play_individual_sound(p, target_obj.parent.sound.value)

                p.target_objects.append(target_obj)
        reviving_tiles = self.get_tiles_from_range(x, y, tile_range=1)
        for tile in reviving_tiles:
            for penguin in self.room.penguins:
                if tile.owner == penguin.ninja and not penguin.is_alive:
                    await self.generate_heal_tiles(p, tile)

    async def generate_heal_tiles(self, p, tile):
        if p.ninja == SnowNinja and tile.owner in [FireNinja, WaterNinja]:  # Healing Target
            target_obj = self.generate_object(PenguinTarget.art_index.value, PenguinTarget.template_id.value,
                                              tile.x, tile.y, parent=PenguinTarget)

            adjusted_x = round(tile.x + PenguinTarget.x_coordinate_offset.value,
                               PenguinTarget.x_coordinate_decimals.value)
            adjusted_y = round(tile.y + PenguinTarget.y_coordinate_offset.value,
                               PenguinTarget.y_coordinate_decimals.value)

            await p.send_tag('O_HERE', target_obj.id, target_obj.art_index, adjusted_x, adjusted_y,
                             0, 1, 0, 0, 0, target_obj.name, target_obj.template_id, 0, 0, 0)
            asyncio.create_task(self.room.animation_manager.display_target(p, target_obj))
            await p.room.sound_manager.play_individual_sound(p, target_obj.parent.sound.value)
            p.heal_target_objects.append(target_obj)

    async def select_enemy(self, p, enemy_id):
        enemy = [e for e in self.enemies if e.id == enemy_id][0]
        p.current_target = enemy
        for target_obj in p.target_objects:
            if target_obj.x == enemy.x and target_obj.y == enemy.y:
                target_obj.parent = SelectedEnemyTarget
                asyncio.create_task(self.room.animation_manager.green_target(p, target_obj))
            else:
                target_obj.parent = EnemyTarget
                asyncio.create_task(self.room.animation_manager.display_target(p, target_obj))

    async def heal_penguin(self, p, tile_id):
        penguin = [e for e in self.room.penguins if e.tile.id == tile_id][0]

        p.heal_target = penguin
        for target_obj in p.heal_target_objects:
            if target_obj.x == penguin.tile.x and target_obj.y == penguin.tile.y:
                target_obj.parent = SelectedPenguinTarget
                asyncio.create_task(self.room.animation_manager.green_target(p, target_obj))
            else:
                target_obj.parent = PenguinTarget
                asyncio.create_task(self.room.animation_manager.display_target(p, target_obj))

    async def player_move(self, penguin):
        await self.room.animation_manager.play_animation(penguin.tile,
                                                         penguin.ninja.move_animation.value,
                                                         'play_once',
                                                         penguin.ninja.move_animation_duration.value)
        await self.room.animation_manager.play_animation(penguin.tile,
                                                         penguin.ninja.idle_animation.value, 'loop',
                                                         penguin.ninja.idle_animation_duration.value)

        self.map[penguin.tile.x][penguin.tile.y].owner = None
        new_tile = penguin.last_object
        new_tile.owner = penguin.ninja

        penguin.tile.x = new_tile.x
        penguin.tile.y = new_tile.y

        healthbar = self.get_healthbar(penguin.ninja)

        healthbar.x = new_tile.x
        healthbar.y = new_tile.y

        adjusted_x = round(new_tile.x + PenguinObject.x_coordinate_offset.value,
                           PenguinObject.x_coordinate_decimals.value)
        adjusted_y = round(new_tile.y + PenguinObject.y_coordinate_offset.value,
                           PenguinObject.y_coordinate_decimals.value)

        await self.room.send_tag('O_SLIDE', penguin.tile.id, adjusted_x, adjusted_y,
                                 128, penguin.ninja.move_animation_duration.value)

        await self.room.sound_manager.play_sound(penguin.ninja.move_animation_sound.value)

        adjusted_x = round(healthbar.x + HPObject.x_coordinate_offset.value,
                           HPObject.x_coordinate_decimals.value)
        adjusted_y = round(healthbar.y + HPObject.y_coordinate_offset.value,
                           HPObject.y_coordinate_decimals.value)

        await self.room.send_tag('O_SLIDE', healthbar.id, adjusted_x, adjusted_y,
                                 128, penguin.ninja.move_animation_duration.value)

        penguin.last_object = None
        await asyncio.sleep(penguin.ninja.move_animation_duration.value * 0.001)
        logger.error(penguin.current_target)

    async def do_move_action(self):
        for penguin in self.get_alive_ninjas():
            if penguin.last_object is not None:
                await self.player_move(penguin)
            if penguin.current_target is not None:
                await self.room.player_manager.player_damage(penguin, penguin.current_target,
                                                             penguin.ninja.attack.value)
                penguin.current_target = None

    def find_open_coordinate(self, x_min, x_max, y_min, y_max):
        if x_min < 0:
            x_min = 0
        if x_max >= MapConstants.board_width.value:
            x_max = MapConstants.board_width.value - 1
        if y_min < 0:
            y_min = 0
        if y_max >= MapConstants.board_height.value:
            y_max = MapConstants.board_height.value - 1

        x, y = random.randint(x_min, x_max), random.randint(y_min, y_max)
        while self.map[x][y].owner is not None:
            x, y = random.randint(x_min, x_max), random.randint(y_min, y_max)

        return x, y

    def get_enemy_by_id(self, enemy_id):
        for enemy in self.enemies:
            if enemy.id == enemy_id:
                return enemy

        return None

    def get_penguin_by_id(self, ninja_id):
        for penguin in self.room.penguins:
            if penguin.tile.id == ninja_id:
                return penguin

        return None

    def get_penguin_by_ninja_type(self, ninja_type):
        for player in self.room.penguins:
            if player.ninja == ninja_type:
                return player

    def get_hpbar_by_ninja_type(self, ninja_type):
        for hpbar in self.player_hpbars:
            if hpbar.owner == ninja_type:
                return hpbar

    def get_heal_target_by_id(self, player, tile_id):
        for tile in player.heal_target_objects:
            if tile.id in tile_id:
                return True
        return False

    def get_y_direction(self, y, compare_x):
        if y >= compare_x:
            return 'north'
        else:
            return ''

    def get_direction(self, x, compare_x):
        if x <= compare_x:
            return 'east'
        else:
            return ''

    def get_tile_by_id(self, tile_id):
        adjusted_object_id = tile_id - 14
        x, y = adjusted_object_id // MapConstants.board_height.value, \
               adjusted_object_id % MapConstants.board_height.value
        try:
            return self.map[x][y]
        except KeyError:
            return None

    def is_player_dead(self):
        def f(player):
            return player.is_alive

        return f

    async def send_map(self, p):
        for column in self.map:
            for tile in column:
                adjusted_x = round(tile.x + tile.parent.x_coordinate_offset.value,
                                   tile.parent.x_coordinate_decimals.value)
                adjusted_y = round(tile.y + tile.parent.y_coordinate_offset.value,
                                   tile.parent.y_coordinate_decimals.value)

                await p.send_tag('O_HERE', tile.id, tile.art_index, adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                                 tile.name, tile.template_id, 0, 1, 0)

        for obj in self.obstacles:
            adjusted_x = round(obj.x + obj.parent.x_coordinate_offset.value, obj.parent.x_coordinate_decimals.value)
            adjusted_y = round(obj.y + obj.parent.y_coordinate_offset.value, obj.parent.y_coordinate_decimals.value)

            await p.send_tag('O_HERE', obj.id, obj.art_index, adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                             obj.name, obj.template_id, 0, 1, 0)
            await p.send_tag('O_SPRITE', obj.id, obj.art_index, 0, '')

        for i, player_obj in enumerate(self.players):
            player_hp_obj = self.player_hpbars[i]
            player_hp_obj.x, player_hp_obj.y = player_obj.x, player_obj.y

            adjusted_x = round(player_obj.x + player_obj.parent.x_coordinate_offset.value,
                               player_obj.parent.x_coordinate_decimals.value)
            adjusted_y = round(player_obj.y + player_obj.parent.y_coordinate_offset.value,
                               player_obj.parent.y_coordinate_decimals.value)

            await p.send_tag('O_MOVE', player_obj.id, adjusted_x, adjusted_y, 128)
            await p.send_tag('P_TILECHANGE', player_obj.x, player_obj.y, OccupiedPenguinSpawnTile.tile_url.value)
            await p.send_tag('O_ANIM', player_obj.id, player_obj.owner.idle_animation.value, 'loop',
                             player_obj.owner.idle_animation_duration.value, 1, 0, player_obj.id, i + 1, 0, 0)

            adjusted_x = round(player_hp_obj.x + player_hp_obj.parent.x_coordinate_offset.value,
                               player_hp_obj.parent.x_coordinate_decimals.value)
            adjusted_y = round(player_hp_obj.y + player_hp_obj.parent.y_coordinate_offset.value,
                               player_hp_obj.parent.y_coordinate_decimals.value)

            await p.send_tag('O_HERE', player_hp_obj.id, player_hp_obj.art_index, adjusted_x, adjusted_y,
                             0, 1, 0, 0, 0, player_hp_obj.name, player_hp_obj.template_id, 0, 1, 0)
            await p.send_tag('O_SPRITEANIM', player_hp_obj.id, 1, 1, 0, 'play_once', 0)
            await p.send_tag('O_SPRITE', player_hp_obj.id, '0:100395', 1, '')


@dataclass
class Object:
    id: int
    name: str

    art_index: str
    template_id: str

    x: float
    y: float

    parent: 'typing.Any'
    owner: 'typing.Any'

    damage: int = 0
