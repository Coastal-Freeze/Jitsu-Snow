import json
from datetime import datetime

from houdini import handlers
from houdini.constants import ClientType
from houdini.converters import Credentials, WorldCredentials
from houdini.crypto import Crypto
from houdini.data.moderator import Ban
from houdini.data.ninja import PenguinCardCollection
from houdini.data.penguin import Penguin
from houdini.handlers import XMLPacket, login, TagPacket

handle_version_check = login.handle_version_check
handle_random_key = login.handle_random_key
handle_snow_version_check = login.handle_snow_version_check
handle_server_context = login.handle_server_context


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
async def snow_login(p, environment, p_id: int, token: str):
    token = token.strip()
    server_token = json.loads((await p.server.redis.get(token)))
    p.logger.info(server_token)

    peng_id = int(server_token['player_id'])

    if server_token is None or peng_id != p_id:
        p.logger.info(f'{p_id} failed to login L')
        return await p.send_tag('S_LOGINDEBUG', 'user code 1000')

    if p.server_world:
        p.world_name = server_token['match_session']
        await p.server.redis.delete(token)

    p.login_key = token

    data = await Penguin.query.where(Penguin.id == p_id).gino.first()
    if data is not None:
        p.logger.info(f'{data.username} Is Logging IN!')
        p.update(**data.to_dict())

        p.snow_ninja.muted = server_token['is_muted']

        p.is_member = True

        p.cards = await PenguinCardCollection.get_collection(p.id)
        await p.send_tag('S_LOGINDEBUG', 'Finalizing login')
        await p.send_tag('S_LOGIN', p_id, '')
        await p.send_tag('S_WORLDTYPE', 0, 1, 0)
        await p.send_tag('S_WORLD', 1, 'cjsnow_0', '0:0', 0, 'none', 0, p_id, 'cjsnow_0', 0, 87.5309, 0)
        await p.send_tag('W_DISPLAYSTATE')
        await p.send_tag('W_ASSETSCOMPLETE', p_id, '')
        p.joined_world = True
