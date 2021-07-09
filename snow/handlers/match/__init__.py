from snow.events import event, FrameworkPacket, player_attribute
from .matcher import SnowMatchMaking
import asyncio

from ...constants import FireNinja, WaterNinja, SnowNinja


@event.on("boot")
async def match_load(server):
    server.attrib['snow_match_making'] = SnowMatchMaking(server)
    asyncio.create_task(server.attrib['snow_match_making'].start())


@event.on(FrameworkPacket('mmElementSelected'))
@player_attribute('login_key')
async def handle_select_element(p, tipMode=False, element=None, **data):
    p.snow_ninja.tip_mode = tipMode
    p.snow_ninja.tile = FireNinja

    if element == 'water':
        p.snow_ninja.tile = WaterNinja
    elif element == 'snow':
        p.snow_ninja.tile = SnowNinja

    p.server.attrib['snow_match_making'].add_penguin(p)


@event.on(FrameworkPacket('mmCancel'))
@player_attribute('login_key')
async def handle_cancel_matchmaking(p, **data):
    p.server.attrib['snow_match_making'].remove_penguin(p)
