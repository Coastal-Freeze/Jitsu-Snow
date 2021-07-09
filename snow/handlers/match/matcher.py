import asyncio

from snow.constants import URLConstants
from snow.crypto import Crypto


class SnowMatchMaking:

    def __init__(self, server):
        self.server = server

        self._penguins = {'fire': [], 'water': [], 'snow': []}

    async def start(self):
        while True:
            await self.match_queue()
            await asyncio.sleep(1)  # blocks whole thing allow other coroutines to finish

    async def match_queue(self):
        while all([len(players) > 0 for players in self._penguins.values()]):
            match_players = [self._penguins['fire'].pop(0), self._penguins['water'].pop(0),
                             self._penguins['snow'].pop(0)]
            element_ids = [1, 2, 4]
            session_id = Crypto.generate_random_key()
            for i, penguin in enumerate(match_players):

                penguin.session_id = session_id
                penguin.element_id = element_ids[i]
                # await penguin.server.redis.set(penguin.login_key, json.dumps(data))
                await penguin.send_tag('W_PLACELIST', '0:10001', 'snow_1', '3 player sex scenario', 1, 9, 5, 0, 1, 8, 0)

                await penguin.send_json(action='jsonPayload',
                                        jsonPayload={'1': match_players[0].safe_name, '2': match_players[1].safe_name,
                                                     '4': match_players[2].safe_name},
                                        targetWindow=f'{match_players[0].media_url}minigames/cjsnow/en_US/deploy/swf'
                                                     f'/ui/windows/cardjitsu_snowplayerselect.swf',
                                        triggerName='matchFound', type='immediateAction')
                #penguin.event_num = 101
                await penguin.send_tag('W_PLACE', '0:10001', 8, 1)
                await penguin.send_tag('P_LOCKSCROLL', 1, 0, 0, 573321786)
                await penguin.send_tag('P_HEIGHTMAPSCALE', 0.078125, 128)
                await penguin.send_tag('UI_BGSPRITE', '0:-1', 0, '1.000000', '1.000000')

    def add_penguin(self, p):
        self._penguins[p.tile.Element.value].append(p)

    def remove_penguin(self, p):
        self._penguins[p.tile.Element.value].remove(p)
