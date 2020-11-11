import asyncio
import random

from houdini.constants import BonusRoundType, RoundState
from houdini.constants import OccupiedEnemySpawnTile
from houdini.constants import URLConstants


class RoundManager():

    def __init__(self, room):
        self.room = room

        self.round = 0
        self.state = RoundState.NEW_ROUND
        self.bonus_criteria = None
        self.bonus_time = None
    
        self.ticks = None
        self.callback = None

        self.randomize_bonus_criteria()

    def randomize_bonus_criteria(self):
        self.bonus_criteria = random.choice([BonusRoundType.NO_NINJAS_DOWN, BonusRoundType.FULL_HEALTH]) #BonusRoundType.BEAT_THE_CLOCK, BonusRoundType.FULL_HEALTH])

    async def start_round(self):
        self.state = RoundState.NINJA_TURN

        self.room.enemy_manager.generate_enemies()
        await self.spawn_enemies()
        
        await self.load_timer()
        await self.load_ui()

    async def spawn_enemies(self):
        for i, enemy_obj in enumerate(self.room.object_manager.enemies):
            enemy_hp_obj = self.room.object_manager.enemy_hpbars[i]

            adjusted_x = round(enemy_obj.x + enemy_obj.parent.XCoordinateOffset.value, enemy_obj.parent.XCoordinateDecimals.value)
            adjusted_y = round(enemy_obj.y + enemy_obj.parent.YCoordinateOffset.value, enemy_obj.parent.YCoordinateDecimals.value)

            await self.room.send_tag('O_HERE', enemy_obj.id, enemy_obj.art_index, adjusted_x, adjusted_y, 0, 1, 0, 0, 0, \
                                     enemy_obj.name, enemy_obj.template_id, 0, 1, 0)
            await self.room.send_tag('P_TILECHANGE', enemy_obj.x, enemy_obj.y, OccupiedEnemySpawnTile.TileUrl.value)
                    
            adjusted_x = round(enemy_hp_obj.x + enemy_hp_obj.parent.XCoordinateOffset.value, \
                                 enemy_hp_obj.parent.XCoordinateDecimals.value)
            adjusted_y = round(enemy_hp_obj.y + enemy_hp_obj.parent.YCoordinateOffset.value, \
                                 enemy_hp_obj.parent.YCoordinateDecimals.value)

            await self.room.send_tag('O_HERE', enemy_hp_obj.id, enemy_hp_obj.art_index, adjusted_x, adjusted_y, 0, 1, 0, \
                                    0, 0, enemy_hp_obj.name, enemy_hp_obj.template_id, 0, 1, 0)
            await self.room.send_tag('O_SPRITEANIM', enemy_hp_obj.id, 1, 1, 0, 'play_once', 0)
            await self.room.send_tag('O_SPRITE', enemy_hp_obj.id, '0:100395', 1, '')

            await self.room.send_tag('O_ANIM', enemy_obj.id, '0:100379', 'play_once', 700, 1, 0, enemy_obj.id, i + 10, 0, 0)
            await self.room.sound_manager.play_sound('0:1840009')
            await self.room.send_tag('O_ANIM', enemy_obj.id, enemy_obj.occupant.IdleAnimation.value, 'loop', \
                                        enemy_obj.occupant.IdleAnimationDuration.value, 1, 1, enemy_obj.id, i + 11, 0, 0)
        # 0 :100305: sly , 0:100297:tank, 0:100311: scrap

    async def show_round_notice(self):
        for penguin in self.room.penguins:
            await penguin.show_round_notice(self.round, self.bonus_criteria.value)

    async def increase_movement_stamina(self):
        for penguin in self.room.penguins:
            if penguin.game_data.last_object is not None:
                await penguin.add_stamina(2)

    async def begin_timer(self):
        await self.show_timer()
        self.callback = asyncio.create_task(self.timer_callback())
    
    async def timer_callback(self):
        try:
            await asyncio.sleep(2) # catch up
            self.ticks = 9
            while True:
                await self.room.send_json(action='jsonPayload', jsonPayload={'tick': self.ticks}, \
                                targetWindow=self.room.penguins[0].media_url + URLConstants.SnowTimer.value, triggerName='update', type='immediateAction')
                
                await asyncio.sleep(1)
                self.ticks -= 1

                if self.ticks < 0:
                    await self.expire_timer()
                    break
                
        except asyncio.CancelledError:
            pass
    
    async def expire_timer(self):
        await self.hide_timer()

        await self.room.send_tag('S_LOADSPRITE', '0:100324')
        await self.room.send_tag('S_LOADSPRITE', '0:100342')
        await self.room.send_tag('S_LOADSPRITE', '0:100364')
        await self.increase_movement_stamina()
        await self.room.object_manager.do_move_action()
        #await self.room.send_tag('O_ANIM', 12, '0:100362', 'play_once', 1330, 1, 0, 12, 28, 0, 0)
        #await self.room.send_tag('O_ANIM', 12, '0:100361', 'loop', 1100, 1, 1, 12, 29, 0, 0)

        # Need to implement battles

        await asyncio.sleep(3)

        await self.do_user_battles()

        await asyncio.sleep(3)

        '''
        await self.room.send_tag('O_HERE', '94', '0:1', '5.5', '3.25', '0', '1', '0', '0', '0', 'Actor94', '0:30059', '0', '0', '0')
        await self.room.send_tag('O_SLIDE', '94', '7.5', '2.25', '128', '200')
        await self.room.send_tag('O_SPRITE', '94', '0:100372', '1', '')
        await self.room.send_tag('O_HERE', '95', '0:1', '7.5', '0.9998', '0', '1', '0', '0', '0', 'Actor95', '0:30059', '0', '0', '0')
        await self.room.send_tag('O_SPRITE', '95', '0:100064', '0', '')
        await self.room.send_tag('O_SPRITEANIM', '76', '1', '6', '0', 'play_once', '500')
                                                             ^ frame
        await self.room.send_tag('FX_PLAYSOUND', '0:1840003', '30', '0', '100', '-1', '0', '-1')
        await self.room.send_tag('O_HERE', '96', '0:1', '7.5', '1.0002', '0', '1', '0', '0', '0', 'Actor96', '0:30059', '0', '0', '0')
        await self.room.send_tag('O_SPRITE', '96', '0:100067', '16', '')
        await self.room.send_tag('O_SPRITEANIM', '96', '16', '20', '0', 'play_once', '1200')
        await self.room.send_tag('O_ANIM', '75', '0:100302', 'play_once', '1200', '1', '0', '75', '30', '0', '0')
        await self.room.send_tag('O_ANIM', '75', '0:100297', 'loop', '1100', '1', '1', '75', '31', '0', '0')
        await self.room.send_tag('FX_PLAYSOUND', '0:1840008', '31', '0', '100', '-1', '0', '-1')

        return'''

        await self.room.enemy_manager.do_enemy_turn()
        await asyncio.sleep(3) # need to show tiles too
        await self.room.object_manager.show_moveable_tiles()
        await self.begin_timer()
    
    async def do_user_battles(self):
        print('unimplemented')
        for penguin in self.room.penguins:
            if penguin.snow_ninja.current_target is not None:
                await self.room.animation_manager.play_animation(penguin.snow_ninja.current_object, penguin.ninja.AttackAnimation.value, \
                                                        'play_once', penguin.ninja.AttackAnimationDuration.value)
                await self.room.animation_manager.play_animation(penguin.snow_ninja.current_object, penguin.ninja.IdleAnimation.value, \
                                                        'loop', penguin.ninja.IdleAnimationDuration.value)
                await self.room.sound_manager.play_sound(penguin.ninja.AttackAnimationSound.value)
                asyncio.create_task(penguin, penguin.snow_ninja.current_target, penguin.ninja.AttackAnimationDuration.value * 0.001)
                penguin.snow_ninja.current_target = None
    
    async def finish_battle(self, p, enemy, delay):
        print('unimplemented')

    async def show_timer(self):
        await self.room.send_json(action='jsonPayload', jsonPayload=[None], targetWindow=self.room.penguins[0].media_url + URLConstants.SnowTimer.value,\
                                    triggerName='enableCards', type='immediateAction')
        await self.room.send_json(action='jsonPayload', jsonPayload={'isEnabled': 1}, targetWindow=self.room.penguins[0].media_url + URLConstants.SnowTimer.value, \
                                    triggerName='enableConfirm', type='immediateAction')
        await self.room.send_json(action='jsonPayload', jsonPayload=[None], targetWindow=self.room.penguins[0].media_url + URLConstants.SnowTimer.value, \
                                    triggerName='Timer_Start', type='immediateAction')
    
    async def hide_timer(self):
        await self.room.send_json(action='jsonPayload', jsonPayload=[None], targetWindow=self.room.penguins[0].media_url + URLConstants.SnowTimer.value, \
                                    triggerName='skipToTransitionOut', type='immediateAction')
                
        await self.room.object_manager.remove_movement_plans()

        await self.room.send_json(action='jsonPayload', jsonPayload=[None], targetWindow=self.room.penguins[0].media_url + URLConstants.SnowTimer.value, \
                                    triggerName='disableCards', type='immediateAction')
        await self.room.send_json(action='jsonPayload', jsonPayload=[None], targetWindow=self.room.penguins[0].media_url + URLConstants.SnowTimer.value, \
                                    triggerName='disableConfirm', type='immediateAction')

    async def load_ui(self):
        for penguin in self.room.penguins:
            await penguin.load_ui()
    
    async def load_timer(self):
        for penguin in self.room.penguins:
            await penguin.load_timer()
    