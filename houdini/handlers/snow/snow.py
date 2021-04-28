from houdini import handlers
from houdini.constants import URLConstants
from houdini.handlers import FrameworkPacket, TagPacket


@handlers.handler(TagPacket('/ready'))
async def handle_penguin_ready(p):
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


@handlers.handler(FrameworkPacket('quit'))
async def handle_quit(p, **data):
    await p.send_json(action='loadWindow', assetPath='', initializationPayload=[None], layerName='toolLayer', \
                      loadDescription='', type='playAction',
                      windowUrl=p.media_url + URLConstants.ExternalInterface.value, \
                      xPercent=0, yPercent=0)
    await p.room.player_manager.player_death(p)
