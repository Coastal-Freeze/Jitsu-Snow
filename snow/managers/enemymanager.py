import asyncio
from dataclasses import dataclass

import numpy as np
import typing
import random
from snow.constants import EnemySly, EnemyScrap, EnemyTank, UnoccupiedEnemySpawnTile
from snow.constants import FireNinja, WaterNinja, SnowNinja
from snow.constants import MapConstants, EnemyObject, HPObject, PenguinObject


class EnemyManager:

    def __init__(self, room):
        self.room = room
        self.object_manager = room.object_manager
        self.animation_manager = room.animation_manager
        self.sound_manager = room.sound_manager

        self.current_enemies = []
        self.default_enemies = [EnemySly, EnemyScrap, EnemyTank]

    def delete_enemy(self, enemy_id):
        for enemy in self.current_enemies:
            if enemy.id == enemy_id:
                self.current_enemies.remove(enemy)

    def generate_enemies(self):
        self.object_manager.generate_enemies()

        for enemy in self.object_manager.enemies:
            self.current_enemies.append(Enemy(id=enemy.id, tile=enemy, parent=enemy.owner))

    async def do_enemy_turn(self):
        for enemy in self.current_enemies:
            players = self.get_nearby_players(enemy.tile.x, enemy.tile.y)
            if len(players) == 0:  # No surrounding users, let's move
                distances = [np.linalg.norm(
                    np.array([player.tile.x, player.tile.y])
                    - np.array([enemy.tile.x, enemy.tile.y])) for player in self.room.penguins if
                    player.is_alive]
                player = self.room.penguins[distances.index(min(distances))]  # Determine which player to follow
                nonoverlap_coordinate = self.object_manager.find_open_coordinate(
                    player.tile.x,
                    player.tile.x + 1, player.tile.y,
                    player.tile.y + 1)
                new_x, new_y = self.do_astar_algorithm((enemy.tile.x, enemy.tile.y),
                                                       (nonoverlap_coordinate[0], nonoverlap_coordinate[1]),
                                                       tile_range=enemy.parent.range.value)[1]

                await self.move_enemy(enemy, new_x, new_y)

            else:  # Attack nearby user
                ninja = random.choice(players)
                penguin = self.object_manager.get_penguin_by_ninja_type(ninja)
                if penguin.is_alive:
                    return await self.enemy_damage(penguin, enemy)

    async def enemy_damage(self, p, enemy):
        damage = enemy.parent.attack.value
        await self.room.animation_manager.play_animation(enemy.tile,
                                                         enemy.parent.attack_animation.value, 'play_once',
                                                         enemy.parent.attack_animation_duration.value)
        await self.room.animation_manager.play_animation(enemy.tile,
                                                         enemy.parent.idle_animation.value, 'loop',
                                                         enemy.parent.idle_animation_duration.value)
        await self.room.sound_manager.play_sound(enemy.parent.attack_animation_sound.value)
        damage_number, tile_particle = self.object_manager.generate_damage_particle(p.ninja,
                                                                                    p.tile.x,
                                                                                    p.tile.y)

        adjusted_x = round(tile_particle.x + PenguinObject.x_coordinate_offset.value,
                           PenguinObject.x_coordinate_decimals.value)

        adjusted_y = round(tile_particle.y + PenguinObject.y_coordinate_offset.value,
                           PenguinObject.y_coordinate_decimals.value)

        await self.room.send_tag('O_HERE', tile_particle.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                                 f'Actor{tile_particle.id}', '0:30059', 0, 0, 0)
        await self.room.send_tag('O_SPRITE', tile_particle.id, '0:100064', 0)

        adjusted_x = round(damage_number.x + PenguinObject.x_coordinate_offset.value,
                           PenguinObject.x_coordinate_decimals.value)
        adjusted_y = round(damage_number.y + PenguinObject.y_coordinate_offset.value,
                           PenguinObject.y_coordinate_decimals.value)

        await self.room.send_tag('O_HERE', damage_number.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                                 f'Actor{damage_number.id}', '0:30059', 0, 0, 0)
        await self.room.send_tag('O_SPRITE', damage_number.id, '0:100067', damage)
        await self.room.send_tag('O_SPRITEANIM', damage_number.id, damage, damage + 4, 0, 'play_once', 800)

        await self.room.animation_manager.play_animation(p.tile,
                                                         p.ninja.hit_animation.value, 'play_once',
                                                         p.ninja.hit_animation_duration.value)
        await self.room.animation_manager.play_animation(p.tile,
                                                         p.ninja.idle_animation.value, 'loop',
                                                         p.ninja.idle_animation_duration.value)

        await self.room.sound_manager.play_sound(p.ninja.hit_animation_sound.value)

        p.damage += damage
        hpbar = self.object_manager.player_hpbars[
            self.object_manager.players.index(p.tile)]

        hp_percentage = round((p.damage * 100) / p.ninja.health_points.value)
        healthbar = round((hp_percentage * 59) / 100)
        await self.room.send_tag('O_SPRITEANIM', hpbar.id, healthbar - damage, healthbar, 0, 'play_once', 500)

        await asyncio.sleep(0.5)
        await p.room.send_tag('O_GONE', tile_particle.id)
        await p.room.send_tag('O_GONE', damage_number.id)

        if not p.is_alive:
            await self.room.player_manager.player_death(p)

    async def move_enemy(self, enemy, x, y):
        enemy_hp_bar = self.object_manager.enemy_hpbars[
            self.object_manager.enemies.index(enemy.tile)]

        old_x, old_y = enemy.tile.x, enemy.tile.y
        enemy.tile.x = x
        enemy.tile.y = y

        enemy_hp_bar.x = x
        enemy_hp_bar.y = y

        adjusted_x = round(x + EnemyObject.x_coordinate_offset.value, EnemyObject.x_coordinate_decimals.value)
        adjusted_y = round(y + EnemyObject.y_coordinate_offset.value, EnemyObject.y_coordinate_decimals.value)

        await self.room.send_tag('O_SLIDE', enemy.tile.id, adjusted_x, adjusted_y,
                                 128, enemy.parent.move_animation_duration.value)

        await self.room.animation_manager.play_animation(enemy.tile,
                                                         enemy.parent.move_animation.value, 'play_once',
                                                         enemy.parent.move_animation_duration.value)
        await self.room.animation_manager.play_animation(enemy.tile,
                                                         enemy.parent.idle_animation.value, 'loop',
                                                         enemy.parent.idle_animation_duration.value)

        await self.room.sound_manager.play_sound(enemy.parent.move_animation_sound.value)

        adjusted_x = round(x + HPObject.x_coordinate_offset.value, HPObject.x_coordinate_decimals.value)
        adjusted_y = round(y + HPObject.y_coordinate_offset.value, HPObject.y_coordinate_decimals.value)
        await self.room.send_tag('O_SLIDE', enemy_hp_bar.id, adjusted_x, adjusted_y,
                                 128, enemy.parent.move_animation_duration.value)

        self.object_manager.map[x][y].owner = enemy.parent
        self.object_manager.map[old_x][old_y].owner = None
        await self.room.send_tag('P_TILECHANGE', old_x, old_y, UnoccupiedEnemySpawnTile.tile_url.value)

    def get_nearby_players(self, x, y, tile_range=1):
        owners = []
        for x_i in range(x - tile_range, x + tile_range + 1):
            if x_i < 0 or x_i >= MapConstants.board_width.value:
                continue

            for y_i in range(y - tile_range, y + tile_range + 1):
                if y_i < 0 or y_i >= MapConstants.board_height.value or (x_i == x and y_i == y):
                    continue

                if self.object_manager.map[x_i][y_i].owner in [FireNinja, WaterNinja, SnowNinja]:
                    ninja = self.object_manager.map[x_i][y_i].owner
                    penguin = self.object_manager.get_penguin_by_ninja_type(ninja)
                    if penguin.is_alive:
                        owners.append(ninja)

        return owners

    def do_astar_algorithm(self, start, end, tile_range=1):
        start_node = Node(parent=None, position=start, g=0, h=0, f=0)
        end_node = Node(parent=None, position=end, g=0, h=0, f=0)

        open_list, closed_list = [], []
        open_list.append(start_node)

        outer_iterations, max_iterations = 0, (len(self.object_manager.map) // 2) ** 2

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
                if new_pos[0] > (len(self.object_manager.map) - 1) or new_pos[0] < 0 or new_pos[1] > (
                        len(self.object_manager.map[len(self.object_manager.map) - 1]) - 1) or new_pos[1] < 0:
                    continue

                if self.object_manager.map[new_pos[0]][new_pos[1]].owner is not None:
                    continue

                children.append(Node(parent=curr_node, position=new_pos, f=0, g=0, h=0))

            for child in children:
                if len([closed_child for closed_child in closed_list if closed_child.position == child.position]) > 0:
                    continue

                child.g = curr_node.g + 1
                child.h = np.linalg.norm(np.array(child.position) - np.array(end_node.position))
                child.f = child.g + child.h

                if len([open_node for open_node in open_list if
                        child.position == open_node.position and child.g > open_node.g]) > 0:
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

    async def enemy_death(self, enemy, hpbar):
        await self.room.animation_manager.play_animation(enemy,
                                                         enemy.owner.knockout_animation.value, 'play_once',
                                                         2500)
        self.object_manager.map[enemy.x][enemy.y].owner = None
        await asyncio.sleep(2.5)
        await self.room.send_tag('O_GONE', enemy.id)
        await self.room.send_tag('O_GONE', hpbar.id)
        self.delete_enemy(enemy.id)
        self.object_manager.enemies.remove(enemy)
        self.object_manager.enemy_hpbars.remove(hpbar)
        await self.room.sound_manager.play_sound('0:1840006')
        if len(self.object_manager.enemies) == 0:
            self.room.round_manager.round += 1
            await self.room.round_manager.show_round_notice()


@dataclass
class Enemy:
    id: int

    tile: 'typing.Any'
    parent: 'typing.Any'


@dataclass
class Node:
    parent: 'typing.Any'
    position: 'typing.Any'

    g: int
    h: int
    f: int
