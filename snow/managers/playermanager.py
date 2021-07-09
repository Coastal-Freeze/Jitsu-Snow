import asyncio

from snow.constants import PenguinObject


class PlayerManager:

    def __init__(self, room):
        self.room = room
        self.object_manager = room.object_manager
        self.enemy_manager = room.enemy_manager
        self.animation_manager = room.animation_manager
        self.sound_manager = room.sound_manager
        self.enemies = room.object_manager.enemies

    async def player_death(self, p):
        await self.animation_manager.play_animation(p.tile,
                                                    p.ninja.knockout_animation.value, 'play_once',
                                                    2500)
        await asyncio.sleep(2.5)
        await self.animation_manager.play_animation(p.tile,
                                                    p.ninja.knockout_animation_loop.value, 'loop',
                                                    800)
        p.damage = p.ninja.health_points.value
        hp_bar = self.object_manager.player_hpbars[self.object_manager.players.index(p.tile)]
        await self.room.send_tag('O_SPRITEANIM', hp_bar.id, 60, 60, 0, 'play_once', 500)

        await self.sound_manager.play_sound('0:1840007')

    async def player_heal(self, p):
        target = p.heal_target
        penguin = self.object_manager.get_penguin_by_ninja_type(target.parent)

        if not penguin.is_alive:
            return await self.player_revive(penguin, target)

        await self.animation_manager.play_animation(penguin.tile,
                                                    penguin.ninja.heal_animation.value, 'play_once',
                                                    penguin.ninja.heal_animation_duration.value)

        await asyncio.sleep(penguin.heal_animation_duration.value * 0.001)

        await self.animation_manager.play_animation(penguin.tile,
                                                    penguin.ninja.idle_animation.value, 'loop',
                                                    penguin.ninja.idle_animation_duration.value)

        await self.player_healing(penguin, target)

    async def player_revive(self, penguin, target):
        await self.animation_manager.play_animation(penguin.tile,
                                                    penguin.ninja.heal_animation.value, 'play_once',
                                                    penguin.ninja.heal_animation_duration.value)
        await asyncio.sleep(penguin.heal_animation_duration.value * 0.001)
        await self.animation_manager.play_animation(penguin.tile,
                                                    penguin.ninja.idle_animation.value, 'loop',
                                                    penguin.ninja.idle_animation_duration.value)

        await self.player_healing(penguin, target)
        print('TBD')

    async def player_healing(self, penguin, target):
        await penguin.room.sound_manager.play_sound(penguin.ninja.attack_animation_sound.value)
        hp_bar = self.object_manager.player_hpbars[self.object_manager.players.index(target)]
        penguin.damage -= 12
        hp_percentage = round((penguin.damage * 100) / penguin.ninja.health_points.value)
        health_bar = round((hp_percentage * 59) / 100)
        await self.room.send_tag('O_SPRITEANIM', hp_bar.id, health_bar - 12, health_bar, 0, 'play_once', 500)

    async def player_damage(self, p, enemy, damage):
        if enemy not in self.enemies:
            return

        ninja = p.ninja

        await self.animation_manager.play_animation(p.tile,
                                                    ninja.attack_animation.value, 'play_once',
                                                    ninja.attack_animation_duration.value)
        await asyncio.sleep(ninja.attack_animation_duration.value * 0.001)
        await self.animation_manager.play_animation(p.tile,
                                                    ninja.idle_animation.value, 'loop',
                                                    ninja.idle_animation_duration.value)
        await p.room.sound_manager.play_sound(ninja.attack_animation_sound.value)
        damage_number, tile_particle = self.object_manager.generate_damage_particle(enemy, enemy.x, enemy.y)

        adjusted_x = round(tile_particle.x + PenguinObject.x_coordinate_offset.value,
                           PenguinObject.x_coordinate_decimals.value)
        adjusted_y = round(tile_particle.y + PenguinObject.y_coordinate_offset.value,
                           PenguinObject.y_coordinate_decimals.value)

        await p.room.send_tag('O_HERE', tile_particle.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                              f'Actor{tile_particle.id}', '0:30059', 0, 0, 0)
        await p.room.send_tag('O_SPRITE', tile_particle.id, '0:100064', 0)

        adjusted_x = round(damage_number.x + PenguinObject.x_coordinate_offset.value,
                           PenguinObject.x_coordinate_decimals.value)
        adjusted_y = round(damage_number.y + PenguinObject.y_coordinate_offset.value,
                           PenguinObject.y_coordinate_decimals.value)

        await p.room.send_tag('O_HERE', damage_number.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                              f'Actor{damage_number.id}', '0:30059', 0, 0, 0)
        await p.room.send_tag('O_SPRITE', damage_number.id, '0:100067', damage)
        await p.room.send_tag('O_SPRITEANIM', damage_number.id, damage, damage + 4, 0, 'play_once', 800)

        await asyncio.sleep(0.5)
        await p.room.send_tag('O_GONE', tile_particle.id)
        await p.room.send_tag('O_GONE', damage_number.id)

        await self.animation_manager.play_animation(enemy,
                                                    enemy.owner.hit_animation.value, 'play_once',
                                                    enemy.owner.hit_animation_duration.value)
        await asyncio.sleep(enemy.owner.hit_animation_duration.value * 0.001)
        await self.animation_manager.play_animation(enemy,
                                                    enemy.owner.idle_animation.value, 'loop',
                                                    enemy.owner.idle_animation_duration.value)
        await self.sound_manager.play_sound(enemy.owner.hit_animationSound.value)

        hp_bar = self.object_manager.enemy_hpbars[self.enemies.index(enemy)]
        enemy.damage += damage

        hp_percentage = round((enemy.damage * 100) / enemy.owner.health_points.value)
        health_bar = round((hp_percentage * 59) / 100)
        await self.room.send_tag('O_SPRITEANIM', hp_bar.id, health_bar - damage, health_bar, 0, 'play_once', 500)

        if enemy.damage >= enemy.owner.health_points.value:
            await self.enemy_manager.enemy_death(enemy, hp_bar)
