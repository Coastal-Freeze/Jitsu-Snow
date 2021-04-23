import asyncio

from houdini import handlers
from houdini.constants import ClientType
from houdini.converters import VersionChkConverter
from houdini.data.buddy import BuddyList
from houdini.handlers import XMLPacket, TagPacket


@handlers.handler(XMLPacket('verChk'))
@handlers.allow_once
async def handle_version_check(p, version: VersionChkConverter):
    if not p.server.config.single_client_mode:
        if p.server.config.legacy_version == version:
            p.client_type = ClientType.Legacy
        elif p.server.config.vanilla_version == version:
            p.client_type = ClientType.Vanilla
    elif p.server.config.default_version == version:
        p.client_type = p.server.config.default_client

    if p.client_type is None:
        await p.send_xml({'body': {'action': 'apiKO', 'r': '0'}})
        await p.close()
    else:
        await p.send_xml({'body': {'action': 'apiOK', 'r': '0'}})


@handlers.handler(TagPacket('/place_context'), pre_login=True)
async def handle_server_context(p, world, parameters):
    parameters_parsed = parameters.split('&')
    for parameter in parameters_parsed:
        curr_param = parameter.split('=')
        if curr_param[0] == 'tipMode':
            p.tip_mode = curr_param[1].lower() == 'true'
        elif curr_param[0] == 'muted':
            p.muted = curr_param[1].lower() == 'true'
        else:
            p.media_url = curr_param[1].rstrip()


@handlers.handler(TagPacket('/version'), pre_login=True)
async def handle_snow_version_check(p):
    await p.send_tag('S_VERSION', 'FY15-20150206 (4954)r', '73971eecbd8923f695303b2cd04e5f70',
                     'Tue Feb  3 14:11:56 PST 2015',
                     '/var/lib/jenkins/jobs/BuildPlatform/workspace/metaserver_source/dimg')


@handlers.handler(XMLPacket('rndK'))
@handlers.allow_once
async def handle_random_key(p, _):
    await p.send_xml({'body': {'action': 'rndK', 'r': '-1'}, 'k': p.server.config.auth_key})


async def get_server_presence(p, pdata):
    buddy_worlds = []
    world_populations = []

    pops = await p.server.redis.hgetall('houdini.population')
    for server_id, server_population in pops.items():
        server_population = 7 if int(server_population) == p.server.config.capacity \
            else int(server_population) // (p.server.config.capacity // 6)
        server_population = server_population if not pdata.moderator else 0

        world_populations.append(f'{int(server_id)},{int(server_population)}')

        server_key = f'houdini.players.{int(server_id)}'
        if await p.server.redis.scard(server_key):
            async with p.server.db.transaction():
                buddies = BuddyList.select('buddy_id').where(BuddyList.penguin_id == pdata.id).gino.iterate()
                tr = p.server.redis.multi_exec()
                async for buddy_id, in buddies:
                    tr.sismember(server_key, buddy_id)
                online_buddies = await tr.execute()
                if any(online_buddies):
                    buddy_worlds.append(str(int(server_id)))

    return '|'.join(world_populations), '|'.join(buddy_worlds)


class SnowMatchMaking:

    def __init__(self, server):
        self.server = server

        self._penguins = {'fire': [], 'water': [], 'snow': []}

    async def start(self):
        while True:
            await self.match_queue()
            await asyncio.sleep(1)  # blocks whole thing allow other corutines to finish

    async def match_queue(self):
        while all([len(players) > 0 for players in self._penguins.values()]):
            match_players = [self._penguins['fire'].pop(0), self._penguins['water'].pop(0),
                             self._penguins['snow'].pop(0)]
            room_name = match_players[0].id
            tr = self.server.redis.multi_exec()
            element_ids = [1, 2, 4]
            for player in match_players:
                tr.set(f'cjsnow.{player.id}', room_name)
                tr.set(f'cjsnow.{player.id}.element', element_ids[match_players.index(player)])
            await tr.execute()

            for penguin in match_players:
                await penguin.send_json(action='jsonPayload',
                                        jsonPayload={'1': match_players[0].safe_name, '2': match_players[1].safe_name,
                                                     '4': match_players[2].safe_name},
                                        targetWindow=f'{match_players[0].media_url}minigames/cjsnow/en_US/deploy/swf'
                                                     f'/ui/windows/cardjitsu_snowplayerselect.swf',
                                        triggerName='matchFound', type='immediateAction')

    def add_penguin(self, p):
        self._penguins[p.snow_ninja.current_object.Element.value].append(p)

    def remove_penguin(self, p):
        self._penguins[p.snow_ninja.current_object.Element.value].remove(p)


@handlers.boot
async def match_load(server):
    if server.config.type == 'login':
        return

    server.snow_match_making = SnowMatchMaking(server)
    print(server.snow_match_making)

    asyncio.create_task(server.snow_match_making.start())
