import asyncio
import random
from dataclasses import dataclass

from houdini import handlers
from houdini.constants import BonusRoundType, FireNinja, WaterNinja, SnowNinja, TipType, URLConstants
from houdini.handlers import TagPacket, FrameworkPacket
from houdini.manager.animationmanager import AnimationManager
from houdini.manager.enemymanager import EnemyManager
from houdini.manager.objectmanager import ObjectManager
from houdini.manager.roundmanager import RoundManager
from houdini.manager.soundmanager import SoundManager


@dataclass
class Object:
    id: int
    name: str
    art_index: str
    template_id: str
    x: float
    y: float
    owner: 'typing.Any'


class SnowBattle:

    def __init__(self, server):
        self.server = server

        self.map = []
        self.player_objs = []
        self.obstacles = []

        self.penguins = []

        self.logic = None
        self.round = 1
        self.bonus_criteria = None
        self.stamp_group = 60

        self.tick = 9
        self.timer = None
        self.object_manager = ObjectManager(self)
        self.enemy_manager = EnemyManager(self)
        self.round_manager = RoundManager(self)
        self.sound_manager = SoundManager(self)
        self.animation_manager = AnimationManager(self)
        self.object_id = 14
        self.sound_id = 6
        self.animation_id = 10

        self.map_width = 9
        self.map_height = 5

        self.generate_map()
        self.generate_obstacles()
        self.generate_player_objects()
        self.randomize_bonus_criteria()

        self.object_id = 75  # account for the spawn

    def generate_map(self):
        for column in range(self.map_width):
            self.map.append([])
            curr_x = 0.5 + column
            for row in range(self.map_height):
                curr_y = 0.9998 + row
                self.map[column].append(
                    Object(id=self.object_id, name=f'Actor{self.object_id}', art_index='0:1', template_id='0:30020',
                           x=curr_x, y=curr_y, owner=None))
                self.object_id += 1

    def generate_player_objects(self):
        y_spawn = [1.0004, 5.0004, 3.0004]
        ninjas = [FireNinja, WaterNinja, SnowNinja]
        random.shuffle(ninjas)
        for player in ninjas:
            y_val = y_spawn.pop(0)
            self.player_objs.append(
                Object(id=self.object_id, name=f'Actor{self.object_id}', art_index='0:1', template_id='0:30040', x=0.5,
                       y=y_val, owner=player))
            self.map[0][int(y_val - 1.0004)].owner = self.player_objs[-1]
            self.object_id += 1

            # player.snow_ninja.y = int(y_val - 1.0004)

    def generate_obstacles(self):
        for x, y in ((2.5, 1), (6.5, 1), (2.5, 5), (6.5, 5)):
            self.obstacles.append(
                Object(id=self.object_id, name=f'Actor{self.object_id}', art_index='0:100394', template_id='0:100145',
                       x=x, y=y, owner=None))
            self.map[int(x - 0.5)][y - 1].owner = self.obstacles[-1]
            self.object_id += 1

    def randomize_bonus_criteria(self):
        self.bonus_criteria = random.choice([BonusRoundType.NO_NINJAS_DOWN,
                                             BonusRoundType.FULL_HEALTH])  # BonusRoundType.BEAT_THE_CLOCK, BonusRoundType.FULL_HEALTH])

    def get_tile_by_id(self, id):
        try:
            adjusted_id = id - 14
            return self.map[adjusted_id // self.map_height][adjusted_id % self.map_height]
        except:
            return None

    def is_ready(self, ready_type='ready'):
        return all(map(lambda p: getattr(p, ready_type), self.penguins))

    def clear_ready(self):
        for penguin in self.penguins:
            penguin.ready = False

    async def start_tick(self):
        self.timer = asyncio.create_task(self.tick_callback())

    async def tick_callback(self):
        try:
            await asyncio.sleep(2)  # catch up
            self.tick = 9
            while True:
                tick_json = {'action': 'jsonPayload', 'jsonPayload': {'tick': self.tick},
                             'targetWindow': f'{self.penguins[0].server.config.media}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowtimer.swf',
                             'triggerName': 'update', 'type': 'immediateAction'}
                await self.send_json(tick_json)
                await asyncio.sleep(1)
                self.tick -= 1

                if self.tick < 0:
                    await self.expire_timer()
                    break
        except asyncio.CancelledError:
            pass

    async def expire_timer(self):
        transition_json = {'action': 'jsonPayload', 'jsonPayload': [None],
                           'targetWindow': f'{self.penguins[0].server.config.media}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowtimer.swf',
                           'triggerName': 'skipToTransitionOut', 'type': 'immediateAction'}

        await self.send_json(transition_json)
        await self.remove_available_tiles()
        await self.remove_movement_plans()

        disable_cards_json = {'action': 'jsonPayload', 'jsonPayload': [None],
                              'targetWindow': f'{self.penguins[0].server.config.media}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowtimer.swf',
                              'triggerName': 'disableCards', 'type': 'immediateAction'}
        disable_confirm_json = {'action': 'jsonPayload', 'jsonPayload': [None],
                                'targetWindow': f'{self.penguins[0].server.config.media}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowtimer.swf',
                                'triggerName': 'disableConfirm', 'type': 'immediateAction'}
        await self.send_json(disable_cards_json)
        await self.send_json(disable_confirm_json)

        await self.send_tag('S_LOADSPRITE', '0:100324')
        await self.send_tag('S_LOADSPRITE', '0:100342')
        await self.send_tag('S_LOADSPRITE', '0:100364')
        await self.increase_stamina()
        await self.move_action()

    async def move_action(self):
        for penguin in self.penguins:
            if penguin.snow_ninja.last_object is not None:
                await self.send_tag('O_ANIM', penguin.snow_ninja.object_id, penguin.ninja.MoveAnimation.value,
                                    'play_once', penguin.ninja.MoveAnimationDuration.value, 1, 0, 9, self.animation_id,
                                    0, 0)
                self.animation_id += 1
                await self.send_tag('O_ANIM', penguin.snow_ninja.object_id, penguin.ninja.IdleAnimation.value, 'loop',
                                    penguin.ninja.IdleAnimationDuration.value, 1, 1, 9, self.animation_id, 0, 0)
                await self.send_tag('FX_PLAYSOUND', '0:1840017', self.sound_id, 0, 100, -1, 0, -1)
                self.sound_id += 1

                self.map[penguin.snow_ninja.x][penguin.snow_ninja.y].owner = None
                new_tile = penguin.snow_ninja.last_object
                penguin.snow_ninja.x = int(new_tile.x)
                penguin.snow_ninja.y = int(new_tile.y)
                self.map[penguin.snow_ninja.x][penguin.snow_ninja.y].owner = penguin.ninja

                await self.send_tag('O_SLIDE', penguin.snow_ninja.object_id, penguin.snow_ninja.x + 0.5,
                                    penguin.snow_ninja.y + 1, 128, penguin.ninja.MoveAnimationDuration.value)
                await self.send_tag('O_SLIDE', penguin.snow_ninja.current_object.id, penguin.snow_ninja.x + 0.5,
                                    penguin.snow_ninja.y + 1.0004, 128, penguin.ninja.MoveAnimationDuration.value)

    async def show_targets(self):
        await self.send_tag('O_HERE', '86', '0:1', '6.5', '3.01', '0', '1', '0', '0', '0', 'Actor86', '0:30033', '0',
                            '0', '0')
        await self.send_tag('O_HERE', '87', '0:1', '7.5', '1.01', '0', '1', '0', '0', '0', 'Actor87', '0:30033', '0',
                            '0', '0')
        await self.send_tag('O_HERE', '88', '0:1', '6.5', '4.01', '0', '1', '0', '0', '0', 'Actor88', '0:30033', '0',
                            '0', '0')
        await self.send_tag('O_SPRITE', '86', '0:100040', '1')
        await self.send_tag('O_SPRITEANIM', '86', '1', '6', '1', 'play_once', '402')
        await self.send_tag('FX_PLAYSOUND', '0:1840039', '86', '0', '100', '-1', '0', '-1')
        await self.send_tag('O_SPRITE', '87', '0:100040', '1')
        await self.send_tag('O_SPRITEANIM', '87', '1', '6', '1', 'play_once', '402')
        await self.send_tag('FX_PLAYSOUND', '0:1840039', '87', '0', '100', '-1', '0', '-1')
        await self.send_tag('O_SPRITE', '88', '0:100040', '1')
        await self.send_tag('O_SPRITEANIM', '88', '1', '6', '1', 'play_once', '402')
        await self.send_tag('FX_PLAYSOUND', '0:1840039', '88', '0', '100', '-1', '0', '-1')
        await self.send_tag('O_SPRITE', '86', '0:100041', '1')
        await self.send_tag('O_SPRITEANIM', '86', '1', '60', '0', 'loop', '4020')
        await self.send_tag('O_SPRITE', '87', '0:100041', '1')
        await self.send_tag('O_SPRITEANIM', '87', '1', '60', '0', 'loop', '4020')
        await self.send_tag('O_SPRITE', '88', '0:100041', '1')
        await self.send_tag('O_SPRITEANIM', '88', '1', '60', '0', 'loop', '4020')

    async def increase_stamina(self):
        for penguin in self.penguins:
            if penguin.snow_ninja.last_object is not None:
                await penguin.add_stamina(2)

    async def spawn_enemies(self):
        await self.send_tag('O_HERE', '66', '0:1', '7.5', '4', '0', '1', '0', '0', '0', 'Actor66', '0:30012', '0', '1',
                            '0')
        # TILE_CHANGE: X | Y | TILE TYPE
        await self.send_tag('P_TILECHANGE', '7', '3', '8')

        # await self.send_tag('O_HERE', '67', '0:1', '7.5', '4.0004', '0', '1', '0', '0', '0', 'Actor67', '0:30040', '0', '1', '0')
        await self.send_tag('O_SPRITEANIM', '67', '1', '1', '0', 'play_once', '0')
        await self.send_tag('O_SPRITE', '67', '0:100395', '1', '')
        await self.send_tag('O_ANIM', '66', '0:100379', 'play_once', '700', '1', '0', '66', '4', '0', '0')
        await self.send_tag('FX_PLAYSOUND', '0:1840009', '2', '0', '100', '-1', '0', '-1')
        await self.send_tag('O_ANIM', '66', '0:100305', 'loop', '1675', '1', '1', '66', '5', '0', '0')

        await self.send_tag('O_HERE', '68', '0:1', '8.5', '3', '0', '1', '0', '0', '0', 'Actor68', '0:30012', '0', '1',
                            '0')
        await self.send_tag('P_TILECHANGE', '8', '2', '8')

        # await self.send_tag('O_HERE', '69', '0:1', '8.5', '3.0004', '0', '1', '0', '0', '0', 'Actor69', '0:30040', '0', '1', '0')
        await self.send_tag('O_SPRITEANIM', '69', '1', '1', '0', 'play_once', '0')
        await self.send_tag('O_SPRITE', '69', '0:100395', '1', '')
        await self.send_tag('O_ANIM', '68', '0:100379', 'play_once', '700', '1', '0', '68', '6', '0', '0')
        await self.send_tag('FX_PLAYSOUND', '0:1840009', '3', '0', '100', '-1', '0', '-1')
        await self.send_tag('O_ANIM', '68', '0:100305', 'loop', '1675', '1', '1', '68', '7', '0', '0')

        # 0 :100305: sly , 0:100297:tank, 0:100311: scrap

    async def add_penguin(self, p):
        self.penguins.append(p)
        p.room = self

    async def remove_penguin(self, p):
        self.penguins.remove(p)
        p.room = None

    async def show_ui(self):
        for penguin in self.penguins:
            await penguin.show_ui()

    async def show_timer(self):
        for penguin in self.penguins:
            await penguin.show_timer()

    async def show_round_notice(self):
        for penguin in self.penguins:
            await penguin.show_round_notice(self.round, self.bonus_criteria.value)

    async def show_tip(self, tip_name):
        for penguin in self.penguins:
            await penguin.show_tip(tip_name)

    async def send_tag(self, *data):
        for penguin in self.penguins:
            await penguin.send_tag(*data)

    async def send_json(self, **data):
        for penguin in self.penguins:
            await penguin.send_json(**data)

    async def remove_movement_plans(self):
        await self.send_tag('O_GONE', 70)
        for player in self.penguins:
            if player.snow_ninja.last_object is not None:
                await self.send_tag('O_GONE', player.snow_ninja.last_object.id)
                player.snow_ninja.last_object = None

    async def remove_available_tiles(self):
        for player in self.penguins:
            for tile_id in player.snow_ninja.modified_object:
                await player.send_tag('O_SPRITE', tile_id, '0:1', 1)

    async def show_available_tiles(self):
        for player in self.penguins:
            player_range = player.ninja.Move.value
            player.snow_ninja.modified_object = []

            i, delta = -1, 1
            for x in range(-player_range + player.snow_ninja.x, player_range + player.snow_ninja.x + 1):
                i += delta
                if i == player_range:
                    delta = -1

                if x < 0 or x >= self.map_width:
                    continue

                for y in range(-i + player.snow_ninja.y, i + player.snow_ninja.y + 1):
                    if y < 0 or y >= self.map_height or x < 0 or x >= self.map_width:
                        continue
                    await player.send_tag('O_SPRITE', self.map[x][y].id,
                                          '0:100063' if self.map[x][y].owner is None else '0:100270', '1')
                    player.snow_ninja.modified_object.append(self.map[x][y].id)
            await player.send_tag('O_HERE', '70', '0:100300', '0', '0', '0', '1', '0', '0', '0', 'Actor70', '0:30038',
                                  '0', '0', '0')


@handlers.handler(FrameworkPacket('roomToRoomMinTime'))
async def handle_room_change(p, **kwargs):
    await p.send_tag('O_SPRITE', '10', '0:100380', '0', '')  # 6740003 - craig valley bg / 0:6740006 - forest
    await p.send_tag('O_SPRITE', '11', '0:1', '0', '')  # 6740004 - foreground / 0:6740007
    await p.room.object_manager.send_map(p)
    await p.room.send_json(action='closeCjsnowRoomToRoom', targetWindow='cardjitsu_snowplayerselect.swf',
                           type='immediateAction')
    await p.room.send_tag('FX_PLAYSOUND', '0:1840002', 1, 1, 75, -1, 0, -1)
    await p.room.round_manager.start_round()


@handlers.handler(FrameworkPacket('roomToRoomScreenClosed'))
async def handle_successful_close(p, **kwargs):
    p.screen_closed = True
    if p.room.is_ready('screen_closed'):
        await p.room.round_manager.show_round_notice()


@handlers.handler(FrameworkPacket('windowClosed'))
async def handle_window_closed(p, windowId=None, **data):
    if windowId == 'cardjitsu_snowrounds.swf':
        p.round_closed = True
        if p.room.is_ready('round_closed'):
            await p.room.round_manager.start_round()


@handlers.handler(FrameworkPacket('windowReady'))
async def handle_ready_window(p, windowId=None, **data):
    if windowId == 'cardjitsu_snowtimer.swf':
        p.timer_ready = True
        if p.room.is_ready('timer_ready'):
            await p.room.object_manager.show_moveable_tiles()

            await p.room.round_manager.begin_timer()
            if p.tip_mode:
                await p.room.show_tip(TipType.MOVE.value)


@handlers.handler(FrameworkPacket('quit'))
async def handle_quit(p, **data):
    await p.room.remove_penguin(p)

    await p.send_json(action='loadWindow', assetPath='', initializationPayload=[None], layerName='toolLayer', \
                      loadDescription='', type='playAction',
                      windowUrl=p.media_url + URLConstants.ExternalInterface.value, \
                      xPercent=0, yPercent=0)
    # await p.close()


@handlers.handler(TagPacket('use'))
async def handle_click_tile(p, tile_id: int, a: float, b: float, c: float, d: float):
    if tile_id <= p.room.object_manager.map[-1][-1].id:  # Is it a tile?
        tile = p.room.object_manager.get_tile_by_id(tile_id)

        if tile is not None and tile.id == tile_id:
            for sprite in p.server.move_sprites:
                await p.room.send_tag('S_LOADSPRITE', f'0:{sprite}')

            await p.room.object_manager.plan_movement(p, tile)
    elif p.room.object_manager.get_enemy_by_id(tile_id) is not None:
        await p.room.object_manager.select_enemy(p, tile_id)


@handlers.handler(FrameworkPacket('ShowMemberCardInfoTip'))
async def handle_member_revive_tip(p, **data):
    await p.show_tip(TipType.BONUS_REVIVE.value, bypass_tipmode=True)
