import asyncio
import os
from datetime import datetime, timedelta

import bcrypt
import json

from sqlalchemy import func

from houdini import handlers
from houdini.constants import ClientType, URLConstants, FireNinja, WaterNinja, SnowNinja
from houdini.converters import Credentials
from houdini.crypto import Crypto
from houdini.data.moderator import Ban
from houdini.data.ninja import PenguinCardCollection
from houdini.data.penguin import Penguin
from houdini.handlers import XMLPacket, TagPacket, FrameworkPacket
from houdini.handlers.login import get_server_presence
from houdini.handlers.play.navigation import get_minutes_played_today


@handlers.handler(XMLPacket('login'))
@handlers.allow_once
@handlers.depends_on_packet(XMLPacket('verChk'), XMLPacket('rndK'))
async def handle_login(p, credentials: Credentials):
    loop = asyncio.get_event_loop()

    username, password = credentials.username, credentials.password
    p.logger.info(f'{username} is logging in!')

    data = await Penguin.query.where(func.lower(Penguin.username) == username).gino.first()

    if data is None:
        p.logger.info(f'{username} failed to login: penguin does not exist')
        return await p.send_error_and_disconnect(100)

    password_correct = await loop.run_in_executor(None, bcrypt.checkpw,
                                                  password.encode('utf-8'), data.password.encode('utf-8'))

    ip_addr = p.peer_name[0]
    flood_key = f'{ip_addr}.flood'

    if not password_correct:
        p.logger.info(f'{username} failed to login: incorrect password')

        if await p.server.redis.exists(flood_key):
            tr = p.server.redis.multi_exec()
            tr.incr(flood_key)
            tr.expire(flood_key, p.server.config.login_failure_timer)
            failure_count, _ = await tr.execute()

            if failure_count >= p.server.config.login_failure_limit:
                return await p.send_error_and_disconnect(150)
        else:
            await p.server.redis.setex(flood_key, p.server.config.login_failure_timer, 1)

        return await p.send_error_and_disconnect(101)

    failure_count = await p.server.redis.get(flood_key)
    if failure_count:
        max_attempts_exceeded = int(failure_count) >= p.server.config.login_failure_limit

        if max_attempts_exceeded:
            return await p.send_error_and_disconnect(150)
        else:
            await p.server.redis.delete(flood_key)

    preactivation_hours = 0
    if not data.active:
        preactivation_expiry = data.registration_date + timedelta(days=p.server.config.preactivation_days)
        preactivation_expiry = preactivation_expiry - datetime.now()
        preactivation_hours = preactivation_expiry.total_seconds() // 3600
        if preactivation_hours <= 0 or p.client_type == ClientType.Legacy:
            return await p.send_error_and_disconnect(900)

    if data.permaban:
        return await p.send_error_and_disconnect(603)

    if data.grounded:
        return await p.send_error_and_disconnect(913)

    if data.timer_active:
        if not data.timer_start < datetime.now().time() < data.timer_end:
            return await p.send_error_and_disconnect(911, data.timer_start, data.timer_end)

        minutes_played_today = await get_minutes_played_today(p)
        if minutes_played_today >= data.timer_total.total_seconds() // 60:
            return await p.send_error_and_disconnect(910, data.timer_total)

    active_ban = await Ban.query.where((Ban.penguin_id == data.id) & (Ban.expires >= datetime.now())).gino.first()

    if active_ban is not None:
        hours_left = round((active_ban.expires - datetime.now()).total_seconds() / 60 / 60)

        if hours_left == 0:
            return await p.send_error_and_disconnect(602)
        else:
            return await p.send_error_and_disconnect(601, hours_left)

    p.logger.info(f'{username} has logged in successfully')

    random_key = Crypto.generate_random_key()
    login_key = Crypto.hash(random_key[::-1])
    confirmation_hash = Crypto.hash(os.urandom(24))

    tr = p.server.redis.multi_exec()
    tr.setex(f'{data.username}.lkey', p.server.config.auth_ttl, login_key)
    tr.setex(f'{data.username}.ckey', p.server.config.auth_ttl, confirmation_hash)
    await tr.execute()

    world_populations, buddy_presence = await get_server_presence(p, data)

    if p.client_type == ClientType.Vanilla:
        raw_login_data = f'{data.id}|{data.id}|{data.username}|{login_key}|houdini|{data.approval}|{data.rejection}'
        if not data.active:
            await p.send_xt('l', raw_login_data, confirmation_hash, '', world_populations, buddy_presence,
                            data.email, int(preactivation_hours))
        else:
            await p.send_xt('l', raw_login_data, confirmation_hash, '', world_populations, buddy_presence, data.email)
    else:
        await p.send_xt('l', data.id, login_key, buddy_presence, world_populations)


@handlers.handler(TagPacket('/login'), pre_login=True)
@handlers.allow_once
@handlers.depends_on_packet(TagPacket('/version'), TagPacket('/place_context'))
async def snow_login(p, environment, p_id: int, token: str):
    token = token.strip()
    server_token = json.loads(await p.server.redis.get(token))

    peng_id = int(server_token['player_id'])

    if server_token is None or peng_id != p_id:
        p.logger.info(f'{p_id} failed to login L')
        return await p.send_tag('S_LOGINDEBUG', 'user code 1000')

    p.login_key = token

    data = await Penguin.query.where(Penguin.id == p_id).gino.first()
    if data is not None:
        p.logger.info(f'{data.username} Is Logging IN!')
        p.update(**data.to_dict())

        p.snow_ninja.muted = server_token['is_muted']

        p.cards = await PenguinCardCollection.get_collection(p.id)
        await p.send_tag('S_LOGINDEBUG', 'Finalizing login')
        await p.send_tag('S_LOGIN', p_id)
        await p.send_tag('S_WORLDTYPE', 0, 1, 0)
        await p.send_tag('S_WORLD', 1, 'cjsnow_0', '0:0', 0, 'none', 0, p_id, 'cjsnow_0', 0, 87.5309, 0)
        await p.send_tag('W_DISPLAYSTATE')
        await p.send_tag('W_ASSETSCOMPLETE', p_id)
        p.joined_world = True

        p.is_member = True


@handlers.handler(TagPacket('/place_ready'))
async def handle_screen_ready(p):
    await p.send_tag('O_HERE', 4, '0:1', 5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)
    await p.send_tag('O_PLAYER', 4, '')
    await p.send_tag('P_CAMERA', 4.48438, 2.48438, 0, 0, 1)
    await p.send_tag('P_ZOOM', '1.000000')
    await p.send_tag('P_LOCKZOOM', 1)
    await p.send_tag('P_LOCKCAMERA', 1)
    p.snow_ninja.ready_object['place_ready'] = True


@handlers.handler(FrameworkPacket('payloadBILogAction'))
async def handle_payload_action(p, action, **data):
    # TODO: handle tipmode and muted soundss
    if action == 'funnel_prepare_to_battle_4':
        await asyncio.sleep(5)  # Prepare to battle animation
        await p.send_json(type='playAction', action='closeWindow',
                          targetWindow=p.media_url + URLConstants.PlayerSelection.value)

        worldname = 'cjsnow_battle1' if 'game_type' == 'normal' else 'cjsnow_tusk'

        await p.send_tag('S_GOTO', 'cjsnow_battle', 'snow_lobby', '',
                         f'battleMode=0&tipMode={p.snow_ninja.tip_mode}&isMuted=false&base_asset_url={p.media_url}')


@handlers.handler(TagPacket('/ready'))
async def handle_penguin_ready(p):
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


@handlers.handler(FrameworkPacket('quit'))
async def handle_quit(p, **data):
    await p.send_json(action='loadWindow', assetPath='', initializationPayload=[None], layerName='toolLayer', \
                      loadDescription='', type='playAction',
                      windowUrl=p.media_url + URLConstants.ExternalInterface.value, \
                      xPercent=0, yPercent=0)


@handlers.handler(FrameworkPacket('windowManagerReady'))
async def handle_window_manager_ready(p, **data):
    fire_cnt, water_cnt, snow_cnt = 0, 0, 0
    for card in p.cards.values():
        card_info = p.server.cards[card.card_id]
        if card_info.power_id > 0:
            if card_info.element == 'f':
                fire_cnt += card.quantity
            if card_info.element == 'w':
                water_cnt += card.quantity
            if card_info.element == 's':
                snow_cnt += card.quantity

    await p.send_json(type='immediateAction', action='setWorldId', worldId=1)
    await p.send_json(type='immediateAction', action='setBaseAssetUrl',
                      baseAssetUrl=p.media_url + URLConstants.BaseAssets.value)
    await p.send_json(type='immediateAction', action='setFontPath',
                      defaultFontPath=p.media_url + URLConstants.BaseFonts.value)
    await p.send_json(type='playAction', action='skinRoomToRoom', url=p.media_url + URLConstants.LoadingScreen.value,
                      className='', variant=0)
    await p.send_json(action='loadWindow', assetPath='', initializationPayload=[None], layerName='bottomLayer', \
                      loadDescription='', type='playAction', windowUrl=p.media_url + URLConstants.ErrorHandler.value, \
                      xPercent=0, yPercent=0)
    await p.send_json(action='loadWindow', assetPath='', initializationPayload={'game': 'snow', 'name': p.safe_name, \
                                                                                'powerCardsFire': fire_cnt,
                                                                                'powerCardsWater': water_cnt,
                                                                                'powerCardsSnow': snow_cnt},
                      layerName='topLayer', \
                      loadDescription='', type='playAction', windowUrl=p.media_url + URLConstants.PlayerSelection.value, \
                      xPercent=0, yPercent=0)


@handlers.handler(FrameworkPacket('mmElementSelected'))
async def handle_select_element(p, tipMode=False, element=None, **data):
    p.snow_ninja.tip_mode = tipMode
    p.snow_ninja.tile = FireNinja

    if element == 'water':
        p.snow_ninja.tile = WaterNinja
    elif element == 'snow':
        p.snow_ninja.tile = SnowNinja

    p.server.snow_match_making.add_penguin(p)


@handlers.handler(FrameworkPacket('mmCancel'))
async def handle_cancel_matchmaking(p, **data):
    p.server.snow_match_making.remove_penguin(p)
