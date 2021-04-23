import asyncio
from dataclasses import dataclass

import numpy as np
import typing
from houdini.constants import EnemySly, EnemyScrap, EnemyTank, UnoccupiedEnemySpawnTile
from houdini.constants import FireNinja, WaterNinja, SnowNinja
from houdini.constants import MapConstants, EnemyObject, HPObject, PenguinObject


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
                    np.array([player.snow_ninja.tile.x, player.snow_ninja.tile.y])
                    - np.array([enemy.tile.x, enemy.tile.y])) for player in self.room.penguins if
                    player.is_alive]
                player = self.room.penguins[distances.index(min(distances))]  # Determine which player to follow
                nonoverlap_coordinate = self.object_manager.find_open_coordinate(
                    player.snow_ninja.tile.x,
                    player.snow_ninja.tile.x + 1, player.snow_ninja.tile.y,
                    player.snow_ninja.tile.y + 1)
                new_x, new_y = self.do_astar_algorithm((enemy.tile.x, enemy.tile.y),
                                                       (nonoverlap_coordinate[0], nonoverlap_coordinate[1]),
                                                       tile_range=enemy.parent.Range.value)[1]

                await self.move_enemy(enemy, new_x, new_y)

                await asyncio.sleep(3)
            else:  # Attack nearby user
                for ninja in players:
                    penguin = self.object_manager.get_penguin_by_ninja_type(ninja)
                    if penguin.is_alive:
                        return await self.enemy_damage(penguin, enemy)
                    else:
                        return await self.room.player_manager.player_death(penguin)
            await asyncio.sleep(1.5)

    async def enemy_damage(self, p, enemy):
        damage = enemy.parent.Attack.value
        await self.room.animation_manager.play_animation(enemy.tile,
                                                         enemy.parent.AttackAnimation.value, 'play_once',
                                                         enemy.parent.AttackAnimationDuration.value)
        await self.room.animation_manager.play_animation(enemy.tile,
                                                         enemy.parent.IdleAnimation.value, 'loop',
                                                         enemy.parent.IdleAnimationDuration.value)
        await self.room.sound_manager.play_sound(enemy.parent.AttackAnimationSound.value)
        damage_number, tile_particle = self.object_manager.generate_damage_particle(p.snow_ninja.ninja,
                                                                                    p.snow_ninja.tile.x,
                                                                                    p.snow_ninja.tile.y)

        adjusted_x = round(tile_particle.x + PenguinObject.XCoordinateOffset.value,
                           PenguinObject.XCoordinateDecimals.value)
        adjusted_y = round(tile_particle.y + PenguinObject.YCoordinateOffset.value,
                           PenguinObject.YCoordinateDecimals.value)

        await self.room.send_tag('O_HERE', tile_particle.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                                 f'Actor{tile_particle.id}', '0:30059', 0, 0, 0)
        await self.room.send_tag('O_SPRITE', tile_particle.id, '0:100064', 0)

        adjusted_x = round(damage_number.x + PenguinObject.XCoordinateOffset.value,
                           PenguinObject.XCoordinateDecimals.value)
        adjusted_y = round(damage_number.y + PenguinObject.YCoordinateOffset.value,
                           PenguinObject.YCoordinateDecimals.value)

        await self.room.send_tag('O_HERE', damage_number.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                                 f'Actor{damage_number.id}', '0:30059', 0, 0, 0)
        await self.room.send_tag('O_SPRITE', damage_number.id, '0:100067', damage)
        await self.room.send_tag('O_SPRITEANIM', damage_number.id, damage, damage + 4, 0, 'play_once', 800)

        await self.room.animation_manager.play_animation(p.snow_ninja.tile,
                                                         p.snow_ninja.ninja.HitAnimation.value, 'play_once',
                                                         p.snow_ninja.ninja.HitAnimationDuration.value)
        await self.room.animation_manager.play_animation(p.snow_ninja.tile,
                                                         p.snow_ninja.ninja.IdleAnimation.value, 'loop',
                                                         p.snow_ninja.ninja.IdleAnimationDuration.value)

        await self.room.sound_manager.play_sound(p.snow_ninja.ninja.HitAnimationSound.value)

        p.snow_ninja.damage = max(0, min(p.snow_ninja.damage + damage, p.snow_ninja.ninja.HealthPoints.value))
        hpbar = self.object_manager.player_hpbars[
            self.object_manager.players.index(p.snow_ninja.tile)]

        hp_percentage = round((p.snow_ninja.damage * 100) / p.snow_ninja.ninja.HealthPoints.value)
        healthbar = round((hp_percentage * 59) / 100)
        await self.room.send_tag('O_SPRITEANIM', hpbar.id, healthbar - damage, healthbar, 0, 'play_once', 500)

        await asyncio.sleep(0.5)
        await p.room.send_tag('O_GONE', tile_particle.id)
        await p.room.send_tag('O_GONE', damage_number.id)

    async def move_enemy(self, enemy, x, y):
        enemy_hp_bar = self.object_manager.enemy_hpbars[
            self.object_manager.enemies.index(enemy.tile)]

        old_x, old_y = enemy.tile.x, enemy.tile.y
        enemy.tile.x = x
        enemy.tile.y = y

        enemy_hp_bar.x = x
        enemy_hp_bar.y = y

        adjusted_x = round(x + EnemyObject.XCoordinateOffset.value, EnemyObject.XCoordinateDecimals.value)
        adjusted_y = round(y + EnemyObject.YCoordinateOffset.value, EnemyObject.YCoordinateDecimals.value)

        await self.room.send_tag('O_SLIDE', enemy.tile.id, adjusted_x, adjusted_y,
                                 128, enemy.parent.MoveAnimationDuration.value)

        await self.room.animation_manager.play_animation(enemy.tile,
                                                         enemy.parent.MoveAnimation.value, 'play_once',
                                                         enemy.parent.MoveAnimationDuration.value)
        await self.room.animation_manager.play_animation(enemy.tile,
                                                         enemy.parent.IdleAnimation.value, 'loop',
                                                         enemy.parent.IdleAnimationDuration.value)

        await self.room.sound_manager.play_sound(enemy.parent.MoveAnimationSound.value)

        adjusted_x = round(x + HPObject.XCoordinateOffset.value, HPObject.XCoordinateDecimals.value)
        adjusted_y = round(y + HPObject.YCoordinateOffset.value, HPObject.YCoordinateDecimals.value)
        await self.room.send_tag('O_SLIDE', enemy_hp_bar.id, adjusted_x, adjusted_y,
                                 128, enemy.parent.MoveAnimationDuration.value)

        self.object_manager.map[x][y].owner = enemy.parent
        self.object_manager.map[old_x][old_y].owner = None
        await self.room.send_tag('P_TILECHANGE', old_x, old_y, UnoccupiedEnemySpawnTile.TileUrl.value)

    def get_nearby_players(self, x, y, tile_range=1):
        owners = []
        for x_i in range(x - tile_range, x + tile_range + 1):
            if x_i < 0 or x_i >= MapConstants.BoardWidth.value:
                continue

            for y_i in range(y - tile_range, y + tile_range + 1):
                if y_i < 0 or y_i >= MapConstants.BoardHeight.value or (x_i == x and y_i == y):
                    continue

                if self.object_manager.map[x_i][y_i].owner in [FireNinja, WaterNinja, SnowNinja]:
                    owners.append(self.object_manager.map[x_i][y_i].owner)

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
                                                         enemy.owner.KnockoutAnimation.value, 'play_once',
                                                         2500)
        self.object_manager.map[enemy.x][enemy.y].owner = None
        await asyncio.sleep(2.5)
        await self.room.send_tag('O_GONE', enemy.id)
        await self.room.send_tag('O_GONE', hpbar.id)
        self.room.enemy_manager.delete_enemy(enemy.id)
        self.object_manager.enemies.remove(enemy)
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
