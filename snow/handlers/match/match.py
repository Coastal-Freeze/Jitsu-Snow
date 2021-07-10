from snow.events import event, FrameworkPacket, player_attribute
from .matcher import SnowMatchMaking
import asyncio

from ...constants import FireNinja, WaterNinja, SnowNinja, URLConstants


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
        await p.send_tag('O_GONE', 4)
        await p.send_tag('W_INPUT', 'use', '4375706:1', 2, 3, 0, 'use')
        await p.send_tag('P_MAPBLOCK', 't', 1, 1,
                         'iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=')
        await p.send_tag('P_MAPBLOCK', 'h', 1, 1,
                         'iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=')
        await p.send_tag('P_ZOOMLIMIT', '-1.000000', '-1.000000')
        await p.send_tag('P_RENDERFLAGS', 0, 48)
        await p.send_tag('P_SIZE', 9, 5)
        await p.send_tag('P_VIEW', 5)
        await p.send_tag('P_START', 4.5, 2.5, 0)
        await p.send_tag('P_LOCKVIEW', 0)
        await p.send_tag('P_TILESIZE', 100)
        await p.send_tag('P_ELEVSCALE', '0.031250')
        await p.send_tag('P_RELIEF', 1)
        await p.send_tag('P_LOCKSCROLL', 1, 0, 0, 573321786)
        await p.send_tag('P_HEIGHTMAPSCALE', 0.078125, 128)
        await p.send_tag('P_HEIGHTMAPDIVISIONS', 1)
        await p.send_tag('P_CAMERA3D', '0.000000', '0.000000', '0.000000', '0.000000', '0.000000', '0.000000', '0.000000',
                         '0.000000', 0, '0.000000', '0.000000', '0.000000', '0.000000', '0.000000', '0.000000',
                         '864397819904.000000', '0.000000', 0, 0)
        await p.send_tag('UI_BGCOLOR', 34, 164, 243)
        await p.send_tag('P_DRAG', 0)
        await p.send_tag('P_CAMLIMITS', 0, 0, 0, 0)
        await p.send_tag('P_LOCKRENDERSIZE', 0, 1024, 768)
        await p.send_tag('P_LOCKOBJECTS', 0)
        await p.send_tag('UI_BGSPRITE', '0:-1', 0, '1.000000', '1.000000')
        
        for tile in p.server.tiles:
            await p.send_tag('P_TILE', tile.tile_url.value, '', 0, 0, 1, tile.sprite_index.value, tile.tile_name.value, 0, 0,
                             0, tile.tile_collection.value)
        await p.send_tag('P_PHYSICS', 0, 0, 0, 0, 0, 0, 0, 1)
        await p.send_tag('P_ASSETSCOMPLETE', 0, 0)
        for sprite in p.server.default_sprites:
            await p.send_tag('S_LOADSPRITE', f'0:{sprite}')

        await p.send_tag('O_HERE', 12, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)
       
        await p.send_tag('O_HERE', 4, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)

        # idk about these
        await p.send_tag('O_HERE', 9, '0:1', 10.7667, 5.92222, 0, 1, 0, 0, 0, 'Actor5', '0:30021', 0, 0, 0)
        await p.send_tag('O_HERE', 10, '0:1', 4.48869, -1.11106, 0, 1, 0, 0, 0, 'Actor6', '0:10002', 0, 0, 0)
        await p.send_tag('O_HERE', 11, '0:1', 4.5, 6.1, 0, 1, 0, 0, 0, 'Actor7', '0:6740002', 0, 0, 0)
        await p.send_tag('O_PLAYER', 12, '')  # prob change it ot the number
        await p.send_tag('P_CAMERA', 4.48438, 2.48438, 0, 0, 1)
        await p.send_tag('P_ZOOM', '1.000000')
        await p.send_tag('P_LOCKZOOM', 1)
        await p.send_tag('P_LOCKCAMERA', 1)