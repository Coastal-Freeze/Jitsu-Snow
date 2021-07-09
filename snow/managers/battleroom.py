from snow.managers.animationmanager import AnimationManager
from snow.managers.enemymanager import EnemyManager
from snow.managers.objectmanager import ObjectManager
from snow.managers.playermanager import PlayerManager
from snow.managers.roundmanager import RoundManager
from snow.managers.soundmanager import SoundManager


class BattleRoom:

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
        ready = all(map(lambda p: p[ready_type], self.penguins))
        return ready

    def clear_ready(self):
        for penguin in self.penguins:
            penguin['ready'] = False

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
