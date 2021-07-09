from snow.constants import URLConstants
from snow.data.ninja import PenguinCardCollection
from snow.events import TagPacket, event
import ujson
from loguru import logger

from snow.data.penguin import Penguin


@event.on(TagPacket('/login'))
async def snow_login(p, environment, p_id: int, token: str):
    token = token.strip()
    server_token = ujson.loads(await p.server.redis.get(token))

    peng_id = int(server_token['player_id'])

    if server_token is None or peng_id != p_id:
        logger.error(f'{p_id} failed to login L')
        await p.send_tag('S_LOGINDEBUG', 'user code 1000')
        await p.send_tag("S_ERROR", 900, "Error", -1, "No")
        return

    data = await Penguin.query.where(Penguin.id == p_id).gino.first()
    if data is not None:
        logger.info(f'{data.username} Is Logging IN!')
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
