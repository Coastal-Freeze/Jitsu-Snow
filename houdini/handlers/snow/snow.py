from houdini.constants import ClientType, URLConstants, WaterNinja, SnowNinja, TipType, FireNinja
from houdini.handlers import login, FrameworkPacket, TagPacket
from houdini import handlers
import asyncio


@handlers.handler(TagPacket('/set_crossworld_ui'), pre_login=True)
async def handle_cross_world(p, switch: bool):
    p.server.snow_world = switch


@handlers.handler(TagPacket('/ready'))
async def handle_penguin_ready(p):
    if p.server.snow_world:
        await snow_world_ready(p)
    else:
        await snow_login_ready(p)


async def snow_login_ready(p):
    # [W_INPUT]|use|4375706:1|2|3|0|use|
    await p.send_tag('W_INPUT', 'use', '4375706:1', 2, 3, 0, 'use')
    # input id | script id | mouse target | key mouse type | key modifier | command

    for sprite in p.server.default_sprites:
        await p.send_tag('S_LOADSPRITE', f'0:{sprite}')

    await p.send_tag('UI_CROSSWORLDSWFREF', 101, 0, 'WindowManagerSwf', 0, 0, 0, 0, 0,
                     p.media_url + URLConstants.WindowManager.value, '#')
    await p.send_tag('UI_ALIGN', 101, 0, 0, 'center', 'scale_none')

    await p.send_tag('W_PLACE', '0:0', 1, 0)
    # tile
    await p.send_tag('P_MAPBLOCK', 't', 1, 1,
                     'iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=')
    # height
    await p.send_tag('P_MAPBLOCK', 'h', 1, 1,
                     'iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=')
    await p.send_tag('P_ZOOMLIMIT', '-1.000000', '-1.000000')
    await p.send_tag('P_RENDERFLAGS', 0, 48)
    await p.send_tag('P_SIZE', 9, 5)
    await p.send_tag('P_VIEW', 5)
    await p.send_tag('P_START', 5, 2.5, 0)
    await p.send_tag('P_LOCKVIEW', 0)
    await p.send_tag('P_TILESIZE', 100)
    await p.send_tag('P_ELEVSCALE', '0.031250')
    await p.send_tag('P_RELIEF', 1)
    await p.send_tag('P_LOCKSCROLL', 1, 0, 0, 0)
    await p.send_tag('P_HEIGHTMAPSCALE', 0.5, 0)
    await p.send_tag('P_HEIGHTMAPDIVISIONS', 1)
    await p.send_tag('P_CAMERA3D', '0.000000', '0.000000', '0.000000', '0.000000', '0.000000', '0.000000', '0.000000',
                     '0.000000', 0, '0.000000', '0.000000', '0.000000', '0.000000', '0.000000', '0.000000',
                     '864397819904.000000', '0.000000', 0, 0)
    await p.send_tag('UI_BGCOLOR', 34, 164, 243)
    await p.send_tag('P_DRAG', 0)
    await p.send_tag('P_CAMLIMITS', 0, 0, 0, 0)
    await p.send_tag('P_LOCKRENDERSIZE', 0, 1024, 768)
    await p.send_tag('P_LOCKOBJECTS', 0)
    await p.send_tag('UI_BGSPRITE', '-1:-1', 0, '0.000000', '0.000000')

    await p.send_tag('P_TILE', 0, '', 0, 0, 1, '0:2', 'Empty Tile', 0, 0, 0, '0:7940006')
    await p.send_tag('P_TILE', 1, '', 0, 0, 1, '0:2', 'blankblue', 0, 0, 0, '0:7940007')
    await p.send_tag('P_TILE', 2, '', 0, 0, 1, '0:3', 'blankgreen', 0, 0, 0, '0:7940008')
    await p.send_tag('P_TILE', 3, '', 0, 0, 1, '0:4', 'blankgrey', 0, 0, 0, '0:7940009')
    await p.send_tag('P_TILE', 4, '', 0, 0, 1, '0:5', 'blankpurpl', 0, 0, 0, '0:7940010')
    await p.send_tag('P_TILE', 5, '', 0, 0, 1, '0:6', 'blankwhite', 0, 0, 0, '0:7940011')

    await p.send_tag('P_PHYSICS', 0, 0, 0, 0, 0, 0, 0, 1)
    await p.send_tag('P_ASSETSCOMPLETE', p.id)


async def snow_world_ready(p):
    await p.send_tag('W_INPUT', 'use', '4375706:1', 2, 3, 0, 'use')
    # input id | script id | mouse target | key mouse type | key modifier | command	
    await p.send_tag('W_PLACE', '0:10001', 8, 1)
    # tile	

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
    # P_TILE: url | blocking | blend | name | mod e| friction | bounce | group | loadnow	
    for tile in p.server.tiles:
        await p.send_tag('P_TILE', tile.TileUrl.value, '', 0, 0, 1, tile.SpriteIndex.value, tile.TileName.value, 0, 0,
                         0, tile.TileCollection.value)
    await p.send_tag('P_PHYSICS', 0, 0, 0, 0, 0, 0, 0, 1)
    await p.send_tag('P_ASSETSCOMPLETE', 0, 0)
    for sprite in p.server.default_sprites:
        await p.send_tag('S_LOADSPRITE', f'0:{sprite}')
    await p.send_tag('UI_CROSSWORLDSWFREF', 102, 0, 'WindowManagerSwf', 0, 0, 0, 0, 0,
                     p.media_url + URLConstants.WindowManager.value,
                     '#')
    await p.send_tag('UI_ALIGN', 102, 0, 0, 'center', 'scale_none')

    p.snow_ninja.ready_object['ready'] = True

@handlers.handler(FrameworkPacket('payloadBILogAction'))
async def handle_payload_action(p, action, **data):
    # TODO: handle tipmode and muted soundss
    if action == 'funnel_prepare_to_battle_4':
        await asyncio.sleep(5)  # Prepare to battle animation
        await p.send_json(type='playAction', action='closeWindow',
                          targetWindow=p.media_url + URLConstants.PlayerSelection.value)

        worldname = 'cjsnow_battle1' if 'game_type' == 'normal' else 'cjsnow_tusk'

        await p.send_tag('S_GOTO', 'cjsnow_coastalfreeze', 'snow_lobby', '',
                         f'battleMode=0&tipMode={p.snow_ninja.tip_mode}&isMuted=false&base_asset_url={p.media_url}')


async def world_place_ready(p):
    await p.send_tag('O_HERE', 12, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)
    await p.send_tag('O_HERE', 4, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)

    # idk about these
    await p.send_tag('O_HERE', 9, '0:1', 10.7667, 5.92222, 0, 1, 0, 0, 0, 'Actor5', '0:30021', 0, 0, 0)
    await p.send_tag('O_HERE', 10, '0:1', 4.48869, -1.11106, 0, 1, 0, 0, 0, 'Actor6', '0:10002', 0, 0, 0)
    await p.send_tag('O_HERE', 11, '0:1', 4.5, 6.1, 0, 1, 0, 0, 0, 'Actor7', '0:6740002', 0, 0, 0)
    await p.send_tag('O_PLAYER', 12, '')  # prob change it ot the number


async def login_place_ready(p):
    await p.send_tag('O_HERE', 4, '0:1', 5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)
    await p.send_tag('O_PLAYER', 4, '')


@handlers.handler(TagPacket('/place_ready'))
async def handle_screen_ready(p):
    if p.server.snow_world:
        await world_place_ready(p)
    else:
        await login_place_ready(p)
    await p.send_tag('P_CAMERA', 4.48438, 2.48438, 0, 0, 1)
    await p.send_tag('P_ZOOM', '1.000000')
    await p.send_tag('P_LOCKZOOM', 1)
    await p.send_tag('P_LOCKCAMERA', 1)

    p.snow_ninja.ready_object['place_ready'] = True


@handlers.handler(FrameworkPacket('quit'))
async def handle_quit(p, **data):
    await p.send_json(action='loadWindow', assetPath='', initializationPayload=[None], layerName='toolLayer', \
                      loadDescription='', type='playAction',
                      windowUrl=p.media_url + URLConstants.ExternalInterface.value, \
                      xPercent=0, yPercent=0)
    if p.server.snow_world:
        p.snow_ninja.damage = p.snow_ninja.ninja.HealthPoints
        await p.room.player_manager.player_death(p)

