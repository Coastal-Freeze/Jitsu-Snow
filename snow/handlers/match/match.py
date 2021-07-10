from snow.events import event, FrameworkPacket, player_attribute
from .matcher import SnowMatchMaking
import asyncio

from ...constants import FireNinja, WaterNinja, SnowNinja


@event.on("boot")
async def match_load(server):
    server.attributes['snow_match_making'] = SnowMatchMaking(server)
    asyncio.create_task(server.attributes['snow_match_making'].start())


@event.on(FrameworkPacket('mmElementSelected'))
async def handle_select_element(p, tipMode=False, element=None, **data):
    p.tip_mode = tipMode
    p.tile = FireNinja
    if element == 'water':
        p.tile = WaterNinja
    elif element == 'snow':
        p.tile = SnowNinja

    p.server.attributes['snow_match_making'].add_penguin(p)


@event.on(FrameworkPacket('mmCancel'))
async def handle_cancel_matchmaking(p, **data):
    p.server.attributes['snow_match_making'].remove_penguin(p)


@event.on(FrameworkPacket('payloadBILogAction'))
async def handle_payload_action(p, action, **data):
    # TODO: handle tipmode and muted soundss
    if action == 'funnel_prepare_to_battle_4':
        await asyncio.sleep(5)  # Prepare to battle animation
        await p.send_json(type='playAction', action='closeWindow',
                          targetWindow=p.media_url + URLConstants.player_selection.value)
