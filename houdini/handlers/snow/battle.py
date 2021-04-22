import asyncio
import random
from dataclasses import dataclass

from houdini import handlers
from houdini.constants import BonusRoundType, FireNinja, WaterNinja, SnowNinja, TipType, URLConstants, PenguinObject
from houdini.handlers import TagPacket, FrameworkPacket
from houdini.manager.animationmanager import AnimationManager
from houdini.manager.enemymanager import EnemyManager
from houdini.manager.objectmanager import ObjectManager
from houdini.manager.roundmanager import RoundManager
from houdini.manager.soundmanager import SoundManager
from houdini.manager.playermanager import PlayerManager


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
        self.game = False
        self.map = []
        self.penguins = []
        self.object_manager = ObjectManager(self)
        
        self.round_manager = RoundManager(self)
        self.sound_manager = SoundManager(self)
        self.animation_manager = AnimationManager(self)
        self.enemy_manager = EnemyManager(self)
        self.player_manager = PlayerManager(self)
        

    def is_ready(self, ready_type='ready'):
        ready = all(map(lambda ninja: ninja.snow_ninja.ready_object[ready_type], self.penguins))
        return ready

    def clear_ready(self):
        for penguin in self.penguins:
            penguin.snow_ninja.ready_object['ready'] = False

    async def increase_stamina(self):
        for penguin in self.penguins:
            if penguin.snow_ninja.last_object is not None:
                await penguin.add_stamina(2)

    async def add_penguin(self, p):
        self.penguins.append(p)
        p.room = self

    async def remove_penguin(self, p):
        self.penguins.remove(p)
        p.room = None

    async def send_tag(self, *tag, f=None):
        for player in filter(f, self.penguins):
            await player.send_tag(*tag)

    async def show_tip(self, tip_name):
        for penguin in self.penguins:
            await penguin.show_tip(tip_name)

    async def send_json(self, **json):
        for player in self.penguins:
            await player.send_json(**json)


@handlers.handler(TagPacket('use'))
async def handle_click_tile(p, tile_id: int, a: float, b: float, c: float, d: float):

    #p.logger.error('heal target: ' + p.room.object_manager.get_heal_target_by_id(p, tile_id))
    if tile_id <= p.room.object_manager.map[-1][-1].id:  # Is it a tile?
        tile = p.room.object_manager.get_tile_by_id(tile_id)

        if tile is not None and tile.id == tile_id:
            for sprite in p.server.move_sprites:
                await p.room.send_tag('S_LOADSPRITE', f'0:{sprite}')

            await p.room.object_manager.plan_movement(p, tile)
    elif p.room.object_manager.get_enemy_by_id(tile_id) is not None:
        await p.room.object_manager.select_enemy(p, tile_id)
    elif p.room.object_manager.get_heal_target_by_id(p, tile_id) is not None:
        await p.room.object_manager.heal_penguin(p, tile_id)


@handlers.handler(FrameworkPacket('confirmClicked'))
async def handle_show_confirm(p, **data):
    await p.room.object_manager.check_mark(p)


@handlers.handler(FrameworkPacket('ShowMemberCardInfoTip'))
async def handle_member_revive_tip(p, **data):
    await p.show_tip(TipType.BONUS_REVIVE.value, bypass_tipmode=True)
