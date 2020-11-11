from datetime import datetime

from houdini import handlers
from houdini.constants import ClientType, URLConstants, WaterNinja, SnowNinja, FireNinja
from houdini.converters import Credentials, WorldCredentials
from houdini.crypto import Crypto
from houdini.data.moderator import Ban
from houdini.data.ninja import PenguinCardCollection
from houdini.data.penguin import Penguin
from houdini.handlers import XMLPacket, login, FrameworkPacket, TagPacket

handle_version_check = login.handle_version_check
handle_random_key = login.handle_random_key


async def world_login(p, data):
    if len(p.server.penguins_by_id) >= p.server.config.capacity:
        return await p.send_error_and_disconnect(103)

    if p.server.config.staff and not data.moderator:
        return await p.send_error_and_disconnect(103)

    if data is None:
        return await p.send_error_and_disconnect(100)

    if data.permaban:
        return await p.close()

    active_ban = await Ban.query.where((Ban.penguin_id == data.id) & (Ban.expires >= datetime.now())).gino.scalar()
    if active_ban is not None:
        return await p.close()

    if data.id in p.server.penguins_by_id:
        await p.server.penguins_by_id[data.id].close()

    p.logger.info(f'{data.username} logged in successfully')
    p.update(**data.to_dict())
    await p.send_xt('l')


@handlers.handler(XMLPacket('login'), client=ClientType.Vanilla)
@handlers.allow_once
@handlers.depends_on_packet(XMLPacket('verChk'), XMLPacket('rndK'))
async def handle_login(p, credentials: WorldCredentials):
    tr = p.server.redis.multi_exec()
    tr.get(f'{credentials.username}.lkey')
    tr.get(f'{credentials.username}.ckey')
    tr.delete(f'{credentials.username}.lkey', f'{credentials.username}.ckey')
    login_key, confirmation_hash, _ = await tr.execute()

    if login_key is None or confirmation_hash is None:
        return await p.close()

    login_key = login_key.decode()
    login_hash = Crypto.encrypt_password(login_key + p.server.config.auth_key) + login_key

    if credentials.client_key != login_hash:
        return await p.close()

    if login_key != credentials.login_key or confirmation_hash.decode() != credentials.confirmation_hash:
        return await p.close()

    data = await Penguin.get(credentials.id)

    p.login_key = login_key
    await world_login(p, data)


@handlers.handler(XMLPacket('login'), client=ClientType.Legacy)
@handlers.allow_once
@handlers.depends_on_packet(XMLPacket('verChk'), XMLPacket('rndK'))
async def handle_legacy_login(p, credentials: Credentials):
    tr = p.server.redis.multi_exec()
    tr.get(f'{credentials.username}.lkey')
    tr.delete(f'{credentials.username}.lkey', f'{credentials.username}.ckey')
    login_key, _ = await tr.execute()

    try:
        login_key = login_key.decode()
    except AttributeError:
        return await p.close()

    login_hash = Crypto.encrypt_password(login_key + p.server.config.auth_key) + login_key

    if login_key is None or login_hash != credentials.password:
        return await p.close()

    data = await Penguin.query.where(Penguin.username == credentials.username).gino.first()

    p.login_key = login_key
    await world_login(p, data)


@handlers.handler(TagPacket('/login'), pre_login=True)
@handlers.allow_once
@handlers.depends_on_packet(TagPacket('/version'), TagPacket('/place_context'))
async def handle_penguin_login(p, world: str, p_id: int, p_token: str):
    data = await Penguin.query.where(Penguin.id == p_id).gino.first()
    p.logger.info('cock and ball tortureinator')
    if data is not None:
        p.update(**data.to_dict())
        p.cards = await PenguinCardCollection.get_collection(p.id)

        tr = p.server.redis.multi_exec()
        tr.get(f'cjsnow.{p.id}')
        tr.get(f'cjsnow.{p.id}.element')
        tr.delete(f'cjsnow.{p.id}', f'cjsnow.{p.id}.element')
        match_id, element, _ = await tr.execute()

        if match_id is None or element is None:
            return await p.close()

        match_id, element = int(match_id), int(element)

        p.ninja = FireNinja
        if element == 2:
            p.ninja = WaterNinja
        elif element == 4:
            p.ninja = SnowNinja

        if match_id not in p.server.battles:
            p.server.battles[match_id] = SnowBattle(p.server)
        p.room = await p.server.battles[match_id].add_penguin(p)
        p.server.logger.info(f'{data.nickname}, {p.room}')
        await p.send_tag('S_LOGIN', p_id)  # Edit: [S_LOGIN]|swid|
        await p.send_tag('S_WORLDTYPE', 0, 1, 0)
        await p.send_tag('S_WORLD', 2, 'cjsnow_{{game}}', '0:0', 0, 'none', 0, 1, 'cjsnow_{{game}}', 0, 87.5309, 0)
        await p.send_tag('W_BASEASSETURL')
        await p.send_tag('W_DISPLAYSTATE')
        await p.send_tag('W_ASSETSCOMPLETE', p_id)
        p.joined_world = True


@handlers.handler(FrameworkPacket('roomToRoomComplete'))
async def handle_joined_room(p, **kwargs):
    for sprite in p.server.default_sprites:
        await p.send_tag('S_LOADSPRITE', f'0:{sprite}')
    await p.send_json(action='loadWindow', assetPath='', initializationPayload=[None], layerName='bottomLayer', \
                      loadDescription='', type='playAction', windowUrl=p.media_url + URLConstants.CloseWindow.value, \
                      xPercent=1, yPercent=0)
    await p.send_tag('O_HERE', 13, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)


@handlers.handler(TagPacket('/ready'))
async def handle_penguin_ready(p):
    # [W_INPUT]|use|4375706:1|2|3|0|use|
    await p.send_tag('W_INPUT', 'use', '4375706:1', 2, 3, 0, 'use')
    # input id | script id | mouse target | key mouse type | key modifier | command

    await p.send_tag('W_PLACE', '0:10001', 8, 1)
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
    await p.send_tag('UI_BGCOLOR', 0, 0, 0)
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
                     '#receivedFromFramework')
    await p.send_tag('UI_ALIGN', 102, 0, 0, 'center', 'scale_none')

    p.ready = True


@handlers.handler(TagPacket('/place_ready'))
async def handle_screen_ready(p):
    # these are the player objects
    await p.send_tag('O_HERE', 12, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)
    await p.send_tag('O_HERE', 4, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)

    # idk about these
    await p.send_tag('O_HERE', 9, '0:1', 10.7667, 5.92222, 0, 1, 0, 0, 0, 'Actor5', '0:30021', 0, 0, 0)
    await p.send_tag('O_HERE', 10, '0:1', 4.48869, -1.11106, 0, 1, 0, 0, 0, 'Actor6', '0:10002', 0, 0, 0)
    await p.send_tag('O_HERE', 11, '0:1', 4.5, 6.1, 0, 1, 0, 0, 0, 'Actor7', '0:6740002', 0, 0, 0)
    await p.send_tag('O_PLAYER', 12, '')  # prob change it ot the number

    p.place_ready = True
