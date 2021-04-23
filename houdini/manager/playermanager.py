import asyncio

from houdini.constants import PenguinObject


class PlayerManager:

    def __init__(self, room):
        self.room = room
        self.object_manager = room.object_manager
        self.enemy_manager = room.enemy_manager
        self.animation_manager = room.animation_manager
        self.sound_manager = room.sound_manager
        self.enemies = room.object_manager.enemies

    async def player_death(self, p):
        n_obj = p.snow_ninja
        await self.animation_manager.play_animation(n_obj.tile,
                                                    n_obj.ninja.KnockoutAnimation.value, 'play_once',
                                                    2500)
        await asyncio.sleep(2.5)
        await self.animation_manager.play_animation(n_obj.tile,
                                                    n_obj.ninja.KnockoutAnimationLoop.value, 'loop',
                                                    800)
        n_obj.damage = n_obj.ninja.HealthPoints.value
        hpbar = self.object_manager.player_hpbars[self.object_manager.players.index(n_obj.tile)]
        await self.room.send_tag('O_SPRITEANIM', hpbar.id, 60, 60, 0, 'play_once', 500)

        await self.sound_manager.play_sound('0:1840007')

    async def player_heal(self, p):
        target = p.heal_target
        penguin = self.object_manager.get_penguin_by_ninja_type(target.parent)

        if not penguin.is_alive:
            return await self.player_revive(penguin, target)

        await self.animation_manager.play_animation(penguin.snow_ninja.tile,
                                                    penguin.snow_ninja.ninja.HealAnimation.value, 'play_once',
                                                    penguin.snow_ninja.ninja.HealAnimationDuration.value)

        await asyncio.sleep(penguin.snow_ninja.HealAnimationDuration.value * 0.001)

        await self.animation_manager.play_animation(penguin.snow_ninja.tile,
                                                    penguin.snow_ninja.ninja.IdleAnimation.value, 'loop',
                                                    penguin.snow_ninja.ninja.IdleAnimationDuration.value)

        await self.player_healing(penguin, target)

    async def player_revive(self, penguin, target):
        await self.animation_manager.play_animation(penguin.snow_ninja.tile,
                                                    penguin.snow_ninja.ninja.HealAnimation.value, 'play_once',
                                                    penguin.snow_ninja.ninja.HealAnimationDuration.value)
        await asyncio.sleep(penguin.snow_ninja.HealAnimationDuration.value * 0.001)
        await self.animation_manager.play_animation(penguin.snow_ninja.tile,
                                                    penguin.snow_ninja.ninja.IdleAnimation.value, 'loop',
                                                    penguin.snow_ninja.ninja.IdleAnimationDuration.value)

        await self.player_healing(penguin, target)
        print('TBD')

    async def player_healing(self, penguin, target):
        await penguin.room.sound_manager.play_sound(penguin.snow_ninja.ninja.AttackAnimationSound.value)
        hpbar = self.object_manager.player_hpbars[self.object_manager.players.index(target)]
        penguin.snow_ninja.damage -= 12
        hp_percentage = round((penguin.snow_ninja.damage * 100) / penguin.snow_ninja.ninja.HealthPoints.value)
        healthbar = round((hp_percentage * 59) / 100)
        await self.room.send_tag('O_SPRITEANIM', hpbar.id, healthbar - 12, healthbar, 0, 'play_once', 500)

    async def player_damage(self, p, enemy, damage):
        if enemy not in self.enemies:
            return

        player = p.snow_ninja
        ninja = player.ninja

        await self.animation_manager.play_animation(player.tile,
                                                    ninja.AttackAnimation.value, 'play_once',
                                                    ninja.AttackAnimationDuration.value)
        await asyncio.sleep(ninja.AttackAnimationDuration.value * 0.001)
        await self.animation_manager.play_animation(player.tile,
                                                    ninja.IdleAnimation.value, 'loop',
                                                    ninja.IdleAnimationDuration.value)
        await p.room.sound_manager.play_sound(ninja.AttackAnimationSound.value)
        damage_number, tile_particle = self.object_manager.generate_damage_particle(enemy, enemy.x, enemy.y)

        adjusted_x = round(tile_particle.x + PenguinObject.XCoordinateOffset.value,
                           PenguinObject.XCoordinateDecimals.value)
        adjusted_y = round(tile_particle.y + PenguinObject.YCoordinateOffset.value,
                           PenguinObject.YCoordinateDecimals.value)

        await p.room.send_tag('O_HERE', tile_particle.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                              f'Actor{tile_particle.id}', '0:30059', 0, 0, 0)
        await p.room.send_tag('O_SPRITE', tile_particle.id, '0:100064', 0)

        adjusted_x = round(damage_number.x + PenguinObject.XCoordinateOffset.value,
                           PenguinObject.XCoordinateDecimals.value)
        adjusted_y = round(damage_number.y + PenguinObject.YCoordinateOffset.value,
                           PenguinObject.YCoordinateDecimals.value)

        await p.room.send_tag('O_HERE', damage_number.id, '0:1', adjusted_x, adjusted_y, 0, 1, 0, 0, 0,
                              f'Actor{damage_number.id}', '0:30059', 0, 0, 0)
        await p.room.send_tag('O_SPRITE', damage_number.id, '0:100067', damage)
        await p.room.send_tag('O_SPRITEANIM', damage_number.id, damage, damage + 4, 0, 'play_once', 800)

        await asyncio.sleep(0.5)
        await p.room.send_tag('O_GONE', tile_particle.id)
        await p.room.send_tag('O_GONE', damage_number.id)

        await self.animation_manager.play_animation(enemy,
                                                    enemy.owner.HitAnimation.value, 'play_once',
                                                    enemy.owner.HitAnimationDuration.value)
        await asyncio.sleep(enemy.owner.HitAnimationDuration.value * 0.001)
        await self.animation_manager.play_animation(enemy,
                                                    enemy.owner.IdleAnimation.value, 'loop',
                                                    enemy.owner.IdleAnimationDuration.value)
        await self.sound_manager.play_sound(enemy.owner.HitAnimationSound.value)

        hpbar = self.object_manager.enemy_hpbars[self.enemies.index(enemy)]
        enemy.damage += damage

        hp_percentage = round((enemy.damage * 100) / enemy.owner.HealthPoints.value)
        healthbar = round((hp_percentage * 59) / 100)
        await self.room.send_tag('O_SPRITEANIM', hpbar.id, healthbar - damage, healthbar, 0, 'play_once', 500)

        if enemy.damage >= enemy.owner.HealthPoints.value:
            await self.enemy_manager.enemy_death(enemy, hpbar)
